# Autonomy Preflight — Preparing a Run That Proceeds Unattended

A plan check proves the plan is sound. It does not prove the run can reach the
gate without a person. An expired token, a sign-in prompt, a test account two
agents share, a red baseline, an escalation nobody receives, or a question
nobody answered before the night stops the run as surely as a cycle in the
plan. Preflight moves every dependency on a person to before the window opens
or to the merge boundary.

Run it after the plan check passes and before the first spawn, whenever the
run is meant to proceed while nobody watches: overnight, over a weekend, or
across more than one wave. Such a plan sets `execution.unattended: true`, and
its gate passes only with a preflight record that still passes against it
(`PREFLIGHT_REQUIRED`), so work done without one never reaches the merge
boundary. A run the human attends end to end may skip it and says so under
What I did not check. Who decides that a run is attended is set where
`execution.unattended` is defined ([contracts.md](contracts.md), Plan).

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
| 12 | Coverage | Every package states its needs, and every need a package or the profile declares is claimed by an entry of its kind (section 2) | `NEEDS_UNDECLARED`, `PREREQUISITE_UNCOVERED` |
| 13 | Binding | The record names the plan revision and base it was made for, and the plan has not changed since (section 3) | `PREFLIGHT_STALE` |

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
- **The needs list is complete.** For each package, read its write set,
  permissions, and acceptance commands, and ask what it must reach, act as,
  run on, and read that its needs do not name. The checker counts coverage
  against the declared needs, so a need nobody declared is a gap it cannot
  see (section 2).
- **Every changed need was proved again.** The checker holds a record to the
  plan revision and to one claiming entry per need, not to a new probe: an
  entry that names a need an amendment added in `covers`, citing a probe run
  before it, passes. For each need an amendment added or changed, confirm
  that its entry cites a probe run after the amendment that exercises it.
- **Probes probe the right thing.** A repository read does not prove a deploy
  permission, and a sign-in does not prove a role.
- **Outcomes are distinguishable.** A check reports "could not evaluate"
  apart from "failed", per `gate-lifecycle`, so an incomplete measurement does
  not page anyone as a defect.
- **Waiting is not working.** Long external waits such as pipeline runs,
  deploys, and quota resets are scheduled into the waves, and packages are
  sized to finish within one context; a run that sleeps through waits is
  bounded by the window, not by progress.

## 2. Needs and Coverage

Validating the entries a record submits proves those entries, not that the
run's prerequisites are all there: an emptied `environment` list has no entry
left to fail. Coverage needs a list of what the work requires, and the plan
is where a package states it. Each package of an unattended plan
carries `needs`, each `{"id", "kind", "what"}`:

| `kind` | What the package needs | Proved in |
|:--|:--|:--|
| `access` | A system it must reach: repository, pipeline, registry, cloud, an external service | `access[]` |
| `account` | An identity it acts as: a test account or role | `accounts[]`, naming the package |
| `environment` | The environment and tools it runs in, the tools its commands call included | `environment[]` |
| `fixture` | Inputs and fixtures it reads: seed data, recorded responses, test files | `fixtures[]` |

Packages that share a need repeat its `id` with the same kind. A preflight
entry claims needs with `covers`, a list of need IDs; one entry may cover
several. Every declared need, and every need the profile lists under
`preflight.needs`, must be claimed by an entry of its kind
(`PREREQUISITE_UNCOVERED`); an account claims a package's need only when its
`packages` names that package. Whether the claiming entry is proved stays
`PREREQUISITE_UNPROVEN`'s question.

A package that declares nothing has not said what it needs. `needs` absent is
`NEEDS_UNDECLARED`, so an omitted prerequisite cannot pass by omitting the
declaration too; `needs: []` is a claim a reviewer can test. Declaring fewer
needs than the work has is held back three ways:

- **A rule.** A package with a `command` acceptance criterion declares an
  `environment` need for the tools that command calls (`NEEDS_UNDECLARED`).
- **The profile.** `preflight.needs` in the project overlay lists what every
  unattended run in the project needs. The library names kinds; the overlay
  names the systems and their probes, and no plan can drop them.
- **A reviewer question.** "The needs list is complete" (section 1) is
  judgment.

The checker cannot see a need that no package, rule, or profile entry names,
nor a `what` that describes the wrong system; the lead reads those against
the work and reports them.

## 3. Binding and Revalidation

A preflight is worth something only for the plan revision it was checked
against. Its `plan` field names that revision: `digest`, the SHA-256 of the
plan's canonical JSON (keys sorted, no whitespace, `base.integrated` left out
because the lead appends wave heads to it), which the plan and preflight
checks print as `plan_digest`; and `base`, the plan's base commit, at which
every probe ran. A record whose digest or base is not the checked plan's is
stale (`PREFLIGHT_STALE`), and so is every probe on another commit
(`PREREQUISITE_UNPROVEN`, `BASELINE_RED`).

When a plan amendment or a later iteration changes the plan, the old record
no longer passes, and the gate refuses the run until a new one does. The lead
writes a new record bound to the new revision:

- **Prove again** every need that is new or whose kind, `what`, or packages
  changed, every entry whose system or identity changed, and everything when
  the base moved: a later iteration starts from a new base, so every probe
  and the baseline run there.
- **Carry over**, on the same base, every other entry with its evidence
  unchanged: its probe still ran at the base the plan names, so a small
  amendment re-runs only the probes of what it changed.
- **Re-check the window.** A changed window re-tests every expiry against it.

The checker enforces the binding and a claim for each need: the new need
stays uncovered until an entry claims it. It cannot tell a probe run again
from one carried over, since both ran at the same base, so whether each
changed need was proved again is the reviewer's question (section 1).
Amendments are part of the revision the digest covers ([contracts.md](contracts.md),
Amendments).

## 4. Record — `alchemy-preflight/1`

Kept with the plan under `state_dir`. Excerpt:

```json
{
  "schema": "alchemy-preflight/1",
  "plan": {"digest": "<plan_digest from the plan check>", "base": "3f9c2e1"},
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
              "expires": "2026-12-31T00:00:00Z", "interactive": false,
              "covers": ["N-REPO"], "evidence": ["E1"]}],
  "accounts": [{"id": "U1", "role": "order clerk", "secret": "TEST_CLERK_A_PASSWORD",
                "packages": ["P1"], "reset": "npm run seed -- --user clerk-a",
                "expires": "never", "covers": ["N-CLERK-A"], "evidence": ["E3"]}],
  "environment": [{"id": "ENV1", "what": "one-command build", "covers": ["N-BUILD"],
                   "evidence": ["E5"]}],
  "fixtures": [{"id": "F1", "what": "orders seed data", "covers": ["N-ORDERS-SEED"],
                "evidence": ["E8"]}],
  "human_steps": [{"action": "approve the plan", "when": "before"},
                  {"action": "merge the pull request", "when": "end"}],
  "evidence": [{"id": "E1", "command": "git ls-remote origin HEAD", "exit_code": 0, "commit": "3f9c2e1"}]
}
```

| Field | Rule |
|:--|:--|
| `plan` | `digest`, 64 hex characters, and `base`, a commit: the revision the record was made for (section 3) |
| `window` | `start` and `end`, ISO 8601 instants with a zone; `end` after `start` |
| `bounds` | `budget`, at least one `stop_conditions` entry, and `escalation` with a `channel` and the `evidence` of a test delivery |
| `work[]` | `subject`, `decision` from `implementation-readiness`, `requirements`, `record`; `PARTLY-READY` counts only with `reversible: true`. Together they cover every plan requirement |
| `decisions[].status` | `answered`, `default` (needs `reversible: true`), or `stop`, each with `decided_by: human`; `answered` and `default` state the `answer`; `open` escalates. Defaults are reported as `queued` for the human to confirm at the merge boundary |
| `access[]`, `accounts[]` | `id`, `evidence`, `expires` (`never` or an instant after the window end), optional `interactive`; accounts add `role`, `secret` (a name), `packages`, `reset`, and `shared: true` only for read-only use |
| `environment[]`, `fixtures[]` | `id`, `evidence`, optional `interactive`; `fixtures` may be absent when no need is a fixture |
| `covers` | On an access, account, environment, or fixture entry: the IDs of the needs it proves; an ID that no package and no profile need declares is `SCHEMA` |
| `human_steps[].when` | `before`, `end`, or `during`; `during` fails |
| `evidence[]` | As in the hand-off: `id`, `command`, `exit_code`, `commit`, optional `expect_exit`. A probe counts only when it passed at the plan base |

A record or plan written before `plan`, `needs`, and `covers` existed fails
after the upgrade:

| Fails with | Because | Add |
|:--|:--|:--|
| `SCHEMA` (`preflight.plan is required`) | The record names no plan revision | `plan`: the `plan_digest` the plan check prints, and the plan's base |
| `NEEDS_UNDECLARED` | A package has no `needs`, or a `command` criterion and no `environment` need; the plan check raises it only for an unattended plan | `needs` on every package, with an `environment` need for the tools its commands call |
| `PREREQUISITE_UNCOVERED` | No entry claims a declared need | `covers` on each entry, and `fixtures[]` for fixture needs |
| `PREFLIGHT_REQUIRED` (gate) | An unattended plan reaches the gate without a passing record | `execution.unattended: true` on a plan meant to run unwatched, and `--preflight <preflight.json>` on its gate |

`check_orchestration.py preflight <preflight.json> --plan <plan.json>
--profile alchemy-workspace.json --root .` returns `PASS`, `FAIL`, `STALE`,
or `ESCALATE` with the codes in [contracts.md](contracts.md). `PASS` with a
non-empty `queued` list means the run proceeds on reversible defaults the
human confirms at the merge boundary. The first wave starts only on `PASS`,
and the gate of an unattended plan re-checks the same record with
`--preflight <preflight.json>`. With `--root`, the repository may stand at the
plan's base or at an integrated head recorded in `base.integrated`, so the
record can be re-checked after a wave; its probes stay bound to the base.

## 5. During the Run

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
