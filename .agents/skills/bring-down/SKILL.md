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
> 6. **Search the current stack first.** Prefer existing local components,
>    templates, platform primitives, and already-approved services before
>    surveying the external market.

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

## 4. Current-Stack Survey

The first bring-down move is discovery inside the current technology stack.
Look for a lower placement or alternative that already exists before creating
or buying anything.

Search for:

| Target | Signals |
| ------ | ------- |
| **Existing component** | Shared package, module, library, helper, internal API |
| **Existing pattern** | Template, generator, reference architecture, ADR, code owner convention |
| **Existing platform primitive** | Internal service, reusable workflow, paved-road module, self-service control |
| **Already-approved managed service** | Provider/service already used, security-approved, contracted, or supported |
| **Framework-native capability** | Built-in feature that replaces local wrapper or custom code |

Prefer stack-native and locally adopted options over new abstractions. A new
component, template, platform primitive, or external service is justified only
when the current stack has no suitable lower placement.

---

## 5. Managed-Service Survey

Browse only after Level 0 is plausible and the current-stack survey has not
found a suitable already-approved alternative. Do not use internet search to
justify extraction, deletion, or abstraction; use it only to compare current
external service alternatives.

1. **Confirm commodity shape.** The capability is non-differentiating, broadly
   available as a service, or mostly operational burden.
2. **Define constraints.** Record data sensitivity, compliance, latency,
   region, cost model, lock-in tolerance, operational model, migration needs,
   and rollback needs.
3. **Search current alternatives.** Use primary sources where possible:
   official docs, pricing pages, SLA pages, security/compliance pages, and
   migration guides.
4. **Compare adjacent levels.** Include "keep local", Level 3 componentized,
   Level 1 platform primitive, and current-stack alternatives in the comparison.
5. **Recommend only with proof.** Level 0 wins only when it reduces code,
   operations, risk, or maintenance without violating constraints.

When the user asks for specific service alternatives, browse. Provider
capabilities, pricing, SLAs, regions, and compliance posture are time-sensitive.

---

## 6. Bring-Down Protocol

1. **Define scope.** Name the repos, modules, services, teams, or workflows
   under review.
2. **Inventory candidates.** Find copy/paste code, repeated scripts, repeated
   PR shapes, local wrappers, and one-off infra/app patterns.
3. **Question necessity.** Delete obsolete or non-problem-solving code first.
4. **Search the current stack.** Look for existing lower placements:
   components, templates, platform primitives, approved services, or
   framework-native capabilities.
5. **Compare variation.** List what is common, what differs, and why.
6. **Assign current level.** Use the scale with evidence.
7. **Choose target level.** Pick the lowest responsible level by repetition,
   stability, risk, and variation.
8. **Compute distance.** Current level - target level.
9. **Choose one move.** Move down one level unless the intermediate level is
   already satisfied.
10. **Prove and retire.** Migrate at least one real consumer and remove the old
   duplicate path.

Prioritize by:

```
priority = bring-down distance x repetition x churn x blast radius
```

If the improvement is mainly about human execution rather than code shape, use
`push-out`. If it is mainly about check timing, use `defect-shift-left`.

---

## 7. Move Patterns

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

## 8. Do Not Confuse With Placement

`bring-down` changes reuse/specificity altitude. It does not assign domain,
tier, layer, or dependency direction.

After choosing to componentize, patternize, or platformize, use
`geometric-architecture` to place the resulting module and `architecture-as-code`
to enforce allowed imports. Use `structural-simplification` to verify the move
actually reduces complexity.

Here, "down" means less bespoke and more systemic, not lower in the dependency
graph.

---

## 9. Anti-Patterns

| Anti-pattern | Correction |
| ------------ | ---------- |
| Extracting after one instance | Wait for repetition or document risk exception |
| Shared abstraction hiding real variation | Split stable core from explicit extension points |
| Building a new shared thing before looking locally | Search the current stack for existing lower placements first |
| Platform primitive without adoption | Measure consumers, escape hatches, and support load |
| Template with no enforcement | Add lint, generator checks, or review gate where feasible |
| Managed service for differentiating logic | Keep local or componentized where domain value lives |
| Service selection from stale memory | Browse current primary sources before recommending alternatives |
| Wrapper around commodity service with no added policy | Delete wrapper or state the invariant it enforces |
| Extraction without deleting copies | Require migration and retirement criteria |
| Treating bring-down as layer movement | Use `geometric-architecture` for placement and dependency direction |

---

## 10. Output Contract

Emit results in this shape:

```
Scope:          <repos/modules/services/teams/workflows>
Mode:           Assessment | Improvement | Roadmap
Decision:       Keep local | Componentize | Patternize | Platformize | Use managed service | Reject
Summary:        <2-4 sentences: main duplication, best bring-down move, key risk>
Verification:   <searches, callers, service docs, tests, or Not run + reason>

Candidates:
| Candidate | Current level | Target level | Distance | Existing lower placement | Repetition evidence | Variation | Service candidates | Decision | Confidence | Next action |
| --------- | ------------- | ------------ | -------- | ------------------------ | ------------------- | --------- | ------------------ | -------- | ---------- | ----------- |

Priorities:
| Rank | Candidate | Why now | Bring-down move | Migration proof | Duplicate to retire |
| ---- | --------- | ------- | --------------- | --------------- | ------------------- |

Gaps:
<Missing evidence, unclear ownership, unproven repetition, variation risks, or excluded candidates>

Managed-service comparison:
| Service option | Fit | Gaps | Lock-in | Migration cost | Rollback path |
| -------------- | --- | ---- | ------- | -------------- | ------------- |
```

---

## 11. See Also

- **`functionality-complexity-tradeoff`** - decide whether the functionality should exist before extracting it.
- **`structural-simplification`** - verify the extraction actually reduces component kinds, edges, depth, or count.
- **`geometric-architecture`** - place the resulting component after bring-down chooses the reuse level.
- **`push-out`** - move recurring operational work outward.
- **`defect-shift-left`** - move defect detection earlier.
- **`architecture-as-code`** - enforce accepted patterns as code.
