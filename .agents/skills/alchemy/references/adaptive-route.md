# Adaptive Route — Qualification, Gates, and Handshakes

Read before selecting stages when dispatch is `ADAPTIVE` or `FULL`, or the
alias is `audit`. `SKILL.md` owns dispatch, aliases, companions, gate
prerequisites, and the output contract; this file owns the route those
dispatches walk. For each qualification stage or gate selected, read the
sibling skill's `SKILL.md` and follow its procedure and output contract; this
file does not duplicate that content.

## 1. Adaptive Requirements Qualification

The requirements skills are conditional qualification stages around **M —
Minimum**, in the order `SKILL.md` §2 draws. They qualify work entering
Architecture; they do not replace any gate or become new A.L.C.H.E.M.Y.
letters.

Routing rules:

1. **Resume, do not restart.** Reuse the latest trustworthy hand-off artifact.
   An artifact is trustworthy only when every decision in it names what it
   supersedes and each predecessor is retired or marked lapsing; otherwise run
   the `requirements-topology` lineage check before resuming. Re-entry begins
   at the earliest failed decision.
2. **Ground conditionally.** Route a new or stale ungrounded request through
   `requirements-grounding`. Route current grounded requirements directly to M.
3. **M owns worth.** Grounding validates evidence and meaning and may supply
   linked outcome hypotheses as value evidence; M alone issues the worth
   verdict.
4. **Topology is conditional.** Use `requirements-topology` when multiple
   requirements have prerequisites, constraints, conflicts, shared foundations,
   or non-trivial sequencing. Skip it for one bounded independent requirement
   and record that rationale.
5. **Readiness guards Architecture.** Only `READY`, or `PARTLY-READY` as a
   bounded reversible increment whose unresolved requirements cannot change its
   meaning or verification, may enter A. `NOT-GROUNDED`, `BLOCKED`, and
   `NOT-READY` stop or return to the named failed stage.
6. **Keep graphs distinct.** Requirements topology models requirement
   relationships. Morphogenetic Architecture places implementation subsystems
   and compares declared topology with observed coupling fields.
7. **Keep the solid path acyclic.** Rework is explicit:
   `PROVISIONAL → grounding`, `NEEDS-REFACTOR/BLOCKED → grounding`,
   `NOT-READY → grounding`, `C redesign → A`, and the bounded topology
   handshake `L candidate → C measurement → L acceptance`.

Decision hand-offs:

| Stage | Passing decisions | Blocking decisions | Required hand-off |
|:--|:--|:--|:--|
| Requirements Grounding | `GROUNDED`; `PROVISIONAL` with its confirmation queue | `NOT-GROUNDED` | Grounded requirements, linked outcome hypotheses when relevant, evidence, assumptions, confirmation queue |
| M — Minimum | `BUILD`, `BUILD-minimal`, `KEEP`, `SIMPLIFY`, `QUARANTINE` | `NEGOTIATE`, `DEFER`, `DROP`, `DEPRECATE`, `DELETE`, `OBSOLETE` | Functionality/complexity decision per candidate |
| Requirements Topology | `STABLE` | `NEEDS-REFACTOR`, `BLOCKED` | Atomic typed graph, stable IDs, conflicts, dependency order |
| Implementation Readiness | `READY`, bounded `PARTLY-READY` | `NOT-READY` | Smallest coherent increment, verification obligations, blockers |

Walk the stages in this order and load each one only when the route reaches
it. A blocking decision ends the route for its candidate, and the stages after
it stay unloaded (`SKILL.md` §4). `PROVISIONAL` passes with its confirmation
queue, and Readiness decides whether the unconfirmed requirements can change
the increment (rule 5); a confirmation that contradicts it reopens grounding
(`PROVISIONAL → grounding`).

After an increment passes readiness and enters architecture/implementation, use
`requirements-traceability` to connect canonical IDs to implementation and
executed completion and outcome evidence. Traceability, Test Strategy, and
Evolutionary Database Design are follow-through or companions, never a
qualification stage, A.L.C.H.E.M.Y. gate, acronym letter, or prerequisite for A.

When current outcome evidence reaches a revisit trigger, route the bounded
functionality back to M in Retrospective mode. This is a new worth decision over
new evidence, not a backward pipeline edge or permission to rerun every gate.
Grounding still owns hypothesis meaning; Traceability owns evidence state and
freshness; M alone owns the worth verdict.

When verification design is material and architecture can change the evidence
boundary, use `test-strategy` as a two-pass task-matched companion:

```text
Implementation Readiness
→ Test Strategy — Obligation pass
→ A → L/C → E, as justified
→ Test Strategy — Portfolio pass
→ H
```

The Obligation pass defines risks, failure modes, oracles, and required
confidence before A. The Portfolio pass consumes final accepted architecture
and enforcement to finalize technique, scope, fidelity, dependencies, data,
environment, and stimulus before H. Collapse them into a Combined pass only
for stable accepted architecture. Gate H still owns the earliest capable
stage, CI/CD owns pipeline execution triggers and gating, and traceability owns
executed-evidence state.

When an admitted increment changes persisted or serialized data shape — a schema,
event or message payload, API body, or file format — use
`evolutionary-database-design` as a two-pass task-matched companion:

```text
Implementation Readiness
→ Evolutionary Database Design — Compatibility pass
→ A → L/C → E, as justified
→ Evolutionary Database Design — Transition pass
→ Test Strategy — Portfolio pass, when it applies
→ H
```

The Compatibility pass inventories readers, writers, the coexistence window,
and the obligations that bind the data, classifies the change, and supplies
the data facts Gate 3 grades reversibility from before A. The Transition pass
consumes final accepted architecture to fix the staged expand/contract path,
migration increments, backfill, contract trigger, and reversal step per stage
before the Test Strategy Portfolio pass and H. Collapse them into a Combined
pass only for a stable accepted target shape. Gate 3 still owns placement and
the reversibility grade, Gate H the earliest capable stage, CI/CD the deploy
order and gating, and traceability the migration anchor. Expand and contract
never ship in one deployable, and the contract step is gated on evidence, not
a date.

For an existing project, implementation is evidence rather than intent.
Code-derived requirements remain `PROVISIONAL` until an authoritative artifact
or independent confirmation supports them.

## 2. The Gates

| # | Gate | Skill | Decision record |
|:--|:--|:--|:--|
| 1 | Necessity check | `functionality-complexity-tradeoff` | BUILD / KEEP / SIMPLIFY or stop per candidate |
| 2 | First principles | `architecture-guidelines` | Smallest correct design |
| 3 | Morphogenetic topology | `morphogenetic-architecture` | Rapid/Full mode + declared Domain / tier / layer + final decision, or one restructuring candidate requiring measurement; probation expiry, instrumentation task, and prediction recheck ride the decision trail to Gate 6 |
| 4 | Complexity measurement | `structural-simplification` | Subsystem-kinds Δ, Dependency-edges Δ, Max-chain-depth Δ, Subsystem-count Δ; then Gate 3 acceptance when restructuring |
| 5 | Architecture as code | `architecture-as-code` (pattern); `-javascript` / `-python` (impl) | Per-subsystem architecture config |
| 6 | Shift defect detection left | `defect-shift-left` | Each error path → earliest catchable stage |
| 7 | Optimize value stream | `system-optimization` | Constraint analysis (iteration 2: the iteration after the increment ships, from its stable, measured baseline) |

### Gate 3–4 topology handshake

Gate 3 starts in Rapid for bounded placement and static-edge checks, then
escalates to Full for restructuring, multi-field evidence, broad scope,
ambiguity, or an explicit deep audit. Preserve the skill's `Analysis mode` and
`Selection reason` in the combined trail. A request for `rapid` or `quick`
cannot bypass a required `Rapid → Full` escalation. Gate 3 `Full` is a local
analysis mode; Alchemy `FULL` is a traversal dispatch and does not override the
Gate 3 selector.

Gate 3 is final on its first pass for `PLACE`, `KEEP`,
`DECLARE-RUNTIME-CYCLE`, and a `DEFER` that contains no restructuring
candidate. A proposed `MOVE`, `SPLIT`, `MERGE`, or `INTRODUCE-BOUNDARY` first
emits a provisional `DEFER` with one named candidate and the measurement
required from Gate 4. Run the bounded handshake
`L candidate → C measurement → L acceptance`: Gate 4 reports the four
structural deltas, then Gate 3 re-enters once for that unchanged candidate and
emits the final topology decision.

Gate E remains blocked until Gate 3 records final acceptance. If Gate 4 rejects
or redesigns the candidate, return to Gate A; a changed candidate starts a new
bounded handshake. The Alchemy orchestrator owns the re-entry, the combined
decision trail records both passes, and one candidate may re-enter Gate 3 only
once. That single re-entry bounds the measurement handshake alone: a
Close-the-Loop revisit after a prediction window or probation expiry closes
re-enters Gate 3 as a new bounded audit, and a probationary acceptance's
expiry, instrumentation task, and prediction recheck travel in the combined
decision trail to Gate 6, which places the standing check.

### Core directives

1. Order matters. Qualification and Gates 1-4 shape the design; Gates 5-6
   enforce it. Never run Gate 5 before a passing readiness decision in a full
   pass, or before final Gate 3 acceptance when a topology restructuring uses
   the Gate 3–4 handshake.
2. Name the second instance before writing an abstraction. Rule of 3 is the
   null hypothesis. If absent, DROP.
3. Ship the architecture rules with the code they govern. Follow-up PRs to
   "add the rules" are drift.
4. Defer Gate 7 to iteration 2 — the iteration after the increment ships,
   starting from its stable, measured baseline — unless the request is
   explicitly about an existing bottleneck.
5. Audit starts at `C₀`, conditionally recovers intent, then resumes the
   qualification phase and remaining gates from the earliest failed decision.
6. Before deleting either of two duplicate implementations, inventory their
   divergences and invariants, then run the same conformance cases against every
   adapter. Backend-specific tests or a fake that repeats one adapter's
   assumptions do not prove equivalence.
7. When verification design is material, preserve the Test Strategy two-pass
   handshake. Architecture may refine the portfolio but must not silently erase
   an admitted risk or oracle.
8. When an increment changes persisted or serialized data shape, preserve the
   Evolutionary Database Design two-pass handshake. Expand and contract never
   ship in one deployable; the contract step is gated on evidence, not a date.

## 3. Pre-Flight Checklist

```
- [ ] Qualification — Current grounded requirements with predecessors retired,
                      or grounding decision
- [ ] Outcomes — Linked outcome hypotheses when decision-relevant, kept separate
                 from completion criteria; authoritative obligations may be N/A
- [ ] Gate 1 — Necessity check on every proposed type/method/parameter
            For each abstraction: name the second concrete instance.
- [ ] Topology — Typed graph when relationships are non-trivial, or recorded skip
- [ ] Readiness — READY or bounded reversible PARTLY-READY before Architecture
- [ ] Aspects — every aspect the increment touches is covered or explicitly open
               (readiness matrix)
- [ ] Test strategy — Obligation pass before A: risks, failure modes, oracles,
                       and required confidence
- [ ] Data shape — Compatibility pass before A: readers, writers, coexistence
                    window, obligations, change class, and compatibility mode
- [ ] Gate 2 — Smallest correct design (SoC + SRP + DI; pure core, I/O at edges)
- [ ] Gate 3 — Rapid/Full mode and selection reason recorded; each subsystem placed at Domain / Tier / Layer; allowed edges and observed fields recorded
- [ ] Gate 4 — Subsystem-kinds / Dependency-edges / Max-chain-depth / Subsystem-count Δ computed for design vs status quo
- [ ] Gate 3 acceptance — MOVE / SPLIT / MERGE / INTRODUCE-BOUNDARY re-entered
                              once with Gate 4 measurement; final decision recorded
- [ ] Gate 5 — architecture rules in the SAME PR as the code
- [ ] Data shape — Transition pass after final A/L/C/E and before the Test
                    strategy Portfolio pass: staged path, migration increments,
                    backfill, contract trigger, and reversal step per stage
- [ ] Test strategy — Portfolio pass after final A/L/C/E and before H: technique,
                       scope, fidelity, dependencies, data, environment, stimulus
- [ ] Gate 6 — Every error path mapped to earliest catchable stage
- [ ] Gate 7 — Deferred to iteration 2 (after the increment ships, from its
            stable, measured baseline)
- [ ] Follow-through — When implementation is in scope, hand admitted IDs and
                       completion and outcome-evidence obligations to
                       requirements-traceability
- [ ] Trail — Evidence, skipped-stage rationales, first blocker, and next action
```

## 4. Retrospective Mode

Auditing existing code starts with `C₀`, a read-only structural baseline. `C₀`
is the existing retrospective complexity scan, not a new permanent gate. Use
requirements recovery only when current intent is missing, stale,
contradictory, or disputed:

| Step | Skill | Action |
|:--|:--|:--|
| 1 — `C₀` | `structural-simplification` | Score current Subsystem-kinds / Dependency-edges / Max-chain-depth / Subsystem-count — expose hot-spots and bound recovery |
| 2 — conditional recovery | `requirements-grounding` | Recover provisional, evidence-linked intent only when trustworthy current requirements are absent |
| 3 | `functionality-complexity-tradeoff` | Run the retrospective necessity decision on the bounded functionality |
| 4 — conditional topology | `requirements-topology` | Structure remediation requirements when relationships are non-trivial |
| 5 — conditional readiness | `implementation-readiness` | Identify the smallest coherent remediation increment that may enter Architecture |
| 6 | Remaining A.L.C.H.E.M.Y. gates | Redesign, enforce, and shift left only as the remediation requires |

## 5. Recurring Failure Modes

`SKILL.md` links the full symptom table. Two symptoms recur often enough to
stay on this path: a capability shipped or acceptance passed is reported as
outcome success (Requirements Grounding skipped; separate completion evidence
from the linked outcome hypothesis and measure impact after representative
use), and stale or inconclusive outcome evidence silently justifies KEEP or
DROP (refresh or bound the evidence in `requirements-traceability`, then rerun
only M in Retrospective mode).
