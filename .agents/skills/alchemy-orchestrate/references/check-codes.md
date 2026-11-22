# Check Codes — `check_orchestration.py`

Read the row of a code a check reports. Exit codes and verdict precedence are
in [contracts.md](contracts.md), Check Codes.

| Code | Check | Verdict | Meaning |
|:--|:--|:--|:--|
| `SCHEMA` | all | FAIL / REJECT | A required field is missing or mistyped, a commit is not 7 to 64 hex characters, a hand-off path is absolute, escapes the workspace, or carries a commit suffix, or the schema version is unknown |
| `SECRET_IN_RECORD` | all | FAIL / REJECT | A plan, preflight, hand-off, or ledger value matches a credential pattern or sits under a credential key; every report redacts it |
| `MISSING_TRACE` | plan, gate | FAIL | A package has no requirement ID, no acceptance criterion, or no skill, or the plan holds no criterion |
| `CYCLE` | plan, gate | FAIL | `depends_on` forms a cycle |
| `UNKNOWN_DEPENDENCY` | plan, gate | FAIL | A dependency, review target, or reviewed package does not exist |
| `INVALID_WRITE_SET` | plan, gate | FAIL | A write entry uses a wildcard other than a trailing `/**` |
| `WRITE_CONFLICT` | plan, gate | FAIL | Two packages with no dependency path between them write overlapping paths, compared case-insensitively |
| `READ_ONLY_WRITES` | plan, gate | FAIL | A `decide`, `verify`, or `analyze` package, or an `analyst` envelope, declares writes or `edit` |
| `CONTRACT_ORDER` | plan, gate | FAIL | A consumer does not depend on the producer of a contract it consumes |
| `UNKNOWN_CONTRACT` | plan, gate | FAIL | A consumed contract is neither produced nor existing |
| `SELF_REVIEW` | plan, gate | FAIL | A verifier owns a package it reviews, or an amendment names its package's owner as reviewer |
| `REVIEW_ORDER` | plan, gate | FAIL | A `verify` package does not depend, directly or transitively, on a package it reviews |
| `UNREVIEWED_CHANGE` | plan, gate | FAIL | An `implement` package lacks an independent `verify` package while `independent_review` is true or its risk is `high` |
| `DELEGATION` | plan, gate | FAIL | A package may delegate, or the profile allows depth above 1 |
| `CAP_EXCEEDED` | plan, gate | FAIL | Declared parallelism or distinct owners exceed the profile |
| `PERMISSION_EXCEEDS` | plan, gate | FAIL | A package asks for `push`, `pull_request`, `merge`, `deploy`, an unknown permission, or one its envelope does not grant |
| `PROTECTED_PATH` | plan, gate | FAIL | A package writes a protected path, or a path under one, without `approved_by: human`, or an amendment does without a valid `approval` in a revision `--approved` names |
| `MERGE_POLICY` | plan, gate | FAIL | `merge_policy` is not `human-approval` |
| `BUDGET_EXCEEDS` | plan, gate | FAIL | A package budget exceeds its envelope's ceiling |
| `REWORK_MINOR_ONLY` | gate | FAIL | A rework amendment's `findings` are all minor in the ledger: a correction cycle is spent on blocking or major findings, and minor ones stay open for the pull request |
| `MODE_MISMATCH` | plan, gate | FAIL | `single-agent` with more than one agent (package owners plus the integration owner), `multi-agent` with one, or any multi-agent plan while the profile sets `execution.multi_agent` to `off` |
| `REQUIREMENT_CONFLICT` | plan, gate | ESCALATE | A recorded requirement conflict has no resolution, or a `human` basis the human did not decide |
| `UNKNOWN_PACKAGE` | handoff | REJECT | The hand-off names a package the plan does not hold |
| `OWNER_MISMATCH` | handoff | REJECT | The sender is not the package owner |
| `NOT_DONE` | handoff | REJECT | `PARTIAL` (returns to the owner), `BLOCKED` (escalates to the lead, then the human), or an `implement` package `DONE` but not integration-ready |
| `SCOPE_VIOLATION` | handoff | REJECT | A changed file lies outside the write set, or a read-only package changed files |
| `SCOPE_EXPANSION` | handoff | REJECT | The hand-off claims requirements its package was not assigned |
| `CLAIM_CONTRADICTS_WORKSPACE` | handoff | REJECT | A changed file is missing or its digest differs from the workspace, or a file declared deleted still exists |
| `CLAIM_CONTRADICTS_EVIDENCE` | handoff | REJECT | A claim cites failing evidence, or `DONE` or integration-ready while any evidence failed; failing is an exit code other than the item's expected one |
| `UNSUPPORTED_CLAIM` | handoff | REJECT | A claim or a finding cites no evidence or unknown evidence |
| `UNEVIDENCED_CRITERION` | handoff | REJECT | A `DONE` package leaves an acceptance criterion without evidence |
| `BLOCKER_IGNORED` | handoff | REJECT | Integration-ready with an open blocking blocker |
| `UNTRUSTED_INSTRUCTION` | handoff | REJECT | A value carries an instruction aimed at agents, such as ignoring prior instructions or skipping review |
| `STALE_BASE` | handoff | STALE | The base commit is neither the plan's base nor an integrated head |
| `STALE_CONTEXT` | handoff | STALE | A `relied_on` digest no longer matches the workspace |
| `AGENT_FAILED` | handoff | RETRY | `FAILED` within the retry budget |
| `RETRY_EXHAUSTED` | handoff | ESCALATE | `FAILED` with the retry budget spent |
| `SILENT_SKIP` | gate | FAIL | A plan criterion is missing from the ledger, or the ledger drops or weakens a blocking or major finding or a convergence link a reviewer's own output or a saved hand-off (`--review`) records |
| `CRITERION_FAILED` | gate | FAIL | A criterion is `failed` |
| `UNVERIFIED` | gate | FAIL | A criterion is `unverified`, or deferred by anyone but the human |
| `UNSUPPORTED_VERDICT` | gate | FAIL | `verified` without evidence that exists, passed (exit 0 for a `command` criterion), runs the criterion's assigned or human-accepted check, and is not recorded for another criterion |
| `EVIDENCE_STALE` | gate | FAIL | Evidence a verified criterion, finding resolution, or dispute decision relies on was produced on a commit other than `head_commit` |
| `REVIEW_NOT_INDEPENDENT` | gate | FAIL | Independent review is required and the verifier is not the owner of a `verify` package that reviews the package |
| `UNRESOLVED_FINDING` | gate | FAIL | A blocking or major finding is open in a run with an `implement` package |
| `UNSUPPORTED_FINDING` | gate | FAIL | An open blocking or major finding of a run without an `implement` package cites no evidence, unknown evidence, or evidence that did not exit with its expected code |
| `UNSUPPORTED_RESOLUTION` | gate | FAIL | A finding resolved or rejected without passing evidence, or rejected on its raiser's own evidence, by ID or identity |
| `RISK_NOT_ACCEPTED_BY_HUMAN` | gate | FAIL | `accepted-risk` without `accepted_by: human` |
| `VOTE_NOT_EVIDENCE` | gate | FAIL | A dispute resolved on a basis other than evidence or the human, on evidence it does not cite, or on a `human` basis the human did not decide |
| `VERIFICATION_FAILED` | gate | FAIL | A profile `repository.verification` command has no passing evidence at `head_commit` |
| `WORKSPACE_MISMATCH` | plan, preflight, gate | FAIL | With `--root`, the repository's HEAD is not the plan's base or an integrated head (plan, preflight), or `head_commit` (gate), it holds uncommitted changes outside `state_dir` other than Python bytecode caches, or git cannot confirm either |
| `DISPUTE_OPEN` | gate | ESCALATE | A dispute is open or escalated, or decided on evidence while both positions, or neither, have passing evidence |
| `REWORK_LIMIT` | gate | ESCALATE | An origin chain took more correction cycles than `max_rework_cycles` or an extension's ceiling, or a cycle beyond the profile's bound misses an extension condition |
| `WORK_NOT_READY` | preflight | FAIL | A plan requirement sits in no `READY` increment and no reversible `PARTLY-READY` one |
| `PREREQUISITE_UNPROVEN` | preflight | FAIL | An access, account, environment, or escalation entry cites no probe, unknown evidence, a failing probe, or one run on a commit other than the plan base; or no access is recorded |
| `INTERACTIVE_STEP` | preflight | FAIL | An entry needs a person at a prompt inside the window |
| `CREDENTIAL_EXPIRES` | preflight | FAIL | An access or account credential expires at or before the window end |
| `ACCOUNT_CONFLICT` | preflight | FAIL | Two packages with no dependency path between them use one test account not marked `shared` |
| `BASELINE_RED` | preflight | FAIL | The profile declares no verification command, or one has no passing evidence at the plan base |
| `UNBOUNDED_RUN` | preflight | FAIL | The window, spend limit, stop conditions, or escalation channel is missing, or the window ends before it starts |
| `HUMAN_STEP_MIDRUN` | preflight | FAIL | A human step is scheduled `during` the window |
| `OPEN_DECISION` | preflight | ESCALATE | A decision is `open`, decided by anyone but the human, or a `default` that is not reversible |
| `NEEDS_UNDECLARED` | plan, preflight, gate | FAIL | In an unattended plan, a package has no `needs`, or has a `command` criterion and no `environment` need |
| `PREREQUISITE_UNCOVERED` | preflight | FAIL | A need a package or the profile declares is covered by no preflight entry of its kind, or an account need only by accounts that do not name the package |
| `PREFLIGHT_STALE` | preflight | STALE | The record's `plan.digest` or `plan.base` is not the checked plan's: the plan changed, or the base moved, after the preflight |
| `AMENDMENT_INVALID` | plan, gate | FAIL | An amendment names an origin that does not exist before it, a superseded revision other than the one before it, a base the run does not hold, or no reviewer; its package does not depend on its origin; it patches work the convergence rule stopped; with `--approved`, the plan holds no such revision; without it, the plan carries amendments, or at the gate an extension or recorded rework; or, with `--revision`, the plan no longer holds that revision |
| `AMENDMENT_BROADENS` | plan, gate | FAIL | An amendment writes outside the approved plan's write sets, asks for a permission its origin lacks, or lowers its origin's risk, without a valid `approval` in a revision `--approved` names |
| `AUTHORIZATION_UNPROVEN` | plan, gate | FAIL | An extension or amendment approval is not granted by the human, names no reference, names a source other than the human's answer (a timeout, a default), or expired; an extension no approved revision anchors; or, with `--root`, a `max_rework_cycles` above the one committed at the plan base |
| `UNOWNED_WRITE` | gate | FAIL | A path of the integrated diff lies in no `implement` package's write set, amendments included, and not under `state_dir` |
| `NOT_CONVERGING` | gate | ESCALATE | The convergence rule of governance section 2 fired for an origin chain; the report lists the `stopped` packages and those that `may_continue` |
| `PREFLIGHT_REQUIRED` | gate | FAIL | The plan is unattended and the gate has no preflight record, or a given record does not pass against the plan: missing, failed, or stale |
