---
name: alchemy
description: >-
    Orchestrates non-trivial design and refactor work through the A.L.C.H.E.M.Y.
    gates in execution order: necessity, first principles, placement,
    complexity, enforcement, shift-left, and optimization. Invoke with
    `/alchemy` in Claude Code or `$alchemy` in Codex. Use for a design, feature,
    refactor, module, service, abstraction, architecture, complexity,
    enforcement, shift-left, or optimization review; when introducing a module,
    service, or library; designing an abstraction; extracting a package or
    component; refactoring across boundaries; or auditing over-engineering.
    Use `/alchemy left`, `/alchemy out`, and `/alchemy down` for the DevOps
    improvement triad: shift defects left, push toil out, and bring bespoke code
    down into reusable capability. Use `/alchemy ?` or `$alchemy ?` for command
    help. Skip for local bug fixes, content or CSS edits, dependency bumps, and
    trivial renames. Defines no new rules; routes to sibling skills.
---

# Alchemy

Command entrypoint for the A.L.C.H.E.M.Y. gate system. Keep the default
response terse: route to the smallest useful gate set, state the verdict, and
name the next action.

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

---

## 2. The Gates

| # | Gate | Skill | Decision record |
|:--|:--|:--|:--|
| 1 | Necessity check | `functionality-complexity-tradeoff` | PASS / DROP per type, method, parameter |
| 2 | First principles | `architecture-guidelines` | Smallest correct design |
| 3 | Geometric placement | `geometric-architecture` | Domain / tier / layer per component + allowed dependency edges |
| 4 | Complexity measurement | `structural-simplification` | Component-kinds Δ, Dependency-edges Δ, Max-chain-depth Δ, Module-count Δ |
| 5 | Architecture as code | `architecture-as-code` (pattern); `-javascript` / `-python` (impl) | Per-module architecture config |
| 6 | Shift defect detection left | `defect-shift-left` | Each error path → earliest catchable stage |
| 7 | Optimize value stream | `system-optimization` | Constraint analysis (deferred to iter 2) |

For each gate selected, read the sibling skill's `SKILL.md` and follow its
procedure and output contract. This file does not duplicate that content.

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

1. Order matters. Gates 1-4 shape the design; Gates 5-6 enforce it. Never run
   Gate 5 before Gate 1 in a full pass.
2. Name the second instance before writing an abstraction. Rule of 3 is the
   null hypothesis. If absent, DROP.
3. Ship `eslint.architecture.mjs` with the code it governs. Follow-up PRs to
   "add the rules" are drift.
4. Defer Gate 7 to iteration 2 unless the request is explicitly about an
   existing bottleneck.
5. Audit reverses the order: Gate 4 -> Gate 1 first, then enforcement and
   shift-left checks.

---

## 3. Pre-Flight Checklist

```
- [ ] Gate 1 — Necessity check on every proposed type/method/parameter
            For each abstraction: name the second concrete instance.
- [ ] Gate 2 — Smallest correct design (SoC + SRP + DI; pure core, I/O at edges)
- [ ] Gate 3 — Each component placed at Domain / Tier / Layer; allowed dependency edges drawn
- [ ] Gate 4 — Component-kinds / Dependency-edges / Max-chain-depth / Module-count Δ computed for design vs status quo
- [ ] Gate 5 — eslint.architecture.mjs in the SAME PR as the code
- [ ] Gate 6 — Every error path mapped to earliest catchable stage
- [ ] Gate 7 — Deferred to iteration 2
```

---

## 4. Retrospective Mode

Auditing existing code (refactor, dead-code review, scope cleanup) reverses
the order:

| Step | Skill | Action |
|:--|:--|:--|
| 1 | `structural-simplification` | Score current Component-kinds / Dependency-edges / Max-chain-depth / Module-count Δ — surface hot-spots |
| 2 | `functionality-complexity-tradeoff` | Run necessity gate on every type / method / branch |
| 3 | `architecture-as-code` (pattern); `-javascript` / `-python` (impl) | Add lint rules so the pruned shape can't re-grow |
| 4 | `defect-shift-left` | For each defect found, ask whether it could have been caught earlier |

---

## 5. Failure-Mode Diagnostics

| Symptom | Skipped gate | Recovery |
|:--|:--|:--|
| Interface added "for the second implementation" but second never lands | 1 — Rule of 3 | Run pruner; collapse to one concrete |
| Generic registry / plugin system with one entry | 1 — generality without instantiation | Inline the entry; remove the registry |
| Empty config / config with one value across all envs | 1 — one-value config | Inline the value |
| `if (impossible_state)` runtime guards | 1 — impossible-state guard | OBSOLETE; document the invariant elsewhere |
| Cross-domain imports across non-adjacent faces | 3 — placement violated | Move the component or extract a face-adjacent shim |
| Refactor "felt simpler" but no measurement | 4 — complexity not scored | Compute Component-kinds / Dependency-edges / Max-chain-depth / Module-count Δ before merging |
| Eslint rules added in follow-up PR | 5 — same-PR discipline broken | Block the follow-up; add rules to original PR |
| Defects caught at runtime that types could express | 6 — left-shift not applied | Move the check upward; remove the runtime guard |
| Architecture file disagrees with code | 5 — drift | Re-run lint; treat as a defect |
| "Just in case" extension point with one user | 1 — speculative optionality | DROP unless second use is named and probable |
| Premature performance optimization | 7 — applied before baseline | Revert; re-apply after stability |

---

## 6. Output Contract

Default output for a single-gate or simple routed request:

```
Route:    <M | A | L | C | E | H | Y | left | out | down>
Verdict:  Proceed | Redesign | Drop | Defer
Reason:   <one or two lines>
Next:     <one concrete action>
```

Use the expanded output only for multi-gate runs, non-trivial design/refactor
passes, audits, or explicit requests for detail. Emit one row per sibling skill
used:

| Gate | Skill | Decision | Evidence | Files/checks | Next action |
| ---- | ----- | -------- | -------- | ------------ | ----------- |

Then state:

```
Scope:          <module / service / refactor / PR>
Mode:           Design | Refactor | Audit
Blocking gate:  <first gate that blocks, or None>
Decision:       Proceed | Redesign | Reject | Defer
Verification:   <commands, lint rules, tests, or Not run + reason>
```

If implementing changes, include the normal coding summary after the alchemy
verdict.

## 7. Discipline

- **Skipped gates require a one-line rationale.** Skipped gates with no
  rationale are over-engineering risk for the next audit.
- **When a gate is consistently skipped across tasks**, that's a signal for
  `continuous-improvement` to update THIS skill — not paper over with
  case-by-case reminders.
