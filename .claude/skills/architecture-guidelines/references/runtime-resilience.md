# Runtime Resilience — Outbound Calls, Retries, and Error Mapping

Read when §5 sends you here: a change adds or alters a call from application
code to something it does not own in-process — a database, cache, queue,
object store, DNS, identity provider, model, or remote API — or decides what a
failed call shows its caller. Pipeline steps belong to
`ci-cd-reliability-architecture` §4; this file covers application code.

## 1. The call contract
Every outbound call declares a timeout and four more fields before it is built:

| Field | Question | When undeclared |
|:--|:--|:--|
| Timeout | How long may the caller wait? | A defect: the call inherits its dependency's hang |
| Retry class | Is each failure temporary or permanent (§2)? | Permanent |
| Retry budget | How many attempts, with what backoff and jitter, inside the caller's own deadline? | No retry |
| Idempotency precondition | What makes a second attempt safe? | No retry of a write |
| Caller-visible error | What does the caller see when the budget runs out? | 500 with the cause logged (§3) |

Timeouts shrink toward the dependency: an inner timeout longer than the outer
deadline retries work nobody is waiting for. A retry without an idempotency
precondition is a second write; the precondition is the record's write model
from `concurrency-control` (version check, fencing token, or idempotency key).
A read needs none.

## 2. Temporary or permanent
| Class | Examples | Action |
|:--|:--|:--|
| Temporary | Timeout; 408, 502, 504; connection refused or reset; DNS failure; 429 or 503, honouring `Retry-After`; throttling; a paused or serverless database waking up; a stream cut before its first byte | Retry within the budget, exponential backoff with jitter |
| Permanent | 400, 401, 403, 404, 422; validation and schema errors; a quota that resets on a calendar; a content-policy refusal | Fail fast; map per §3 |
| Conflict | 409, 412 | Not a retry: the record's write model decides (`concurrency-control`) |
| Unknown | Anything the client does not classify | Permanent for retry; 500 |

A database waking up is temporary: the budget covers its documented wake time,
or the design keeps it warm.

## 3. Map errors to what the caller can do
- A status is a promise about recovery: 503 says retry later, 409 says you lost
  a race, any other 4xx says change the request. Send one only when the code knows it is true.
- An unknown error is a 500 with its cause logged. Never a guessed 503, 409, or
  404: the wrong status sends the caller into the wrong recovery.
- Log the cause of every 5xx once, at the boundary that maps it, with the
  dependency, attempt count, and elapsed time; `observability-design` decides
  which of these become signals.
- Never pass a dependency's internal message to an untrusted caller.

## 4. Streams, workers, and jobs end with their real outcome
- A stream ends with an explicit terminal event: completed, failed with a
  cause, or cancelled. A stream that stops without one is failed, never a short success.
- A job records success only after its last write commits; an exception
  swallowed into "done" is a lost failure.
- A retried job resumes from a checkpoint its write model makes safe.
- A partial result is labelled partial.

## 5. Verification
Each field has an oracle: the timeout fires; a temporary failure retries
within the budget and then stops; a permanent failure does not retry; an
unknown error maps to 500 with its cause logged; a stream cut midway ends
failed. `test-strategy` selects deterministic fault injection at the
dependency boundary. `defect-shift-left` places the call-site check: an
outbound call without a timeout is a stage 5 lint, else a stage 7
fault-injection test.
