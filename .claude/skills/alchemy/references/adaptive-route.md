# Adaptive Route — Qualification, Gates, and Handshakes

Read before selecting stages when dispatch is `ADAPTIVE` or `FULL`, or the
alias is `audit`. `SKILL.md` owns dispatch, the stage set each dispatch
selects, aliases, companion selection, focused-gate prerequisites, and the
output contract; this file owns the route those dispatches walk, the two-pass
companion order, the execution selection, and the decision-trail format. For
each stage selected, read the sibling skill's `SKILL.md` and follow its
procedure and output contract; this file does not duplicate that content.

## 1. Adaptive Requirements Qualification

The requirements skills are conditional qualification stages around **M —
Minimum**, in the order `SKILL.md` §2 draws. They qualify work entering
Architecture and replace no gate.

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
   verdict. Hypotheses are linked when decision-relevant and kept separate
   from completion criteria, so that no capability shipped or acceptance
   passed is reported as outcome success; authoritative obligations may be
   N/A.
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
   `NOT-READY → grounding`, `C redesign → A`, and the bounded Gate 3–4
   handshake of §2.

Decision hand-offs:

| Stage | Passing decisions | Blocking decisions | Required hand-off |
|:--|:--|:--|:--|
| Requirements Grounding | `GROUNDED`; `PROVISIONAL` with its confirmation queue | `NOT-GROUNDED` | Grounded requirements, linked outcome hypotheses when relevant, evidence, assumptions, confirmation queue |
| M — Minimum | `BUILD`, `BUILD-minimal`, `KEEP`, `SIMPLIFY`, `QUARANTINE` | `NEGOTIATE`, `DEFER`, `DROP`, `DEPRECATE`, `DELETE`, `OBSOLETE` | Functionality/complexity decision per candidate |
| Requirements Topology | `STABLE` | `NEEDS-REFACTOR`, `BLOCKED` | Atomic typed graph, stable IDs, conflicts, dependency order |
| Implementation Readiness | `READY`, bounded `PARTLY-READY` | `NOT-READY` | Smallest coherent increment, verification obligations, blockers, and an aspect matrix with every aspect the increment touches covered or explicitly open |

**Load each stage when the route reaches it.** Walk the stages in this order
and read a stage's or companion pass's `SKILL.md` only once every stage before
it has passed, never ahead. A blocking decision in the route's hand-off table
ends the route for that candidate: the stages after it stay unloaded and
appear in the trail as `Not run` with that decision as the reason. Only
candidates with a passing decision continue. `PROVISIONAL` passes with its
confirmation queue, and Readiness decides whether the unconfirmed requirements
can change the increment (rule 5); a confirmation that contradicts it reopens
grounding.

After an increment passes readiness and enters architecture/implementation, use
`requirements-traceability` to connect canonical IDs to implementation and
executed completion and outcome evidence. Traceability, Test Strategy, and
Evolutionary Database Design are follow-through or companions, never a
qualification stage, A.L.C.H.E.M.Y. gate, acronym letter, or prerequisite for A.

When current outcome evidence reaches a revisit trigger, rerun only M in
Retrospective mode on the bounded functionality. This is a new worth decision
over new evidence, not a backward pipeline edge. Grounding still owns
hypothesis meaning, and Traceability owns evidence state and freshness:
refresh or bound stale or inconclusive evidence there before it justifies KEEP
or DROP.

For an existing project, implementation is evidence rather than intent.
Code-derived requirements remain `PROVISIONAL` until an authoritative artifact
or independent confirmation supports them.

## 2. The Gates

| # | Gate | Skill | Decision record |
|:--|:--|:--|:--|
| 1 | Necessity check | `functionality-complexity-tradeoff` | BUILD / KEEP / SIMPLIFY or stop per candidate, down to every proposed type, method, and parameter |
| 2 | First principles | `architecture-guidelines` | Smallest correct design (SoC + SRP + DI; pure core, I/O at edges) |
| 3 | Morphogenetic topology | `morphogenetic-architecture` | Rapid/Full mode and selection reason; each subsystem's declared Domain / tier / layer, allowed edges, and observed fields; final decision, or one restructuring candidate requiring measurement |
| 4 | Complexity measurement | `structural-simplification` | Subsystem-kinds Δ, Dependency-edges Δ, Max-chain-depth Δ, Subsystem-count Δ for the design against the status quo |
| 5 | Architecture as code | `architecture-as-code`, plus its stack reference only when rule files are written or changed | Per-subsystem constraints, in the pattern's encoding-neutral form until the stack's files are written |
| 6 | Shift defect detection left | `defect-shift-left` | Each error path → earliest catchable stage |
| 7 | Optimize value stream | `system-optimization` | Constraint analysis, or the deferral record of directive 4 |

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
structural deltas, then Gate 3 re-enters for that unchanged candidate and
emits the final topology decision. `SKILL.md` §1 holds Gate E until then.

If Gate 4 rejects or redesigns the candidate, return to Gate A; a changed
candidate starts a new bounded handshake. The Alchemy orchestrator owns the
re-entry, the combined decision trail records both passes, and one candidate
may re-enter Gate 3 only once. That single re-entry bounds the measurement
handshake alone: a Close-the-Loop revisit after a prediction window or
probation expiry closes re-enters Gate 3 as a new bounded audit, and a
probationary acceptance's expiry, instrumentation task, and prediction recheck
travel in the combined decision trail to Gate 6, which places the standing
check.

### Core directives

1. Order matters. Qualification and Gates 1-4 shape the design; Gates 5-6
   enforce it. Gate E also waits for a passing readiness decision in a full
   pass.
2. Name the second concrete instance before writing an abstraction. Rule of 3
   is the null hypothesis. If absent, DROP.
3. Ship the architecture rules in the same PR as the code they govern.
   Follow-up PRs to "add the rules" are drift.
4. Gate 7 is deferred as `SKILL.md` §1 states. The deferral names its baseline
   metric, where that metric is read, and the date or event that opens
   iteration 2; when the increment adds pipeline work or stored output, the
   metric includes what it consumes. A deferral without them never reopens.
5. Before deleting either of two duplicate implementations, inventory their
   divergences and invariants, then run the same conformance cases against every
   adapter. Backend-specific tests or a fake that repeats one adapter's
   assumptions do not prove equivalence.
6. Decomposition and aspect extraction are different cuts: decomposition
   splits one subsystem into several; extraction pulls one aspect out of
   several subsystems into one mechanism. A design that models an aspect as a
   subsystem, or copies its mechanism per subsystem, has confused the two.
   [change-primitives.md](change-primitives.md) defines the four primitives.

## 3. Two-Pass Companions

`SKILL.md` §1 selects and reports companions. Two are two-pass task-matched
companions that bracket A/L/C/E. When verification design is material and
architecture can change the evidence boundary, use `test-strategy`. When an
admitted increment changes persisted or serialized data shape — a schema,
event or message payload, API body, or file format — use
`evolutionary-database-design`. This block is the order of their passes; each
line applies only when its companion is selected:

```text
Implementation Readiness
→ Test Strategy — Obligation pass
→ Evolutionary Database Design — Compatibility pass
→ A → L/C → E, as justified
→ Evolutionary Database Design — Transition pass
→ Test Strategy — Portfolio pass
→ H
```

The Obligation pass defines risks, failure modes, oracles, and required
confidence. The Portfolio pass consumes final accepted architecture and
enforcement to finalize technique, scope, fidelity, dependencies, data,
environment, and stimulus; architecture may refine the portfolio but must not
silently erase an admitted risk or oracle. Gate H still owns the earliest
capable stage, CI/CD owns pipeline execution triggers and gating, and
traceability owns executed-evidence state.

The Compatibility pass inventories readers, writers, the coexistence window,
and the obligations that bind the data, classifies the change and its
compatibility mode, and supplies the data facts Gate 3 grades reversibility
from. The Transition pass consumes final accepted architecture to fix the
staged expand/contract path, migration increments, backfill, contract trigger,
and reversal step per stage. Gate 3 still owns placement and the reversibility
grade, CI/CD the deploy order and gating, and traceability the migration
anchor. Expand and contract never ship in one deployable, and the contract
step is gated on evidence, not a date.

Collapse a companion's passes into a Combined pass only for stable accepted
architecture (Test Strategy) or a stable accepted target shape (Evolutionary
Database Design).

## 4. Execution

Select `multi-agent` only when the work changes or audits code and at least
two parts are independent — different subsystems, disjoint files, no ordering
between them — or a high-risk change (security, public contract, persisted
shape) needs a reviewer that did not write it. Count every agent: one writer
and one independent reviewer is `multi-agent`. The number of gates or skills
on the route is never a reason. Stay `single-agent` and say why when neither
holds, when the project's `alchemy-workspace.json` sets
`execution.multi_agent` to `off`, or when the runtime cannot launch agents.
On `multi-agent`, load `alchemy-orchestrate` before the first stage that
changes or audits code; it plans, launches, verifies, and gates the agents.

## 5. Retrospective Mode

Auditing existing code starts with `C₀`, a read-only structural baseline. `C₀`
is the existing retrospective complexity scan, not a new permanent gate. Use
requirements recovery only when current intent is missing, stale,
contradictory, or disputed:

| Step | Skill | Action |
|:--|:--|:--|
| 1 — `C₀` | `structural-simplification` | Score current Subsystem-kinds / Dependency-edges / Max-chain-depth / Subsystem-count — expose hot-spots and bound recovery |
| 2 — conditional recovery | `requirements-grounding` | Recover provisional, evidence-linked intent |
| 3 | `functionality-complexity-tradeoff` | Run the retrospective necessity decision on the bounded functionality |
| 4 — conditional topology | `requirements-topology` | Structure remediation requirements when relationships are non-trivial |
| 5 — conditional readiness | `implementation-readiness` | Identify the smallest coherent remediation increment that may enter Architecture |
| 6 | Remaining A.L.C.H.E.M.Y. gates | Redesign, enforce, and shift left only as the remediation requires |

## 6. Decision Trail

`SKILL.md` §3 decides which runs emit this trail, what it lists, and what goes
before and after it; this section is its format. A skipped stage requires a
one-line rationale; a skip without one is a defect and an over-engineering
risk for the next audit.

| Stage | Skill | Decision | Evidence / hand-off | Files/checks | Next action or skip rationale |
| ----- | ----- | -------- | ------------------- | ------------ | ----------------------------- |

Then state:

```
Scope:          <subsystem / service / refactor / PR>
Mode:           Design | Refactor | Audit
Dispatch:       SKIP | DIRECT | ADAPTIVE | FULL
Companions:     <None | task-matched skills>
Execution:      single-agent | multi-agent
Blocking stage: <first non-passing qualification decision or gate, or None>
Decision:       Proceed | Redesign | Drop | Defer
Verification:   <commands, lint rules, tests, or Not run + reason>
```
