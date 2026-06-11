---
name: bring-down
description: >-
    Moves bespoke, duplicated, or over-local code down into reusable
    components, patterns, platform primitives, or managed services. Use when
    assessing whether custom code should stay one-off, be componentized,
    patternized, platformized, or replaced by a service; when applying Rule of
    3 extraction; when reducing copy/paste implementations; or when designing
    an improvement roadmap for code specificity, reuse, and platform leverage.
---

# Bring-Down

> **Purpose**: Lower implementation altitude. Move code from bespoke one-off
> solutions toward the lowest responsible reusable capability.

> **Improvement Trio**
>
> - `defect-shift-left`: move defect detection earlier.
> - `push-out`: move recurring operational work outward.
> - `bring-down`: move bespoke code down into reusable capability.

> **Core Directives**
>
> 1. **Prove repetition before extraction.** One instance is not a pattern.
> 2. **Bring down to the lowest responsible level.** Stop when the target level
>    absorbs real duplication without hiding necessary variation.
> 3. **Do not platformize uncertainty.** A premature platform multiplies cost.
> 4. **Preserve escape hatches.** Lower-level capability must not block valid
>    local needs.
> 5. **Measure adoption and deletion.** Extraction succeeds when copies retire,
>    not when a shared abstraction exists.

---

## 1. Bring-Down Scale

The scale measures implementation altitude: high means bespoke and local; low
means reusable and systemic.

| Level | Name | Code lives as | Evidence |
| ----- | ---- | ------------- | -------- |
| **5** | One-off custom code | A single local implementation | One repo/feature/team, no repeated shape |
| **4** | Repeated local pattern | Similar code repeated informally | Copy/paste, parallel scripts, recurring PR shape |
| **3** | Componentized | Shared module, package, component, or API | Consumers import/call one maintained implementation |
| **2** | Patternized / templated | Golden path, template, generator, policy, reference architecture | New instances start from the standard path |
| **1** | Platform primitive | Guardrailed internal capability | Teams consume it self-service with validation and observability |
| **0** | Managed service / commodity | External or managed service with minimal custom code | Local implementation is gone or only integration remains |

```
bring-down distance = current level - target level
```

Lower is not automatically better. The target is the lowest level that removes
real duplication while preserving legitimate variation.

---

## 2. Extraction Triggers

| Signal | Default action |
| ------ | -------------- |
| **1 instance** | Keep local unless risk/compliance demands a standard |
| **2 instances** | Watch; document similarities and differences |
| **3 instances** | Extract, patternize, or justify why contexts differ |
| **High-risk single instance** | Consider early pattern/platform if failure cost is high |
| **Many divergent copies** | Standardize the stable core; keep extension points explicit |

Rule of 3 is a trigger, not an order. If three copies solve materially different
problems, do not force a shared abstraction.

---

## 3. Target-Level Heuristics

| Condition | Target |
| --------- | ------ |
| Unique feature-specific behavior | Level 5 |
| Repeated shape but variation still unclear | Level 4 or 3 |
| Stable logic reused by multiple call sites | Level 3 |
| Stable creation workflow repeated across repos | Level 2 |
| Cross-team operational capability with policy needs | Level 1 |
| Non-differentiating commodity function | Level 0 |

Use `functionality-complexity-tradeoff` before extracting: if the duplicated
functionality is unnecessary, delete it instead of bringing it down.

---

## 4. Bring-Down Protocol

1. **Define scope.** Name the repos, modules, services, teams, or workflows
   under review.
2. **Inventory candidates.** Find copy/paste code, repeated scripts, repeated
   PR shapes, local wrappers, and one-off infra/app patterns.
3. **Question necessity.** Delete obsolete or non-problem-solving code first.
4. **Compare variation.** List what is common, what differs, and why.
5. **Assign current level.** Use the scale with evidence.
6. **Choose target level.** Pick the lowest responsible level by repetition,
   stability, risk, and variation.
7. **Compute distance.** Current level - target level.
8. **Choose one move.** Move down one level unless the intermediate level is
   already satisfied.
9. **Prove and retire.** Migrate at least one real consumer and remove the old
   duplicate path.

Prioritize by:

```
priority = bring-down distance x repetition x churn x blast radius
```

If the improvement is mainly about human execution rather than code shape, use
`push-out`. If it is mainly about check timing, use `defect-shift-left`.

---

## 5. Move Patterns

| Move | Use when | Action |
| ---- | -------- | ------ |
| **5 to 4** | First repetition appears | Name the pattern; keep local implementations |
| **4 to 3** | Repetition is stable | Extract shared module/component/API |
| **3 to 2** | New instances repeat setup | Add template, generator, policy, or reference architecture |
| **2 to 1** | Teams need a governed capability | Build platform primitive with validation, observability, support model |
| **1 to 0** | Capability is commodity | Replace with managed service or external standard |

Each move must include migration and deletion criteria. A new abstraction with
all old copies still alive is inventory, not simplification.

---

## 6. Anti-Patterns

| Anti-pattern | Correction |
| ------------ | ---------- |
| Extracting after one instance | Wait for repetition or document risk exception |
| Shared abstraction hiding real variation | Split stable core from explicit extension points |
| Platform primitive without adoption | Measure consumers, escape hatches, and support load |
| Template with no enforcement | Add lint, generator checks, or review gate where feasible |
| Managed service for differentiating logic | Keep local or componentized where domain value lives |
| Wrapper around commodity service with no added policy | Delete wrapper or state the invariant it enforces |
| Extraction without deleting copies | Require migration and retirement criteria |

---

## 7. Output Contract

Emit results in this shape:

```
Scope:          <repos/modules/services/teams/workflows>
Mode:           Assessment | Improvement | Roadmap
Summary:        <2-4 sentences: main duplication, best bring-down move, key risk>

Candidates:
| Candidate | Current level | Target level | Distance | Repetition evidence | Variation | Confidence | Next action |
| --------- | ------------- | ------------ | -------- | ------------------- | --------- | ---------- | ----------- |

Priorities:
| Rank | Candidate | Why now | Bring-down move | Migration proof | Duplicate to retire |
| ---- | --------- | ------- | --------------- | --------------- | ------------------- |

Gaps:
<Missing evidence, unclear ownership, unproven repetition, variation risks, or excluded candidates>
```

---

## 8. See Also

- **`functionality-complexity-tradeoff`** - decide whether the functionality should exist before extracting it.
- **`structural-simplification`** - verify the extraction actually reduces component kinds, edges, depth, or count.
- **`push-out`** - move recurring operational work outward.
- **`defect-shift-left`** - move defect detection earlier.
- **`architecture-as-code`** - enforce accepted patterns as code.
