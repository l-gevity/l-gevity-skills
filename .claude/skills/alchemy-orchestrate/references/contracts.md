# Orchestration Contracts — Plan, Hand-off, Ledger, Profile

The four records an orchestrated run exchanges, in the exact shape
`scripts/check_orchestration.py` reads. They are execution state for one
iteration: keep them under the profile's `state_dir` (default
`.alchemy/runs/<run-id>/`), never commit them, and never copy a requirement,
decision, or test result into them that a canonical artifact already holds —
link it by ID, path, commit, or command instead (`zero-copy-requirements`).

All four are JSON. Every record carries a `schema` string with a version; a
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
| `acceptance` | At least one criterion per package, so the plan holds at least one. `check` is `command` with a `command`, or `review` with a `question`. IDs are canonical criterion IDs where they exist. |
| `permissions` | Subset of `read`, `test`, `edit`, `commit`, and of the package's envelope. `push` and `pull_request` belong to the lead after human approval; `merge` and `deploy` never appear in a plan. |
| `approved_by` | `human` on a package that writes a protected path. A protected entry guards itself and every path under it, with or without a trailing `/`, case-insensitively. |
| `may_delegate` | Absent or `false`. Delegation depth is 1. |
| required | `id`, `kind`, `owner`, `envelope` (a profile envelope), `risk` (`low`, `medium`, `high`), `requirements`, `writes`, `depends_on`, `acceptance`, `permissions`. Package and criterion IDs are unique. |
| `conflicts` | `{"between": [ids], "resolution": null}` until a human or evidence resolves it: `{"basis": "human", "decided_by": "human", "rationale": "..."}` or `{"basis": "evidence", "evidence": [...], "rationale": "..."}`. |

## Hand-off — `alchemy-handoff/1`

Returned by every package owner, read-only packages included. It links
artifacts; it never pastes them.

```json
{
  "schema": "alchemy-handoff/1",
  "package": "P1",
  "owner": "agent-a",
  "status": "DONE",
  "attempt": 1,
  "base_commit": "3f9c2e1",
  "head_commit": "8a1d4b0",
  "requirements": ["REQ-12"],
  "decisions": [{"id": "D-4", "summary": "Validate at the HTTP boundary", "ref": "issue #42"}],
  "assumptions": ["Order totals are integers in cents"],
  "relied_on": [{"path": "src/orders/repository.js", "sha256": "<64 hex>"}],
  "changed_files": [{"path": "src/orders/validate.js", "sha256": "<64 hex>"}],
  "evidence": [{"id": "E1", "criterion": "REQ-12-AC1", "command": "npm test -- orders", "exit_code": 0, "commit": "8a1d4b0", "summary": "14 passed"}],
  "claims": [{"text": "Order input is validated before persistence", "evidence": ["E1"]}],
  "blockers": [],
  "next_owner": "lead",
  "integration_ready": true
}
```

`status` is `DONE`, `PARTIAL`, `BLOCKED`, or `FAILED`. A blocker is
`{"id", "text", "blocking": true|false}`; an evidence item needs `id`,
`command`, `exit_code`, and `commit`. An item passes when `exit_code` equals its
optional `expect_exit`, 0 when absent: a search proving absence records the
code it returns on no match, such as `git grep` with `"expect_exit": 1`, so an
error code still fails. Evidence for a `command` criterion passes only on exit
0; its `expect_exit` is ignored. Commits match when one is a hex prefix
of the other and at least seven characters long. `relied_on` lists every
artifact the work depended on with the digest it saw, so a receiver detects a
context that moved underneath it. `changed_files` digests are taken after the
change, so a receiver detects a summary that does not match the workspace.

## Ledger — `alchemy-ledger/1`

Kept by the lead from hand-offs, independent verification, and integration.

```json
{
  "schema": "alchemy-ledger/1",
  "head_commit": "c47e9aa",
  "rework_cycles": {"P1": 1},
  "evidence": [{"id": "E7", "command": "npm test", "exit_code": 0, "commit": "c47e9aa", "produced_by": "agent-c"}],
  "criteria": [
    {"id": "REQ-12-AC1", "package": "P1", "status": "verified", "evidence": ["E7"], "verified_by": "agent-c"},
    {"id": "REQ-13-AC2", "package": "P2", "status": "deferred", "deferred_by": "human", "reason": "Needs production data"}
  ],
  "findings": [
    {"id": "F1", "package": "P1", "severity": "blocking", "status": "resolved", "raised_by": "agent-c",
     "evidence": ["E5"], "resolution": {"by": "agent-a", "evidence": ["E7"]}}
  ],
  "disputes": [
    {"id": "X1", "subject": "Validate in handler or in repository",
     "positions": [{"by": "agent-a", "claim": "handler", "evidence": ["E7"]}, {"by": "agent-b", "claim": "repository", "evidence": []}],
     "status": "resolved",
     "resolution": {"basis": "evidence", "decided_by": "lead", "evidence": ["E7"], "rationale": "Only the handler position has a passing test"}}
  ]
}
```

| Field | Rule |
|:--|:--|
| `head_commit` | The integrated head. Every evidence item the gate relies on — for a verified criterion, a finding resolution or rejection, or a dispute decided on evidence — ran at it. |
| `criteria[].status` | `verified` (evidence IDs that passed at `head_commit`), `failed`, `unverified`, or `deferred` with `deferred_by: human`. Every plan criterion appears once. |
| `criteria[]` | `verified_by` is required when verified; `reason` when deferred. Only plan criteria, under their own package. When independent review is on or the package's risk is `high`, an `implement` criterion's `verified_by` is the owner of a `verify` package that reviews it. A verified `command` criterion cites evidence whose `command` is the plan's, whitespace-normalized, or that of an `equivalent: {"command", "accepted_by": "human"}` the human accepted in its place. |
| `evidence[]` | `id`, `command`, `exit_code`, `commit`; optional `produced_by`, `expect_exit` as in the hand-off, and `criterion`, the only criterion the item may verify. Items with the same normalized command, commit, and exit code are the same evidence, whatever their IDs. Profile verification commands pass only on exit 0. |
| `findings[].severity` | `blocking`, `major`, or `minor`. Blocking and major must end `resolved` with `resolution.evidence`, `rejected` with `resolution.evidence` showing the finding is wrong — sharing no evidence, by ID or identity, with the raiser's own `evidence` — or `accepted-risk` with `accepted_by: human`. |
| `disputes[].resolution.basis` | `evidence` with evidence IDs, only when exactly one position's evidence all exists and exited 0; when both positions or neither have it, the human decides. Or `human` with `decided_by: human`. Majority, seniority, model, and confidence are not a basis. |
| `rework_cycles` | Correction rounds per package; above the profile's `max_rework_cycles` the gate escalates. |

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
| `repository.protected_paths` | `[]` | Writes need `approved_by: human` |
| `repository.verification` | `[]` | Commands, as `{"id", "command"}` or plain strings, the integrated head must pass; the gate needs passing ledger evidence for each at `head_commit` |
| `repository.state_dir` | `.alchemy/runs/` | Run records; never committed; the only uncommitted changes `gate --root` tolerates |
| `approval` | human for `merge`, `push`, `pull_request`, `destructive`, `external` | Actions the lead may not take without the human |
| `envelopes` | `analyst`, `implementer` | Permission envelopes the adapters render |

## Check Codes

`check_orchestration.py` exits 0 on `PASS` or `ACCEPT`, 1 on any other verdict,
2 on unreadable input, and prints one JSON report. Verdict precedence:
`ESCALATE` over `REJECT`/`FAIL` over `STALE` over `RETRY` over a pass, because a
bound reached must stop rework rather than restart it.

| Code | Check | Verdict | Meaning |
|:--|:--|:--|:--|
| `SCHEMA` | all | FAIL / REJECT | A required field is missing or mistyped, a commit is not 7 to 64 hex characters, or the schema version is unknown |
| `SECRET_IN_RECORD` | all | FAIL / REJECT | A plan, hand-off, or ledger value matches a credential pattern or sits under a credential key; every report redacts it |
| `MISSING_TRACE` | plan, gate | FAIL | A package has no requirement ID, no acceptance criterion, or no skill, or the plan holds no criterion |
| `CYCLE` | plan, gate | FAIL | `depends_on` forms a cycle |
| `UNKNOWN_DEPENDENCY` | plan, gate | FAIL | A dependency, review target, or reviewed package does not exist |
| `INVALID_WRITE_SET` | plan, gate | FAIL | A write entry uses a wildcard other than a trailing `/**` |
| `WRITE_CONFLICT` | plan, gate | FAIL | Two packages with no dependency path between them write overlapping paths, compared case-insensitively |
| `READ_ONLY_WRITES` | plan, gate | FAIL | A `decide`, `verify`, or `analyze` package, or an `analyst` envelope, declares writes or `edit` |
| `CONTRACT_ORDER` | plan, gate | FAIL | A consumer does not depend on the producer of a contract it consumes |
| `UNKNOWN_CONTRACT` | plan, gate | FAIL | A consumed contract is neither produced nor existing |
| `SELF_REVIEW` | plan, gate | FAIL | A verifier owns a package it reviews |
| `REVIEW_ORDER` | plan, gate | FAIL | A `verify` package does not depend, directly or transitively, on a package it reviews |
| `UNREVIEWED_CHANGE` | plan, gate | FAIL | An `implement` package lacks an independent `verify` package while `independent_review` is true or its risk is `high` |
| `DELEGATION` | plan, gate | FAIL | A package may delegate, or the profile allows depth above 1 |
| `CAP_EXCEEDED` | plan, gate | FAIL | Declared parallelism or distinct owners exceed the profile |
| `PERMISSION_EXCEEDS` | plan, gate | FAIL | A package asks for `push`, `pull_request`, `merge`, `deploy`, an unknown permission, or one its envelope does not grant |
| `PROTECTED_PATH` | plan, gate | FAIL | A package writes a protected path, or a path under one, without `approved_by: human` |
| `MERGE_POLICY` | plan, gate | FAIL | `merge_policy` is not `human-approval` |
| `MODE_MISMATCH` | plan, gate | FAIL | `single-agent` with more than one agent (package owners plus the integration owner), `multi-agent` with one, or any multi-agent plan while the profile sets `execution.multi_agent` to `off` |
| `REQUIREMENT_CONFLICT` | plan, gate | ESCALATE | A recorded requirement conflict has no resolution, or a `human` basis the human did not decide |
| `UNKNOWN_PACKAGE` | handoff | REJECT | The hand-off names a package the plan does not hold |
| `OWNER_MISMATCH` | handoff | REJECT | The sender is not the package owner |
| `NOT_DONE` | handoff | REJECT | `PARTIAL` (returns to the owner), `BLOCKED` (escalates to the lead, then the human), or an `implement` package `DONE` but not integration-ready |
| `SCOPE_VIOLATION` | handoff | REJECT | A changed file lies outside the write set, or a read-only package changed files |
| `SCOPE_EXPANSION` | handoff | REJECT | The hand-off claims requirements its package was not assigned |
| `CLAIM_CONTRADICTS_WORKSPACE` | handoff | REJECT | A changed file is missing or its digest differs from the workspace |
| `CLAIM_CONTRADICTS_EVIDENCE` | handoff | REJECT | A claim cites failing evidence, or `DONE` or integration-ready while any evidence failed; failing is an exit code other than the item's expected one |
| `UNSUPPORTED_CLAIM` | handoff | REJECT | A claim cites no evidence or unknown evidence |
| `UNEVIDENCED_CRITERION` | handoff | REJECT | A `DONE` package leaves an acceptance criterion without evidence |
| `BLOCKER_IGNORED` | handoff | REJECT | Integration-ready with an open blocking blocker |
| `UNTRUSTED_INSTRUCTION` | handoff | REJECT | A value carries an instruction aimed at agents, such as ignoring prior instructions or skipping review |
| `STALE_BASE` | handoff | STALE | The base commit is neither the plan's base nor an integrated head |
| `STALE_CONTEXT` | handoff | STALE | A `relied_on` digest no longer matches the workspace |
| `AGENT_FAILED` | handoff | RETRY | `FAILED` within the retry budget |
| `RETRY_EXHAUSTED` | handoff | ESCALATE | `FAILED` with the retry budget spent |
| `SILENT_SKIP` | gate | FAIL | A plan criterion is missing from the ledger |
| `CRITERION_FAILED` | gate | FAIL | A criterion is `failed` |
| `UNVERIFIED` | gate | FAIL | A criterion is `unverified`, or deferred by anyone but the human |
| `UNSUPPORTED_VERDICT` | gate | FAIL | `verified` without evidence that exists, passed (exit 0 for a `command` criterion), runs the criterion's assigned or human-accepted check, and is not recorded for another criterion |
| `EVIDENCE_STALE` | gate | FAIL | Evidence a verified criterion, finding resolution, or dispute decision relies on was produced on a commit other than `head_commit` |
| `REVIEW_NOT_INDEPENDENT` | gate | FAIL | Independent review is required and the verifier is not the owner of a `verify` package that reviews the package |
| `UNRESOLVED_FINDING` | gate | FAIL | A blocking or major finding is open |
| `UNSUPPORTED_RESOLUTION` | gate | FAIL | A finding resolved or rejected without passing evidence, or rejected on its raiser's own evidence, by ID or identity |
| `RISK_NOT_ACCEPTED_BY_HUMAN` | gate | FAIL | `accepted-risk` without `accepted_by: human` |
| `VOTE_NOT_EVIDENCE` | gate | FAIL | A dispute resolved on a basis other than evidence or the human, on evidence it does not cite, or on a `human` basis the human did not decide |
| `VERIFICATION_FAILED` | gate | FAIL | A profile `repository.verification` command has no passing evidence at `head_commit` |
| `WORKSPACE_MISMATCH` | plan, gate | FAIL | With `--root`, the repository's HEAD is not the plan's base or an integrated head (plan) or `head_commit` (gate), it holds uncommitted changes outside `state_dir`, or git cannot confirm either |
| `DISPUTE_OPEN` | gate | ESCALATE | A dispute is open or escalated, or decided on evidence while both positions, or neither, have passing evidence |
| `REWORK_LIMIT` | gate | ESCALATE | A package exceeded `max_rework_cycles` |
