# Write Models — Mechanisms, Leases, Keys, and Tests

Read when `concurrency-control` §1 has chosen a model and the store's mechanism,
the lease and token handling, or the test recipe is needed.

## Version check
- HTTP: return the record's ETag; the client sends it back in `If-Match`; the
  server passes it to the store as the write condition and maps a failed
  condition to 412 (or 409 for a domain conflict). `If-None-Match: *` makes a
  create fail when the record exists.
- Document and object stores: conditional replace or put on the item's ETag.
- SQL: a version or rowversion column; `UPDATE … WHERE id = ? AND version = ?`,
  then require exactly one affected row.
- Key-value stores: compare-and-set on the stored revision.
- Send the version the user's edit was based on. Fetching a fresh version just
  before the write turns the check off.
- Reject a write that carries no precondition (`If-Match` for an update,
  `If-None-Match: *` for a create) with 428; never treat it as unconditional.

## Single writer
- A lease is a record with an owner and an expiry, taken by a conditional write
  (blob lease, lease row, lock service). Renew well before expiry.
- A fencing token rises with every lease. Every write by the holder carries
  it, and the store rejects a token lower than the highest it has seen. A
  holder that paused past its expiry wakes up still believing it holds the
  lease; the token, not the lease, stops its write.
- A job that loses its lease stops and writes nothing; the next holder resumes
  from a checkpoint its own write model makes safe.

## Idempotency key
- The caller chooses one key per logical operation and sends it on every retry.
- Store the key and the result under a unique constraint in the same
  transaction as the effect; a second arrival returns the stored result.
- Keep keys at least as long as the longest retry, replay, or redelivery window.
- The same key with a different payload is rejected, never silently merged.
- When the effect lives in another system, pass the key on to it. A duplicate
  that arrives while the first is still running waits for it or gets 409.

## Commutative merge
- Use the store's atomic operators: increment, patch, set-add, append.
- A bounded counter is not commutative: two decrements that each pass a
  stock or balance check can overdraw it. Use a conditional atomic operation
  (decrement only where the value is at least n) or a version check.
- Clients that edit offline need a merge type that converges (for example a
  CRDT); a timestamp comparison is last-writer-wins.

## Ordered start-up
- Nothing computes or saves until the state it reads has loaded: storage,
  profile, configuration, feature flags.
- A calculation that runs on defaults and then saves overwrites real data with
  defaults. Gate the first save on the load, not on a timer.

## Interleaving test recipes
Control the schedule with barriers or hooks, never sleeps, against the real
store or its emulator:
1. Two writers read version v; both write; exactly one succeeds and the other
   sees the conflict.
2. A holder pauses past expiry; a second takes the lease; the first one's write
   is rejected by the token.
3. The same request is sent twice; there is one effect and both calls get the same result.
4. A save fires before load completes; it is blocked, or it waits.

## Lint heuristic
Flag store writes (replace, upsert, update, put) that carry no condition
argument, version predicate, idempotency key, or token. The rule is per stack;
`defect-shift-left` places it at stage 5.
