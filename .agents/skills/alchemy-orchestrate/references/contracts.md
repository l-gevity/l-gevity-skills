# Orchestration Contracts — Plan, Preflight, Hand-off, Ledger, Profile

The five records an orchestrated run exchanges, in the exact shape
`scripts/check_orchestration.py` reads. They are execution state for one
iteration: keep them under the profile's `state_dir` (default
`.alchemy/runs/<run-id>/`), never commit them, and never copy a requirement,
decision, or test result into them that a canonical artifact already holds —
link it by ID, path, commit, or command instead (`zero-copy-requirements`).

All five are JSON. Every record carries a `schema` string with a version; a
reader rejects a version it does not know. Unknown keys are allowed and ignored,
so a project overlay can annotate records without forking the format.

## Plan — `alchemy-plan/1`

Excerpt: package `P2`, a second `implement` package owned by `agent-b`, is
omitted.

```json
{
  "schema": "alchemy-plan/1",
  "objective": "Validate order input and paginate shipments",
  "requirements": ["REQ-12", "REQ-13"],
  "conflicts": [],
  "base": {"commit": "3f9c2e1"},
  "contracts_existing": ["contract:orders-repository"],
  "execution": {
    "mode": "multi-agent",
    "strategy": "dependency-aware",
    "max_parallel_agents": 2,
    "integration_owner": "lead",
    "independent_review": true,
    "merge_policy": "human-approval"
  },
  "packages": [
    {
      "id": "P1",
      "kind": "implement",
      "capabilities": ["engineering"],
      "skills": ["test-strategy"],
      "owner": "agent-a",
      "envelope": "implementer",
      "risk": "medium",
      "requirements": ["REQ-12"],
      "writes": ["src/orders/", "test/orders/"],
      "reads": ["src/"],
      "depends_on": [],
      "produces": [],
      "consumes": ["contract:orders-repository"],
      "acceptance": [{"id": "REQ-12-AC1", "check": "command", "command": "npm test -- orders"}],
      "permissions": ["read", "edit", "test"],
      "budget": {"max_turns": 40}
    },
    {
      "id": "P3",
      "kind": "verify",
      "capabilities": ["verification", "security"],
      "skills": ["test-strategy"],
      "owner": "agent-c",
      "envelope": "analyst",
      "risk": "low",
      "requirements": ["REQ-12", "REQ-13"],
      "writes": [],
      "reads": ["src/", "test/"],
      "depends_on": ["P1", "P2"],
      "reviews": ["P1", "P2"],
      "acceptance": [{"id": "P3-AC1", "check": "review", "question": "Do the diffs meet REQ-12 and REQ-13 with passing evidence?"}],
      "permissions": ["read", "test"]
    }
  ]
}
```

| Field | Rule |
|:--|:--|
| `base` | `commit` the run starts from; `integrated` lists heads the lead integrated a wave at, which later waves may start from. Every commit in every record is a hex SHA of 7 to 64 characters. |
| `kind` | `decide` (architecture or contract decision), `implement`, `verify`, or `analyze`. Only `implement` writes. |
| `owner` | The agent label. `lead` is the integration owner. Distinct owners are the agent count. Owner labels and `human` compare trimmed and case-insensitively. |
| `envelope` | `analyst` (read, test) or `implementer` (read, edit, test, commit); the runtime adapter enforces it where it can. |
| `skills` | At least one skill the agent loads from the library, never from text pasted into its prompt. |
| `writes` | Files, or directories ending in `/`. `dir/**` is read as `dir/`. Any other wildcard is rejected, so overlap stays decidable: two write sets overlap when one entry equals or is a directory prefix of the other, compared case-insensitively. |
| `depends_on` | Package IDs. The graph must be acyclic. |
| `produces` / `consumes` | Contract names. A consumer depends, directly or transitively, on the producer; a consumed contract nobody produces must be listed in `contracts_existing`. |
| `reviews` | `verify` only: the packages it reviews. Its owner owns none of them, and it depends, directly or transitively, on each. |
| `acceptance` | At least one criterion per package, so the plan holds at least one. `check` is `command` with a `command`, or `review` with a `question`. IDs are canonical criterion IDs where they exist. A check proves a `review` criterion's evidence passed, not that it answers the question. |
| `permissions` | Subset of `read`, `test`, `edit`, `commit`, and of the package's envelope. `push` and `pull_request` belong to the lead after human approval; `merge` and `deploy` never appear in a plan. |
| `approved_by` | `human` on a package of the approved plan that writes a protected path; the human approves the plan that carries it. A protected entry guards itself and every path under it, with or without a trailing `/`, case-insensitively. An amendment's protected write needs an `approval` record instead. |
| `may_delegate` | Absent or `false`. Delegation depth is 1. |
| `budget` | `{"max_turns", "max_tool_calls"}`, positive integers. A key left out takes its envelope's ceiling; a value above that ceiling is `BUDGET_EXCEEDS`, because the runtime stops the agent at the ceiling. The plan check prints each package's effective budget under `budgets`. An agent that reaches its budget stops and returns `BLOCKED` with a blocking blocker naming it. |
| `execution.unattended` | `true` when the run proceeds while nobody watches; absent is `false`. Every package then states `needs`, and the gate requires a passing preflight bound to the plan. The field is the plan author's statement: the gate holds the run to it, but it does not prove that anybody watches. A workflow that records the human's choice at plan approval treats an absent or unclear answer as unattended, and stops before any probe a run the human leaves unattended whose plan is not. |
| `needs` | Package prerequisites for an unattended run, each `{"id", "kind", "what"}` with `kind` `access`, `account`, `environment`, or `fixture`; absent is undeclared, `[]` declares none. Shared needs repeat one `id` with one kind. Coverage rules are in [autonomy-preflight.md](autonomy-preflight.md). |
| required | `id`, `kind`, `owner`, `envelope` (a profile envelope), `risk` (`low`, `medium`, `high`), `requirements`, `writes`, `depends_on`, `acceptance`, `permissions`. Package and criterion IDs are unique. |
| `amendments` | Rework and replanning added after approval, in order; see Amendments below. Absent is none. |
| `execution.rework_extension` | A ceiling above the profile's `max_rework_cycles` for this run: `{"ceiling", "conditions", "authorization"}`, captured in the approved plan before the first cycle that uses it; see Amendments below. |
| `conflicts` | `{"between": [ids], "resolution": null}` until a human or evidence resolves it: `{"basis": "human", "decided_by": "human", "rationale": "..."}` or `{"basis": "evidence", "evidence": [...], "rationale": "..."}`. |

### Scheduling a checked plan

The plan check retains `waves` for a batch runtime and reports `ready` for
the current state. Re-run `check_orchestration.py plan <plan.json> --completed A
--running B` with the same profile, approval/revision anchors, and `--root` at
the clean integrated head. Repeat each option for every package in that state.
`completed` means its hand-off was checked and accepted, its decisions accepted,
and its changes integrated and committed; finishing alone never qualifies. The
caller supplies these facts; the check cannot prove runtime completion.

`ready` releases packages whose dependencies are completed, within the lower
plan/profile sub-agent cap, with no owner running two packages. The lead is
excluded from that cap. Unknown IDs, overlapping states, unmet dependencies,
duplicate active owners, and excess running agents are rejected. A failing
plan releases nothing. Record the returned IDs as running before calling again;
this is a single lead's scheduling calculation, not a concurrent reservation.

Use it after each accepted integration only when the runtime delivers individual
completions, all in-flight inputs are pinned to immutable heads, and integration
cannot alter another agent's live read scope. Otherwise use `waves`, including
foreground batch runtimes. Keep the lead alive until every spawned agent finishes;
do not replace a safe wait with detached agents. Scheduling never bypasses the
plan, unattended preflight, hand-off checks, or final integrated-head gate.

### Amendments

The plan owns packages, so rework is a change to the plan: the lead appends
an amendment before anybody edits, and every rule that holds for a package
holds for the package it adds, whoever owns it, the lead included. The
approved revision is the plan without `amendments`; the plan check prints its
digest as `approved_digest`, and `--approved <digest>` on the plan and gate
checks refuses a plan that holds no such revision (`AMENDMENT_INVALID`). A plan
with amendments, and at the gate one with an extension or a ledger recording
rework (`rework_cycles`, `after`, `introduced_by`, `reopened_after`), fails
without it: those rules mean nothing unanchored. When the human approves an
amended revision, `--approved` names that revision's digest, and the
amendments it holds count as approved. `--revision <digest>`, a `plan_digest`
an earlier check of the run printed, refuses a plan that no longer holds that
revision: amendments are only appended, so deleting one cannot reset a count.
The workflow adapter feeds both from step outputs the lead does not write.

```json
{"id": "A1", "origin": "P1", "supersedes": "<digest of the revision before it>", "base": "c47e9aa",
 "reason": "corrects F1", "findings": ["F1"], "reviewer": "agent-c",
 "package": {"id": "P1-R1", "kind": "implement", "owner": "agent-a", "depends_on": ["P1"], "...": "a package record"}}
```

| Field | Rule |
|:--|:--|
| `origin` | The package the work originates from: an approved package or one an earlier amendment added. A rename is an amendment whose package has a new ID. The rework budget is counted along the chain of origins (`REWORK_LIMIT`); an amendment whose writes overlap the approved write set of another chain counts against that chain too. |
| `supersedes` | `revision_digest` of the plan with the amendments before this one; the first names `approved_digest`. |
| `base` | The plan base or an integrated head the rework starts from. |
| `reviewer` | Required on an `implement` (rework) or `decide` (replanning) amendment; never the package owner (`SELF_REVIEW`). Under independent review or high risk it owns a `verify` package of the plan. It verifies the package's criteria at the gate. |
| `findings` | Ledger finding IDs the cycle corrects, at least one of them blocking or major (`REWORK_MINOR_ONLY`); a cycle beyond `max_rework_cycles` needs them to meet the extension's conditions. Each amendment is one cycle, so a correction pass adds one amendment per origin chain, listing every finding it answers, never one per finding. |
| `package` | A full package record. It depends on its `origin`. Inside the approved envelope it writes only paths an approved `implement` package writes, asks for no permission the first package of its origin chain lacks, and keeps that package's risk or raises it; anything else is `AMENDMENT_BROADENS`, and a protected write is `PROTECTED_PATH`, unless `approval` holds a valid authorization and the revision `--approved` names holds the amendment. An amendment after that revision cannot broaden, whatever its `approval` says: the run stops, and the human approves a revision that holds it. |
| `approval` | An authorization: `{"by": "human", "ref", "source": "answer", "expires"}`. `ref` names where the human said so (an approval step, an issue or review comment); `source` is `answer`, never a timeout or a default; `expires`, when present, is still ahead. Otherwise `AUTHORIZATION_UNPROVEN`. The checker cannot open `ref`: the gate lists each one under `authorizations` for the human to read. |

An amendment is inside the plan revision: `plan_digest` covers it, so a
preflight made before it is `PREFLIGHT_STALE`, and a need it adds is
`PREREQUISITE_UNCOVERED` until an entry of a record bound to the new
revision claims it.

`execution.rework_extension` raises the bound only when its `authorization`
is valid, its `ceiling` exceeds the profile's bound, and the gate is given
the approved revision with `--approved`, which shows the extension predates
the run (`AUTHORIZATION_UNPROVEN` otherwise; the profile's bound applies).
Each cycle beyond the profile's bound then meets every listed condition:
`new-finding`, it corrects a blocking or major finding the review after the
previous cycle raised and nobody reopened; `same-check-green`, a check that
failed for that finding passes at head. A cycle that misses one is
`REWORK_LIMIT`.

## Hand-off — `alchemy-handoff/1`

Returned by every package owner, read-only packages included: shape, evidence,
claims, and findings are in [handoff.md](handoff.md), the only file of this
skill a delegated agent reads.

## Ledger — `alchemy-ledger/1`

Kept by the lead from hand-offs, independent verification, and integration.

```json
{
  "schema": "alchemy-ledger/1",
  "head_commit": "c47e9aa",
  "rework_cycles": {"P1": 1},
  "evidence": [{"id": "P3-E7", "command": "npm test", "exit_code": 0, "commit": "c47e9aa", "produced_by": "agent-c"}],
  "criteria": [
    {"id": "REQ-12-AC1", "package": "P1", "status": "verified", "evidence": ["P3-E7"], "verified_by": "agent-c"},
    {"id": "REQ-13-AC2", "package": "P2", "status": "deferred", "deferred_by": "human", "reason": "Needs production data"}
  ],
  "findings": [
    {"id": "F1", "package": "P1", "severity": "blocking", "status": "resolved", "raised_by": "agent-c",
     "evidence": ["P3-E5"], "resolution": {"by": "agent-a", "evidence": ["P3-E7"]}}
  ],
  "disputes": [
    {"id": "X1", "subject": "Validate in handler or in repository",
     "positions": [{"by": "agent-a", "claim": "handler", "evidence": ["P3-E7"]}, {"by": "agent-b", "claim": "repository", "evidence": []}],
     "status": "resolved",
     "resolution": {"basis": "evidence", "decided_by": "lead", "evidence": ["P3-E7"], "rationale": "Only the handler position has a passing test"}}
  ]
}
```

| Field | Rule |
|:--|:--|
| `head_commit` | The integrated head. Every evidence item the gate relies on — for a verified criterion, a finding resolution or rejection, or a dispute decided on evidence — ran at it. |
| `criteria[].status` | `verified` (evidence IDs that passed at `head_commit`), `failed`, `unverified`, or `deferred` with `deferred_by: human`. Every plan criterion appears once. |
| `criteria[]` | `verified_by` is required when verified; `reason` when deferred. Only plan criteria, under their own package. When independent review is on or the package's risk is `high`, an `implement` criterion's `verified_by` is the owner of a `verify` package that reviews it. A verified `command` criterion cites evidence whose `command` is the plan's, whitespace-normalized, or that of an `equivalent: {"command", "accepted_by": "human"}` the human accepted in its place. |
| `evidence[]` | `id`, `command`, `exit_code`, `commit`; optional `produced_by`, `expect_exit` as in the hand-off, `criterion`, the only criterion the item may verify, and `log` and `log_sha256`, the output file and its digest. Items with the same normalized command, commit, and exit code are the same evidence, whatever their IDs. Profile verification commands pass only on exit 0. |
| `findings[]` | Optional convergence links, recorded by the reviewer who raises the finding: `after`, the amendment whose review raised it (absent: the review of the planned work); `related_to`, earlier finding IDs in the same component or of the same class; `introduced_by`, the amendment whose fix caused it; `reopened_after`, the amendments after which it was reopened. Each named amendment and finding exists, and `package` names a plan package. Once the plan has amendments, every blocking or major finding names its `package`, and one with `related_to` or `introduced_by` names `after` (`SCHEMA` otherwise). The gate evaluates them as governance section 2 states (`NOT_CONVERGING`). |
| `--review` | A reviewer's own output, a file the reviewing step wrote, or a saved hand-off; repeat it to give every one. Each of its blocking or major findings appears in the ledger under its ID, at no lower severity, for the same package (a hand-off's own `package` for its findings), with every `related_to` link, `introduced_by` when it is a `regression`, and `reopened_after` on the finding it `reopens` (`SILENT_SKIP` otherwise). The gate checks that the ledger keeps what the reviewer recorded; whether a finding is related, a regression, or reopened is the reviewer's judgment, which no check confirms. Without `--review` the gate reads the ledger alone. |
| `findings[].severity` | `blocking`, `major`, or `minor`. In a run whose plan holds no `implement` package, a blocking or major finding may stay `open`: it is the run's result, which the gate lists under `open_serious`, and it cites passing evidence (`UNSUPPORTED_FINDING`). Otherwise blocking and major must end `resolved` with `resolution.evidence`, `rejected` with `resolution.evidence` showing the finding is wrong — sharing no evidence, by ID or identity, with the raiser's own `evidence` — or `accepted-risk` with `accepted_by: human`. |
| `disputes[].resolution.basis` | `evidence` with evidence IDs, only when exactly one position's evidence all exists and exited 0; when both positions or neither have it, the human decides. Or `human` with `decided_by: human`. Majority, seniority, model, and confidence are not a basis. |
| `rework_cycles` | A claim of correction rounds per package, summed along each origin chain. The gate counts the chain's rework amendments and takes the larger number, so neither a rename nor a new rework package starts at zero; above the bound it escalates. A ledger that records it, even for a plan without amendments, needs `--approved` on the gate (`AMENDMENT_INVALID` otherwise; see the upgrade table below). |
| `usage[]` | What each delegated package spent, as the runtime reported it to the lead; absent when the runtime reports nothing: `package` and any of `turns`, `tool_calls`, `duration_ms`, `tokens`, non-negative integers. The gate reports totals and `over_budget`, the packages that spent more turns or tool calls than their effective budget; it is a fact for the report and the scale-down decision, not a verdict. |
| `changed_files` | Optional: the paths of the integrated diff from the plan base. With `--root` the gate reads them from git instead, without rename detection, so a moved file counts at its source and its destination. Each lies in an `implement` package's write set, amendments included, or under `state_dir` (`UNOWNED_WRITE`). |

`scripts/record_evidence.py --plan <plan.json> --root <repository>` produces
these items. It runs only the commands the plan's `command` criteria and the
profile's `repository.verification` declare, at a committed head that is clean
outside `state_dir`, and writes per command a log of its combined output and
one `evidence[]` item with `produced_by: harness`, `log`, and `log_sha256`. The
ID is the criterion or verification ID, `@`, and the head's short commit. A
command that leaves the work tree changed fails the run, because its result is
not the commit's alone. A verifier reads these logs and cites their IDs:
running the same command on the same commit again yields the same evidence,
by the identity rule above, and adds nothing.

A plan or gate check that passed without the approved revision before rework
was anchored fails after the upgrade:

| Fails with | Because | Add |
|:--|:--|:--|
| `AMENDMENT_INVALID` (gate: `the plan carries recorded rework but no approved revision anchors it`) | The ledger records `rework_cycles` or a finding with `after`, `introduced_by`, or `reopened_after`, or the plan carries `execution.rework_extension`; this holds for a plan without amendments too, which used to pass | `--approved <digest>` on the gate: the `approved_digest` the plan check printed when the human approved the plan, or the digest of the amended revision the human approved since |
| `AMENDMENT_INVALID` (plan: `the plan carries amendments but no approved revision anchors it`) | A plan with amendments is checked without the anchor | `--approved <digest>` on the plan check, the same digest |

## Preflight — `alchemy-preflight/1`

The record that proves a checked plan can run unattended for its whole
window: work that may start, decisions the human made, access, test accounts,
and environment proved by probes executed at the plan base, a green baseline,
bounds with a test-delivered escalation channel, and human steps only before
or after the window. It is bound to the plan revision by the plan's digest
and base, and covers every need the packages and the profile declare. Shape,
field rules, and the checklist behind it are in
[autonomy-preflight.md](autonomy-preflight.md). The checker reads the probe
evidence and never runs a probe.

## Profile — `alchemy-workspace/1`

The project overlay, committed at the repository root as
`alchemy-workspace.json`. `assets/alchemy-workspace.json` holds the defaults;
a project file overrides only the keys it states.

| Key | Default | Meaning |
|:--|:--|:--|
| `execution.multi_agent` | `auto` | `off` refuses any multi-agent plan (`MODE_MISMATCH`) |
| `execution.default_mode` | `single-agent` | Mode when no rule selects another |
| `execution.max_parallel_agents` | `3` | Concurrent agents, lead excluded |
| `execution.max_agents` | `5` | Distinct owners per run, lead included |
| `execution.max_delegation_depth` | `1` | Fixed; a delegated agent never delegates |
| `execution.max_retries` | `1` | Re-runs of a failed package from its base |
| `execution.max_rework_cycles` | `2` | Correction rounds per package before escalation |
| `envelopes.<name>.budget` | analyst 45 turns, 50 tool calls; implementer 60 turns, 70 tool calls | The ceiling a package budget may not exceed; the runtime adapter renders `max_turns` into the agent definition where the runtime enforces it |
| `repository.protected_paths` | `[]` | Writes need `approved_by: human` |
| `repository.verification` | `[]` | Commands, as `{"id", "command"}` or plain strings, the integrated head must pass; the gate needs passing ledger evidence for each at `head_commit` |
| `preflight.needs` | `[]` | Needs every unattended run of the project has, shaped as a package's `needs`; a preflight covers them too |
| `repository.state_dir` | `.alchemy/runs/` | Run records; never committed; the only uncommitted changes `gate --root` tolerates |
| `approval` | human for `merge`, `push`, `pull_request`, `destructive`, `external` | Actions the lead may not take without the human |
| `envelopes` | `analyst`, `implementer` | Permission envelopes the adapters render |

## Check Codes

`check_orchestration.py` exits 0 on `PASS` or `ACCEPT`, 1 on any other verdict,
2 on unreadable input, and prints one JSON report. Verdict precedence:
`ESCALATE` over `REJECT`/`FAIL` over `STALE` over `RETRY` over a pass, because a
bound reached must stop rework rather than restart it.

The codes, the checks that raise them, their verdicts, and their meanings are
in [check-codes.md](check-codes.md). Read the row of a code a check reports.
