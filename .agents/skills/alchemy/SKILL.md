---
name: alchemy
description: >-
    Runs a lightweight change preflight, then routes non-trivial design,
    refactor, and audit work through only the needed requirements and
    A.L.C.H.E.M.Y. skills. Explicitly trigger with `/alchemy`, `$alchemy`, or
    natural phrases such as "do some alchemy", "run alchemy on this", "use
    alchemy", or "give this an alchemy pass". Use for architecture, complexity,
    enforcement, shift-left, optimization, subsystems, increments (vertical
    slices), abstractions, cross-boundary refactors, consolidation, and over-engineering
    audits. Explicit invocation on a local bug fix, content or CSS edit,
    dependency bump, or trivial rename returns a cheap `SKIP` or `DIRECT`
    dispatch instead of loading every gate. Defines no new domain rules; routes
    to core sibling skills and task-matched companion skills.
---

# Alchemy

Command entrypoint for the adaptive A.L.C.H.E.M.Y. gate system. Requirements
qualification spans the Minimum gate without adding letters to the acronym.
Keep the default response terse: resume from the latest trustworthy decision,
route to the smallest useful stage set, state the verdict, and name the next
action.

## 1. Command Grammar

Invoke as `/alchemy` in Claude Code or `$alchemy` in Codex. Natural language is
equivalent: `do some alchemy`, `run alchemy on this`, `use alchemy`, and `give
this an alchemy pass` all request adaptive dispatch, not a full traversal.

Request context:

- Treat the current user prompt or invocation arguments as the subject.
- In environments that expand command arguments, `$ARGUMENTS` is the argument
  string. If `$ARGUMENTS` is empty or appears literally unexpanded, use the
  surrounding user request text instead.
- When a natural phrase contains no explicit subject, use the active request or
  most recent unresolved task. Do not ask the user to restate context already
  available in the conversation or worktree.

If the argument is `?`, `help`, or `--help`, return only this help. An empty
command with no active subject also returns help; a natural phrase with active
task context runs the preflight.

```
/alchemy <subject>   | $alchemy <subject>   route through the needed gates
/alchemy audit <subject> | $alchemy audit <subject> start at the C₀ baseline
/alchemy full <subject>  | $alchemy full <subject>  traverse all justified stages
/alchemy M <subject> | $alchemy M <subject> Minimum: worth it?
/alchemy A <subject> | $alchemy A <subject> Architecture: sound design?
/alchemy L <subject> | $alchemy L <subject> Locality: where belongs?
/alchemy C <subject> | $alchemy C <subject> Complexity: simpler?
/alchemy E <subject> | $alchemy E <subject> Enforcement: rules as code?
/alchemy H <subject> | $alchemy H <subject> Hermetic: catch earlier?
/alchemy Y <subject> | $alchemy Y <subject> Yield: optimize flow?
/alchemy left <subject> | $alchemy left <subject> detect defects earlier
/alchemy out <subject>  | $alchemy out <subject> move toil out of humans
/alchemy down <subject> | $alchemy down <subject> move bespoke code down
```

| User phrase | Route |
|:--|:--|
| `alchemy <subject>` | Infer Design, Refactor, or Audit mode from context, then run the relevant gate sequence. |
| `do some alchemy`, `run/use/apply alchemy`, `give this an alchemy pass` | Use the active subject and run the dispatch preflight; never imply `full`. |
| `alchemy audit ...` | Start with the read-only `C₀` structural baseline; recover requirements only when intent is missing, stale, contradictory, or disputed. |
| `alchemy full ...`, `alchemy all ...`, `alchemy walk the gates ...`, `alchemy complete alchemy ...` | Traverse every justified qualification stage and gate; record why any conditional stage is skipped. |
| `alchemy M ...`, `alchemy minimum ...`, `alchemy necessity ...`, `alchemy worth ...` | Invoke `functionality-complexity-tradeoff`. |
| `alchemy A ...`, `alchemy architecture ...`, `alchemy first-principles ...` | Invoke `architecture-guidelines`. |
| `alchemy L ...`, `alchemy locality ...`, `alchemy placement ...` | Invoke `morphogenetic-architecture`. |
| `alchemy C ...`, `alchemy complexity ...`, `alchemy simplify ...` | Invoke `structural-simplification`. |
| `alchemy E ...`, `alchemy enforcement ...`, `alchemy architecture-as-code ...` | Invoke `architecture-as-code`; add `-javascript` or `-python` when the stack is known. |
| `alchemy H ...`, `alchemy hermetic ...`, `alchemy shift-left ...` | Invoke `defect-shift-left`; add `ci-cd-reliability-architecture` for pipeline reliability. |
| `alchemy Y ...`, `alchemy yield ...`, `alchemy optimize ...` | Invoke `system-optimization`. |
| `alchemy left ...` | Invoke `defect-shift-left`. |
| `alchemy out ...`, `alchemy push-out ...` | Invoke `push-out`. |
| `alchemy zero-copy ...`, `alchemy source-of-truth ...` | Invoke `zero-copy-requirements`. |
| `alchemy down ...`, `alchemy bring-down ...` | Invoke `bring-down`. |

### Dispatch Preflight

Classify before reading any sibling skill body. Use prompt context, current
diff/task scope, available skill metadata, and the latest trustworthy decision
artifacts only.

Make dispatch the first observable checkpoint. Decide from the user request and
already-loaded context; do not scan the repository or open sibling bodies merely
to choose a dispatch. After emitting the dispatch, inspect only the artifacts
and skills selected by that route.

| Dispatch | Select when | Core action |
|:--|:--|:--|
| `SKIP` | Local behavior stays inside one governed boundary and does not ask an Alchemy question: copy/CSS, trivial rename, routine dependency bump, or isolated bug fix | Load no Alchemy gate skill; continue with task-matched companion skills and normal verification |
| `DIRECT` | A focused alias or one unambiguous gate question maps to exactly one gate or triad skill | Load only that core sibling skill |
| `ADAPTIVE` | Structure, responsibility, data flow, abstraction, multiple requirements, or boundaries may change | Select the smallest justified qualification and gate set |
| `FULL` | The user explicitly requests `full`, `all`, `walk the gates`, or `complete alchemy` | Traverse every justified stage and record all skips |

Use this deterministic signal matrix when no alias is present:

| Change signal | Dispatch / minimum core route |
|:--|:--|
| Copy, CSS, trivial rename, routine dependency bump, isolated in-boundary fix | `SKIP` |
| Worth, dead code, speculative abstraction, or "should this exist?" | `DIRECT → M` |
| Defect found late, check placement, or CI detection timing | `DIRECT → H` or `left` |
| Structural refactor inside one boundary | `ADAPTIVE → M, C`; add A when responsibility or public contract changes, H when verification placement changes |
| New subsystem/service/library, cross-boundary dependency, increment cut through every layer (vertical slice), consolidation, or an aspect added or changed across several subsystems (auth, audit, logging, retry, i18n) | `ADAPTIVE → qualification as needed, M, A, L, C, E, H` |
| Existing-code over-engineering audit | `ADAPTIVE` Audit mode beginning at `C₀` |
| Explicit full traversal | `FULL` |

Do not convert uncertainty into `FULL`. Select the smallest plausible route,
state the uncertain signal, and stop at the first missing prerequisite.

### Companion Skill Routing

Alchemy owns the core qualification and gate route, not every task domain.
Inspect available skill metadata and project instructions, then select any
non-Alchemy skill whose trigger independently matches the subject. Read only
the selected companion skill bodies.

- A project profile may require companion skills for its domain, stack, UX,
  security, accessibility, API, release, or evidence rules.
- When the subject decides where a fact, decision, or document belongs — a
  proposed document, a decision record, an architecture note, a status page, or
  a documentation-tree audit — select `zero-copy-requirements`. It names the
  artifact that owns the question; `push-out` prunes prose already covered by an
  executable source, and `requirements-traceability` anchors evidence once the
  location exists. None of the three is a qualification stage, gate, or acronym
  letter.
- `SKIP` skips only the Alchemy core; it never suppresses a matching companion.
- `DIRECT` keeps the core route focused while allowing independently triggered
  companions.
- Report companions explicitly. Use `None` when no companion trigger matches.
- Never hard-code project-specific companion names into this generic skill.

Gate and triad aliases are authoritative. If an alias is present, use only that
core gate or triad move, even when the subject mentions subsystem boundaries.
Independently triggered companions may still apply. Expand the core route only
when the user explicitly asks for `full`, `all`, `audit`, `walk the gates`, or
`complete alchemy`.

If no gate alias is present, infer Design, Refactor, or Audit mode and run only
the relevant gates.

Do not run every gate by default. Non-trivial or cross-boundary work uses the
smallest `ADAPTIVE` route; only explicit full language selects `FULL`.

Focused aliases never silently run requirements qualification. If a focused
gate lacks a prerequisite, report the missing decision artifact and stop at that
gate unless the user asked for a broader pass.

### Change Primitives

Every stage describes change with four primitives. Each sibling skill names
its own term as a specialization of exactly one and never redefines them.
This is vocabulary, not a gate rule.

| Primitive | Definition | Named specializations |
|:--|:--|:--|
| **Subsystem** | A part produced by decomposition: the thing a position is assigned to and a rule file governs. *Where change lands.* | L places it at a position; E governs it per directory; C counts subsystems (n) and their kinds (D); `bring-down` ranks the capability it can be replaced by. Requirements skills group requirements into *capabilities*; A decides when a capability becomes a subsystem boundary, and L places it. |
| **Aspect** | A property that holds across a declared set of the units the stage knows — problem scopes at Grounding and Topology, capabilities at Readiness, subsystems from L onward; the scope → subsystem mapping is L's placement decision, never inferred upstream. One obligation (the rule) and one mechanism (the subsystem that implements it). *Which dimension is touched.* | Grounding: a requirement with `Holds across`; Topology: a `constraint` node with `holds_across` and the `Aspect coverage` check; Readiness: a row of the aspect matrix; M: the aspect-owner map; A: extracted, never interleaved; L: the mechanism's position plus `Holds across`; C: the aspect-extraction delta; E: the mechanism's exclusivity edges; H: placement of the coverage check; Test Strategy: its oracle; Traceability: the `aspect-uncovered` gap. |
| **Increment** | The bounded unit of change admitted to implementation; it adds, changes, or removes cells of the subsystem × aspect matrix. *What changes.* | Readiness admits it — a *vertical increment* realizes one outcome end to end through every layer it crosses; `evolutionary-database-design`: a *migration increment* per stage; `system-optimization`: a *batch* is the set of increments moved together; CI/CD: the *candidate artifact* is its built form. |
| **Iteration** | One cycle that admits an increment, realizes it, and measures the resulting baseline: completion evidence plus the structural and flow measurements later windows compare against. Prediction windows, outcome-evidence windows, and revisit triggers are carried across iterations and close on their own trigger, re-entering L or M as a new bounded decision. "Iteration 2" is the next iteration on the same subject, *starting from that measured baseline*. | Completion evidence closes an iteration (`requirements-traceability`); outcome evidence does not. Y optimizes only a stable, measured baseline, so it *runs in the iteration after the increment ships*. A PDCA or DMAIC turn in `system-optimization` is an iteration whose Check or Control step is the measurement. |

Decomposition and aspect extraction are different cuts. Decomposition splits
one subsystem into several; extraction pulls one aspect out of several
subsystems into one mechanism. A design that models an aspect as a subsystem,
or copies its mechanism per subsystem, has confused the two.

---

## 2. Adaptive Requirements Qualification

The requirements skills are conditional qualification stages around **M —
Minimum**. They qualify work entering Architecture; they do not replace any
gate or become new A.L.C.H.E.M.Y. letters.

```text
Requirements Grounding, when evidence or meaning is absent or stale
→ M — Minimum
→ Requirements Topology, when relationships are non-trivial
→ Implementation Readiness
→ A — Architecture
```

Routing rules:

1. **Resume, do not restart.** Reuse the latest trustworthy hand-off artifact.
   An artifact is trustworthy only when every decision in it names what it
   supersedes and each predecessor is retired or marked lapsing; otherwise run
   the `requirements-topology` lineage check before resuming. Re-entry begins
   at the earliest failed decision.
2. **Ground conditionally.** Route a new or stale ungrounded request through
   `requirements-grounding`. Route current grounded requirements directly to M.
3. **M owns worth.** Grounding validates evidence and meaning and may supply
   linked outcome hypotheses as value evidence; M alone decides `BUILD`,
   `KEEP`, `SIMPLIFY`, `DEFER`, `DROP`, or `OBSOLETE`.
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
| Requirements Grounding | `GROUNDED` | `PROVISIONAL`, `NOT-GROUNDED` | Grounded requirements, linked outcome hypotheses when relevant, evidence, assumptions, confirmation queue |
| M — Minimum | `BUILD`, `KEEP`, `SIMPLIFY` | `DEFER`, `DROP`, `OBSOLETE` | Functionality/complexity decision per candidate |
| Requirements Topology | `STABLE` | `NEEDS-REFACTOR`, `BLOCKED` | Atomic typed graph, stable IDs, conflicts, dependency order |
| Implementation Readiness | `READY`, bounded `PARTLY-READY` | `NOT-READY` | Smallest coherent increment, verification obligations, blockers |

After an increment passes readiness and enters architecture/implementation, use
`requirements-traceability` to connect canonical IDs to implementation and
executed completion and outcome evidence. Traceability is implementation
follow-through, not another qualification stage, A.L.C.H.E.M.Y. gate, acronym
letter, or prerequisite for A.

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
executed-evidence state. Test Strategy is not a qualification stage,
A.L.C.H.E.M.Y. gate, acronym letter, or prerequisite for A.

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
a date. Evolutionary Database Design is not a qualification stage,
A.L.C.H.E.M.Y. gate, acronym letter, or prerequisite for A.

For an existing project, implementation is evidence rather than intent.
Code-derived requirements remain `PROVISIONAL` until an authoritative artifact
or independent confirmation supports them.

---

## 3. The Gates

| # | Gate | Skill | Decision record |
|:--|:--|:--|:--|
| 1 | Necessity check | `functionality-complexity-tradeoff` | BUILD / KEEP / SIMPLIFY or stop per candidate |
| 2 | First principles | `architecture-guidelines` | Smallest correct design |
| 3 | Morphogenetic topology | `morphogenetic-architecture` | Rapid/Full mode + declared Domain / tier / layer + final decision, or one restructuring candidate requiring measurement; probation expiry, instrumentation task, and prediction recheck ride the decision trail to Gate 6 |
| 4 | Complexity measurement | `structural-simplification` | Subsystem-kinds Δ, Dependency-edges Δ, Max-chain-depth Δ, Subsystem-count Δ; then Gate 3 acceptance when restructuring |
| 5 | Architecture as code | `architecture-as-code` (pattern); `-javascript` / `-python` (impl) | Per-subsystem architecture config |
| 6 | Shift defect detection left | `defect-shift-left` | Each error path → earliest catchable stage |
| 7 | Optimize value stream | `system-optimization` | Constraint analysis (iteration 2: the iteration after the increment ships, from its stable, measured baseline) |

For each qualification stage or gate selected, read the sibling skill's
`SKILL.md` and follow its procedure and output contract. This file does not
duplicate that content.

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

DevOps improvement triad:

| Command | Skill | Use when |
|:--|:--|:--|
| `left` | `defect-shift-left` | Defects are found too late; move detection to the earliest capable stage. |
| `out` | `push-out` | Recurring operational work lives in human memory, tickets, or local team practice. |
| `down` | `bring-down` | Bespoke, duplicated, or over-local code should move into reusable capability. |

The triad is not part of the core seven-gate sequence. Run it directly when the
user names a triad move. During `/alchemy Y`, recommend `out` or `down` when
the bottleneck is manual toil or bespoke implementation, but do not run them
unless the user asks.

Core directives:

1. Order matters. Qualification and Gates 1-4 shape the design; Gates 5-6
   enforce it. Never run Gate 5 before a passing readiness decision in a full
   pass, or before final Gate 3 acceptance when a topology restructuring uses
   the Gate 3–4 handshake.
2. Name the second instance before writing an abstraction. Rule of 3 is the
   null hypothesis. If absent, DROP.
3. Ship `eslint.architecture.mjs` with the code it governs. Follow-up PRs to
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

---

## 4. Pre-Flight Checklist

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
- [ ] Gate 5 — eslint.architecture.mjs in the SAME PR as the code
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

---

## 5. Retrospective Mode

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

---

## 6. Failure-Mode Diagnostics

A symptom, skipped gate, and recovery table for a run whose result looks
wrong, an audit of existing code, or a decision trail with an unexplained skip.
Read [references/failure-modes.md](references/failure-modes.md) when a subject
shows one of its symptoms, then route the recovery to the named stage instead
of rerunning every gate. Two symptoms recur often enough to stay here: a
capability shipped or acceptance passed is reported as outcome success
(Requirements Grounding skipped; separate completion evidence from the linked
outcome hypothesis and measure impact after representative use), and stale or
inconclusive outcome evidence silently justifies KEEP or DROP (refresh or bound
the evidence in `requirements-traceability`, then rerun only M in Retrospective
mode).

---

## 7. Output Contract

Default output for a single-gate or simple routed request:

```
Dispatch:   <SKIP | DIRECT | ADAPTIVE | FULL>
Core route: <None | M | A | L | C | E | H | Y | left | out | down | ordered set>
Companions: <None | task-matched skills>
Verdict:    Proceed | Redesign | Drop | Defer
Reason:     <one or two lines>
Next:       <one concrete action>
```

For `SKIP`, emit the same compact output with `Core route: None`; do not load a
core sibling merely to justify the skip.

Use the expanded output only for multi-stage runs, non-trivial design/refactor
passes, audits, or explicit requests for detail. Emit one combined decision
trail in execution order. Include every stage used and every conditional stage
skipped; a skip without a rationale is a defect:

| Stage | Skill | Decision | Evidence / hand-off | Files/checks | Next action or skip rationale |
| ----- | ----- | -------- | ------------------- | ------------ | ----------------------------- |

Then state:

```
Scope:          <subsystem / service / refactor / PR>
Mode:           Design | Refactor | Audit
Dispatch:       SKIP | DIRECT | ADAPTIVE | FULL
Companions:     <None | task-matched skills>
Blocking stage: <first non-passing qualification decision or gate, or None>
Decision:       Proceed | Redesign | Reject | Defer
Verification:   <commands, lint rules, tests, or Not run + reason>
```

If implementing changes, include the normal coding summary after the alchemy
verdict.

Lead any run that reaches a verdict with the four report blocks the root
instruction file defines, What I found, Why it matters, Do this first, and
What I did not check, then emit the records unchanged. `SKIP` emits the compact
output alone.

## 8. Discipline

- **Skipped stages require a one-line rationale.** Skipped qualification stages
  or gates with no rationale are over-engineering risk for the next audit.
- **Dispatch before loading.** `SKIP` must be decidable from task context and
  metadata; reading every sibling before skipping defeats the preflight.
- **Dispatch before inspecting.** Emit the route before substantive repository
  discovery; inspection begins only after the route bounds what to read.
- **Natural language stays adaptive.** "Do some alchemy" never means `FULL`
  without explicit full-traversal language.
- **Companions remain independent.** A core skip or focused alias must not hide
  a task-matched domain, stack, security, UX, accessibility, or evidence skill.
- **When a gate is consistently skipped across tasks**, that's a signal for
  `continuous-improvement` to update THIS skill — not paper over with
  case-by-case reminders.
