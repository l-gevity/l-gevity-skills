---
name: alchemy
description: >-
    Orchestrates non-trivial design, refactor, and audit work through adaptive
    requirements qualification and the A.L.C.H.E.M.Y. gates. Invoke with
    `/alchemy` in Claude Code or `$alchemy` in Codex. Use for architecture,
    complexity, enforcement, shift-left, or optimization reviews; introducing a
    module, service, or library; implementing a vertical slice across transport,
    domain, and persistence; consolidating duplicate implementations; designing
    an abstraction; extracting a package or component; refactoring across
    boundaries; or auditing over-engineering. Use `/alchemy left`, `/alchemy
    out`, and `/alchemy down` to shift defects left, push toil out, or bring
    bespoke code down into reusable capability. Use `/alchemy ?` or `$alchemy ?`
    for help. Skip local bug fixes, content or CSS edits, dependency bumps, and
    trivial renames. Defines no new rules; routes to sibling skills.
---

# Alchemy

Command entrypoint for the adaptive A.L.C.H.E.M.Y. gate system. Requirements
qualification spans the Minimum gate without adding letters to the acronym.
Keep the default response terse: resume from the latest trustworthy decision,
route to the smallest useful stage set, state the verdict, and name the next
action.

## 1. Command Grammar

Invoke as `/alchemy` in Claude Code or `$alchemy` in Codex.

Request context:

- Treat the current user prompt or invocation arguments as the subject.
- In environments that expand command arguments, `$ARGUMENTS` is the argument
  string. If `$ARGUMENTS` is empty or appears literally unexpanded, use the
  surrounding user request text instead.

If the argument is empty, `?`, `help`, or `--help`, return only this help:

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
| `alchemy audit ...` | Start with the read-only `C₀` structural baseline; recover requirements only when intent is missing, stale, contradictory, or disputed. |
| `alchemy full ...`, `alchemy all ...`, `alchemy walk the gates ...`, `alchemy complete alchemy ...` | Traverse every justified qualification stage and gate; record why any conditional stage is skipped. |
| `alchemy M ...`, `alchemy minimum ...`, `alchemy necessity ...`, `alchemy worth ...` | Invoke `functionality-complexity-tradeoff`. |
| `alchemy A ...`, `alchemy architecture ...`, `alchemy first-principles ...` | Invoke `architecture-guidelines`. |
| `alchemy L ...`, `alchemy locality ...`, `alchemy placement ...` | Invoke `geometric-architecture`. |
| `alchemy C ...`, `alchemy complexity ...`, `alchemy simplify ...` | Invoke `structural-simplification`. |
| `alchemy E ...`, `alchemy enforcement ...`, `alchemy architecture-as-code ...` | Invoke `architecture-as-code`; add `-javascript` or `-python` when the stack is known. |
| `alchemy H ...`, `alchemy hermetic ...`, `alchemy shift-left ...` | Invoke `defect-shift-left`; add `ci-cd-reliability-architecture` for pipeline reliability. |
| `alchemy Y ...`, `alchemy yield ...`, `alchemy optimize ...` | Invoke `system-optimization`. |
| `alchemy left ...` | Invoke `defect-shift-left`. |
| `alchemy out ...`, `alchemy push-out ...` | Invoke `push-out`. |
| `alchemy down ...`, `alchemy bring-down ...` | Invoke `bring-down`. |

Gate and triad aliases are authoritative. If an alias is present, use only that
gate or triad move, even when the subject mentions module boundaries. Expand
beyond the selected route only when the user explicitly asks for `full`, `all`,
`audit`, `walk the gates`, or `complete alchemy`.

If no gate alias is present, infer Design, Refactor, or Audit mode and run only
the relevant gates.

Do not run every gate by default. Expand to the full sequence only when the
request is non-trivial, crosses module boundaries, or explicitly asks for a full
alchemy pass.

Focused aliases never silently run requirements qualification. If a focused
gate lacks a prerequisite, report the missing decision artifact and stop at that
gate unless the user asked for a broader pass.

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
   Re-entry begins at the earliest failed decision.
2. **Ground conditionally.** Route a new or stale ungrounded request through
   `requirements-grounding`. Route current grounded requirements directly to M.
3. **M owns worth.** Grounding validates evidence and meaning; M alone decides
   `BUILD`, `KEEP`, `SIMPLIFY`, `DEFER`, `DROP`, or `OBSOLETE`.
4. **Topology is conditional.** Use `requirements-topology` when multiple
   requirements have prerequisites, constraints, conflicts, shared foundations,
   or non-trivial sequencing. Skip it for one bounded independent requirement
   and record that rationale.
5. **Readiness guards Architecture.** Only `READY`, or `PARTLY-READY` as a
   bounded reversible slice whose unresolved requirements cannot change its
   meaning or verification, may enter A. `NOT-GROUNDED`, `BLOCKED`, and
   `NOT-READY` stop or return to the named failed stage.
6. **Keep graphs distinct.** Requirements topology models requirement
   relationships. Geometric Architecture places implementation components.
7. **Keep the solid path acyclic.** Rework is explicit:
   `PROVISIONAL → grounding`, `NEEDS-REFACTOR/BLOCKED → grounding`,
   `NOT-READY → grounding`, and `C redesign → A`.

Decision hand-offs:

| Stage | Passing decisions | Blocking decisions | Required hand-off |
|:--|:--|:--|:--|
| Requirements Grounding | `GROUNDED` | `PROVISIONAL`, `NOT-GROUNDED` | Grounded requirements, evidence, assumptions, confirmation queue |
| M — Minimum | `BUILD`, `KEEP`, `SIMPLIFY` | `DEFER`, `DROP`, `OBSOLETE` | Functionality/complexity decision per candidate |
| Requirements Topology | `STABLE` | `NEEDS-REFACTOR`, `BLOCKED` | Atomic typed graph, stable IDs, conflicts, dependency order |
| Implementation Readiness | `READY`, bounded `PARTLY-READY` | `NOT-READY` | Smallest coherent slice, verification obligations, blockers |

After a slice passes readiness and enters architecture/implementation, use
`requirements-traceability` to connect canonical IDs to implementation and
executed evidence. Traceability is implementation follow-through, not another
qualification stage, A.L.C.H.E.M.Y. gate, acronym letter, or prerequisite for A.

For an existing project, implementation is evidence rather than intent.
Code-derived requirements remain `PROVISIONAL` until an authoritative artifact
or independent confirmation supports them.

---

## 3. The Gates

| # | Gate | Skill | Decision record |
|:--|:--|:--|:--|
| 1 | Necessity check | `functionality-complexity-tradeoff` | BUILD / KEEP / SIMPLIFY or stop per candidate |
| 2 | First principles | `architecture-guidelines` | Smallest correct design |
| 3 | Geometric placement | `geometric-architecture` | Domain / tier / layer per component + allowed dependency edges |
| 4 | Complexity measurement | `structural-simplification` | Component-kinds Δ, Dependency-edges Δ, Max-chain-depth Δ, Module-count Δ |
| 5 | Architecture as code | `architecture-as-code` (pattern); `-javascript` / `-python` (impl) | Per-module architecture config |
| 6 | Shift defect detection left | `defect-shift-left` | Each error path → earliest catchable stage |
| 7 | Optimize value stream | `system-optimization` | Constraint analysis (deferred to iter 2) |

For each qualification stage or gate selected, read the sibling skill's
`SKILL.md` and follow its procedure and output contract. This file does not
duplicate that content.

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
   pass.
2. Name the second instance before writing an abstraction. Rule of 3 is the
   null hypothesis. If absent, DROP.
3. Ship `eslint.architecture.mjs` with the code it governs. Follow-up PRs to
   "add the rules" are drift.
4. Defer Gate 7 to iteration 2 unless the request is explicitly about an
   existing bottleneck.
5. Audit starts at `C₀`, conditionally recovers intent, then resumes the
   qualification phase and remaining gates from the earliest failed decision.
6. Before deleting either of two duplicate implementations, inventory their
   divergences and invariants, then run the same conformance cases against every
   adapter. Backend-specific tests or a fake that repeats one adapter's
   assumptions do not prove equivalence.

---

## 4. Pre-Flight Checklist

```
- [ ] Qualification — Current grounded requirements, or grounding decision
- [ ] Gate 1 — Necessity check on every proposed type/method/parameter
            For each abstraction: name the second concrete instance.
- [ ] Topology — Typed graph when relationships are non-trivial, or recorded skip
- [ ] Readiness — READY or bounded reversible PARTLY-READY before Architecture
- [ ] Gate 2 — Smallest correct design (SoC + SRP + DI; pure core, I/O at edges)
- [ ] Gate 3 — Each component placed at Domain / Tier / Layer; allowed dependency edges drawn
- [ ] Gate 4 — Component-kinds / Dependency-edges / Max-chain-depth / Module-count Δ computed for design vs status quo
- [ ] Gate 5 — eslint.architecture.mjs in the SAME PR as the code
- [ ] Gate 6 — Every error path mapped to earliest catchable stage
- [ ] Gate 7 — Deferred to iteration 2
- [ ] Follow-through — When implementation is in scope, hand admitted IDs and
                       evidence obligations to requirements-traceability
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
| 1 — `C₀` | `structural-simplification` | Score current Component-kinds / Dependency-edges / Max-chain-depth / Module-count — expose hot-spots and bound recovery |
| 2 — conditional recovery | `requirements-grounding` | Recover provisional, evidence-linked intent only when trustworthy current requirements are absent |
| 3 | `functionality-complexity-tradeoff` | Run the retrospective necessity decision on the bounded functionality |
| 4 — conditional topology | `requirements-topology` | Structure remediation requirements when relationships are non-trivial |
| 5 — conditional readiness | `implementation-readiness` | Identify the smallest coherent remediation slice that may enter Architecture |
| 6 | Remaining A.L.C.H.E.M.Y. gates | Redesign, enforce, and shift left only as the remediation requires |

---

## 6. Failure-Mode Diagnostics

| Symptom | Skipped gate | Recovery |
|:--|:--|:--|
| Architecture starts from an assumed or stale problem | Requirements Grounding | Stop; source or confirm actor, problem, scope, and completion evidence |
| Requirement order is prose-only, cyclic, or contradictory | Requirements Topology | Build the typed graph; return blocking conflicts or cycles to grounding |
| Architecture invents meaning, permissions, data, or acceptance criteria | Implementation Readiness | Stop at `NOT-READY`; resolve the named product or policy blocker |
| `PARTLY-READY` work can be invalidated by an unresolved requirement | Implementation Readiness | Reject the slice; admit only bounded reversible work |
| Interface added "for the second implementation" but second never lands | 1 — Rule of 3 | Run pruner; collapse to one concrete |
| Generic registry / plugin system with one entry | 1 — generality without instantiation | Inline the entry; remove the registry |
| Empty config / config with one value across all envs | 1 — one-value config | Inline the value |
| `if (impossible_state)` runtime guards | 1 — impossible-state guard | OBSOLETE; document the invariant elsewhere |
| Cross-domain imports across non-adjacent faces | 3 — placement violated | Move the component or extract a face-adjacent shim |
| Refactor "felt simpler" but no measurement | 4 — complexity not scored | Compute Component-kinds / Dependency-edges / Max-chain-depth / Module-count Δ before merging |
| Eslint rules added in follow-up PR | 5 — same-PR discipline broken | Block the follow-up; add rules to original PR |
| Defects caught at runtime that types could express | 6 — left-shift not applied | Move the check upward; remove the runtime guard |
| Architecture file disagrees with code | 5 — drift | Re-run lint; treat as a defect |
| Requirement marked verified from a code anchor or unexecuted test | Implementation follow-through | Run `requirements-traceability`; separate implemented from verified evidence |
| Duplicate implementations are unified but retain separate behavior tests | 6 — integration / contract | Add one shared conformance suite and real-boundary coverage for backend-specific semantics before deleting either copy |
| "Just in case" extension point with one user | 1 — speculative optionality | DROP unless second use is named and probable |
| Premature performance optimization | 7 — applied before baseline | Revert; re-apply after stability |

---

## 7. Output Contract

Default output for a single-gate or simple routed request:

```
Route:    <M | A | L | C | E | H | Y | left | out | down>
Verdict:  Proceed | Redesign | Drop | Defer
Reason:   <one or two lines>
Next:     <one concrete action>
```

Use the expanded output only for multi-stage runs, non-trivial design/refactor
passes, audits, or explicit requests for detail. Emit one combined decision
trail in execution order. Include every stage used and every conditional stage
skipped; a skip without a rationale is a defect:

| Stage | Skill | Decision | Evidence / hand-off | Files/checks | Next action or skip rationale |
| ----- | ----- | -------- | ------------------- | ------------ | ----------------------------- |

Then state:

```
Scope:          <module / service / refactor / PR>
Mode:           Design | Refactor | Audit
Blocking stage: <first non-passing qualification decision or gate, or None>
Decision:       Proceed | Redesign | Reject | Defer
Verification:   <commands, lint rules, tests, or Not run + reason>
```

If implementing changes, include the normal coding summary after the alchemy
verdict.

## 8. Discipline

- **Skipped stages require a one-line rationale.** Skipped qualification stages
  or gates with no rationale are over-engineering risk for the next audit.
- **When a gate is consistently skipped across tasks**, that's a signal for
  `continuous-improvement` to update THIS skill — not paper over with
  case-by-case reminders.
