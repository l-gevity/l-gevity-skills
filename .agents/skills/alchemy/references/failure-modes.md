# Failure-Mode Diagnostics

Symptoms that reveal a skipped qualification stage, gate, or companion pass,
each with the recovery that returns work to the named stage. `SKILL.md` §6
points here when a run, an audit, or a decision trail shows one of them. This
table adds no rule of its own; every recovery names the sibling skill or gate
that owns it, and re-entry starts at that stage, never at the beginning of the
pipeline.

| Symptom | Skipped gate | Recovery |
|:--|:--|:--|
| Architecture starts from an assumed or stale problem | Requirements Grounding | Stop; source or confirm actor, problem, scope, and completion evidence |
| Capability shipped or acceptance passed is reported as outcome success | Requirements Grounding | Separate completion evidence from the linked outcome hypothesis; measure impact after representative use |
| Requirement order is prose-only, cyclic, or contradictory | Requirements Topology | Build the typed graph; return blocking conflicts or cycles to grounding |
| Requirement text carries an old and a new decision at once | Requirements Topology — predecessor not retired | Retire it or mark it lapsing with an expiry in the same change; rerun the repository gate |
| Architecture invents meaning, permissions, data, or acceptance criteria | Implementation Readiness | Stop at `NOT-READY`; resolve the named product or policy blocker |
| `PARTLY-READY` work can be invalidated by an unresolved requirement | Implementation Readiness | Reject the increment; admit only bounded reversible work |
| Interface added "for the second implementation" but second never lands | 1 — Rule of 3 | Run pruner; collapse to one concrete |
| Generic registry / plugin system with one entry | 1 — generality without instantiation | Inline the entry; remove the registry |
| Empty config / config with one value across all envs | 1 — one-value config | Inline the value |
| `if (impossible_state)` runtime guards | 1 — impossible-state guard | OBSOLETE; document the invariant elsewhere |
| Cross-domain imports bypass the declared boundary | 3 — topology violated | Move the subsystem or introduce one named boundary |
| Aspect hand-wired per subsystem (n copies of auth, audit, or logging) | 2 — aspect extraction skipped | Re-run A with the aspect's holds-across set; C measures the n → 1 extraction |
| Refactor "felt simpler" but no measurement | 3–4 — topology candidate not accepted | Compute Subsystem-kinds / Dependency-edges / Max-chain-depth / Subsystem-count Δ, then re-enter Gate 3 once for final acceptance |
| Eslint rules added in follow-up PR | 5 — same-PR discipline broken | Block the follow-up; add rules to original PR |
| Defects caught at runtime that types could express | 6 — left-shift not applied | Move the check upward; remove the runtime guard |
| Architecture file disagrees with code | 5 — drift | Re-run lint; treat as a defect |
| Many tests or high coverage but no risk or oracle rationale | Test Strategy companion | Run `test-strategy`; map material risks to credible evidence and remove false-confidence metrics |
| Test scope or fidelity was frozen before architecture boundaries were accepted | Test Strategy companion | Preserve the Obligation pass; rerun the affected Portfolio rows after final A/L/C/E and before H |
| Migration ran green in development but the code versions live during rollout or rollback cannot all read the shape | Evolutionary Database Design companion | Run `evolutionary-database-design`; inventory the coexisting versions and stage the change as expand/contract |
| Expansion never contracted: parallel columns, dual writes, or `_old`/`_new` pairs with no closing evidence | Evolutionary Database Design companion — contract trigger undefined | Name the evidence that closes the old shape and an owner, or record it as accepted residual risk |
| Contract or destructive migration shipped in the same deployable as its expand step | Evolutionary Database Design companion — staged path collapsed | Split the deployable; gate the contract step on evidence and a snapshot |
| Requirement marked verified from a code anchor or unexecuted test | Implementation follow-through | Run `requirements-traceability`; separate implemented from verified evidence |
| A model, inventory, or design doc asserts another artifact's state and the code contradicts it | Implementation follow-through | Run `requirements-traceability`; prose about another artifact's state is a trace anchor, not narration |
| Decided text cannot land because the trace gate refuses an unbuilt criterion, so text lags decisions | Implementation follow-through — gate admits no pending or lapsing state | Admit pending and lapsing states in the gate; the retirement lands with the implementation |
| Stale or inconclusive outcome evidence silently justifies KEEP or DROP | Outcome follow-through → M | Refresh or bound the evidence in `requirements-traceability`, then rerun only M in Retrospective mode |
| Duplicate implementations are unified but retain separate behavior tests | 6 — integration / contract | Add one shared conformance suite and real-boundary coverage for backend-specific semantics before deleting either copy |
| "Just in case" extension point with one user | 1 — speculative optionality | DROP unless second use is named and probable |
| Premature performance optimization | 7 — applied before baseline | Revert; re-apply after stability |
