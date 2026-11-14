# Autonomy Preflight — Preparing a Run That Proceeds Unattended

A plan check proves the plan is sound. It does not prove the run can reach the
gate without a person. An expired token, a sign-in prompt, a test account two
agents share, a red baseline, an escalation nobody receives, or a question
nobody answered before the night stops the run as surely as a cycle in the
plan. Preflight moves every dependency on a person to before the window opens
or to the merge boundary.

Run it after the plan check passes and before the first spawn, whenever the
run is meant to proceed while nobody watches: overnight, over a weekend, or
across more than one wave. A run the human attends end to end may skip it and
says so under What I did not check.

**Preflight reads evidence; it never runs a probe.** The lead executes each
probe at the plan's base, records command, exit code, and commit, and the
checker decides from those records, the plan, and the profile.

## 1. Checklist

Each line is a fact the preflight record states and the code that refuses it
when it is missing.

| # | Area | Must hold before the window opens | Code |
|:--|:--|:--|:--|
| 1 | Work | Every plan requirement sits in an increment that is `READY`, or `PARTLY-READY` and reversible, per `implementation-readiness` | `WORK_NOT_READY` |
| 2 | Decisions | Every question an agent would stop to ask is answered, given a reversible default, or made a stop rule, by the human | `OPEN_DECISION` |
| 3 | Access | Repository, pipeline, registries, cloud, and every external system the packages touch answer a non-interactive probe at the base, with the identity and the operation each package uses | `PREREQUISITE_UNPROVEN` |
| 4 | No prompts | No step inside the window waits on a sign-in, second factor, consent screen, human check, license prompt, permission dialog, or a pipeline step that asks a human | `INTERACTIVE_STEP` |
| 5 | Expiry | No token, refresh token, session, certificate, or temporary role expires before the window ends, including sign-in frequency limits that end a session early | `CREDENTIAL_EXPIRES` |
| 6 | Test accounts | One account per role the acceptance criteria exercise, per concurrently running package, that obtains a token without interaction and has a reset command; only read-only accounts are shared | `ACCOUNT_CONFLICT`, `PREREQUISITE_UNPROVEN` |
| 7 | Environment | Each probe below passed at the base | `PREREQUISITE_UNPROVEN` |
| 8 | Baseline | Every profile verification command passed at the base, so a later red result belongs to the run; flaky checks are quarantined first per `test-strategy` | `BASELINE_RED` |
| 9 | Bounds | A window, a spend limit, stop conditions, and an escalation channel proved by a deliberate test escalation that arrived | `UNBOUNDED_RUN`, `PREREQUISITE_UNPROVEN` |
| 10 | Human steps | Approvals happen before the window; merge, deploy, and accepted risk are batched at its end | `HUMAN_STEP_MIDRUN` |
| 11 | Secrets | The record names secrets; it never holds a value | `SECRET_IN_RECORD` |

Environment probes, line 7:

- Every tool an acceptance command calls is present at the version it needs,
  and runs inside every permission envelope that must run it; a read-only
  reviewer that cannot execute a command cannot verify.
- The build is one command with its dependencies available; seed data loads
  and resets per package.
- The delivery path has run once before the window: pipeline definitions
  exist where the trigger looks for them, an infrastructure preview or dry
  run succeeds in the target region at the target capacity, and a re-run of a
  failed step succeeds.
- The pipeline calls the same entrypoints the local checks call, so a script
  that passes locally does not fail in the pipeline on path or module
  resolution.
- Every probe and oracle the run relies on was itself run once against the
  real dependency; an untested probe produces a false `NO-GO` mid-run.
- The host stays up for the window: no sleep, the runtime open, and the locale
  and encoding the scripts assume set.

Judgment the checker cannot make, reviewed by the lead and reported:

- **The riskiest assumption goes first.** Order the increments per
  `implementation-readiness`, so the one most likely to be wrong fails early
  in the window instead of at its end; the checker reads readiness, not order.
- **The decision list is complete.** Read each package's acceptance criteria
  and open technical questions, and ask which answer would change the code.
  Include the bound questions: whether the lead may raise a retry or rework
  bound, by how much, and once. Two run rules that contradict each other are
  an open decision. An unlisted question is an interruption the record cannot
  catch.
- **Every file the criteria touch has an owner.** Shared registries, counts
  pinned by architecture tests, and sequence-numbered migrations are written
  by more than one package unless the plan serializes them; a criterion that
  contradicts the increment's goal is a plan defect, not a finding.
- **Probes probe the right thing.** A repository read does not prove a deploy
  permission, and a sign-in does not prove a role.
- **Outcomes are distinguishable.** A check reports "could not evaluate"
  apart from "failed", per `gate-lifecycle`, so an incomplete measurement does
  not page anyone as a defect.
- **Waiting is not working.** Long external waits such as pipeline runs,
  deploys, and quota resets are scheduled into the waves, and packages are
  sized to finish within one context; a run that sleeps through waits is
  bounded by the window, not by progress.

## 2. Record — `alchemy-preflight/1`

Kept with the plan under `state_dir`. Excerpt:

```json
{
  "schema": "alchemy-preflight/1",
  "window": {"start": "2026-11-13T18:00:00Z", "end": "2026-11-14T08:00:00Z"},
  "bounds": {
    "budget": "400 agent-minutes, USD 60",
    "stop_conditions": ["gate PASS", "a bound escalates", "window end"],
    "escalation": {"channel": "push notification; blocked packages park, the rest continue",
                   "evidence": ["E7"]}
  },
  "work": [{"subject": "I1", "decision": "READY", "requirements": ["REQ-12"], "record": "issue#12"}],
  "decisions": [{"id": "D2", "question": "Sort order when dates tie?", "status": "default",
                 "decided_by": "human", "reversible": true, "answer": "by id ascending"}],
  "access": [{"id": "A1", "system": "repository and pipeline", "secret": "REPO_TOKEN",
              "expires": "2026-12-31T00:00:00Z", "interactive": false, "evidence": ["E1"]}],
  "accounts": [{"id": "U1", "role": "order clerk", "secret": "TEST_CLERK_A_PASSWORD",
                "packages": ["P1"], "reset": "npm run seed -- --user clerk-a",
                "expires": "never", "evidence": ["E3"]}],
  "environment": [{"id": "ENV1", "what": "one-command build", "evidence": ["E5"]}],
  "human_steps": [{"action": "approve the plan", "when": "before"},
                  {"action": "merge the pull request", "when": "end"}],
  "evidence": [{"id": "E1", "command": "git ls-remote origin HEAD", "exit_code": 0, "commit": "3f9c2e1"}]
}
```

| Field | Rule |
|:--|:--|
| `window` | `start` and `end`, ISO 8601 instants with a zone; `end` after `start` |
| `bounds` | `budget`, at least one `stop_conditions` entry, and `escalation` with a `channel` and the `evidence` of a test delivery |
| `work[]` | `subject`, `decision` from `implementation-readiness`, `requirements`, `record`; `PARTLY-READY` counts only with `reversible: true`. Together they cover every plan requirement |
| `decisions[].status` | `answered`, `default` (needs `reversible: true`), or `stop`, each with `decided_by: human`; `answered` and `default` state the `answer`; `open` escalates. Defaults are reported as `queued` for the human to confirm at the merge boundary |
| `access[]`, `accounts[]` | `id`, `evidence`, `expires` (`never` or an instant after the window end), optional `interactive`; accounts add `role`, `secret` (a name), `packages`, `reset`, and `shared: true` only for read-only use |
| `environment[]` | `id`, `evidence`, optional `interactive` |
| `human_steps[].when` | `before`, `end`, or `during`; `during` fails |
| `evidence[]` | As in the hand-off: `id`, `command`, `exit_code`, `commit`, optional `expect_exit`. A probe counts only when it passed at the plan base |

`check_orchestration.py preflight <preflight.json> --plan <plan.json>
--profile alchemy-workspace.json --root .` returns `PASS`, `FAIL`, or
`ESCALATE` with the codes in [contracts.md](contracts.md). `PASS` with a
non-empty `queued` list means the run proceeds on reversible defaults the
human confirms at the merge boundary.

## 3. During the Run

Preflight removes the known interruptions; the run handles the rest without
stopping everything:

- A package that hits an unlisted question, an expired credential, or a
  failing probe returns `BLOCKED` with the cause. The lead parks it, reports
  it on the escalation channel, and continues every package that does not
  depend on it.
- The lead pushes progress on the same channel at each wave boundary, so the
  human never has to ask whether action is needed.
- Each new interruption is a missing checklist line or probe. Record it, and
  route a recurring one to `continuous-improvement` so the next preflight
  catches it.
