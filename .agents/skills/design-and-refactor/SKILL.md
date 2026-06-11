---
name: design-and-refactor
description: >-
    Orchestrates non-trivial design and refactor work through sibling gates in
    order: necessity, first principles, placement, complexity, enforcement,
    shift-left, and optimization. Use when introducing a module, service, or
    library; designing an abstraction; extracting a package or component;
    refactoring across boundaries; or auditing over-engineering. Skip for local
    bug fixes, content or CSS edits, dependency bumps, and trivial renames.
    Defines no new rules; routes to the sibling skills that own each gate.
---

# Design & Refactor — Gate Sequence

> **Scope.** Pure routing — names the order, the trigger discipline, and the
> failure-mode diagnostics. Defines NO principles, metrics, or rules of its
> own. Every gate is a one-line pointer to a sibling skill.

> **Core Directives**
>
> 1. **Order matters.** Gates 1–4 are upstream (shape the design); Gates 5–6
>    are downstream (enforce it). NEVER run 5 before 1.
> 2. **Name the second instance.** Before writing any abstraction, name the
>    second concrete instance that justifies it. Rule of 3 is the null
>    hypothesis. If absent → DROP.
> 3. **Same PR, same gates.** `eslint.architecture.mjs` ships with the code
>    it governs. Follow-up PRs to "add the rules" are drift.
> 4. **Defer Gate 7.** `system-optimization` needs a stable baseline. Run on
>    iteration 2, not iteration 1.
> 5. **Audit reverses the order.** Retrospective mode runs Gate 4 → Gate 1
>    first to drive delete/simplify decisions before any restructuring.

---

## 1. The Gates

| # | Gate | Skill | Decision record |
|:--|:--|:--|:--|
| 1 | Necessity check | `functionality-complexity-tradeoff` | PASS / DROP per type, method, parameter |
| 2 | First principles | `architecture-guidelines` | Smallest correct design |
| 3 | Geometric placement | `geometric-architecture` | Domain / tier / layer per component + allowed dependency edges |
| 4 | Complexity measurement | `structural-simplification` | Component-kinds Δ, Dependency-edges Δ, Max-chain-depth Δ, Module-count Δ |
| 5 | Architecture as code | `architecture-as-code` (pattern); `-javascript` / `-python` (impl) | Per-module architecture config |
| 6 | Shift defect detection left | `defect-shift-left` | Each error path → earliest catchable stage |
| 7 | Optimize value stream | `system-optimization` | Constraint analysis (deferred to iter 2) |

For each gate's procedure and output contract: invoke the sibling skill. This
file does not duplicate that content, but the final report must normalize each
gate into the common coder-facing shape in §5.

---

## 2. Pre-Flight Checklist

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

## 3. Retrospective Mode

Auditing existing code (refactor, dead-code review, scope cleanup) reverses
the order:

| Step | Skill | Action |
|:--|:--|:--|
| 1 | `structural-simplification` | Score current Component-kinds / Dependency-edges / Max-chain-depth / Module-count Δ — surface hot-spots |
| 2 | `functionality-complexity-tradeoff` | Run necessity gate on every type / method / branch |
| 3 | `architecture-as-code` (pattern); `-javascript` / `-python` (impl) | Add lint rules so the pruned shape can't re-grow |
| 4 | `defect-shift-left` | For each defect found, ask whether it could have been caught earlier |

---

## 4. Failure-Mode Diagnostics

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

## 5. Output Contract

Emit one gate row per sibling skill used:

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

## 6. Discipline

- **Skipped gates require a one-line rationale.** Skipped gates with no
  rationale are over-engineering risk for the next audit.
- **When a gate is consistently skipped across tasks**, that's a signal for
  `continuous-improvement` to update THIS skill — not paper over with
  case-by-case reminders.
