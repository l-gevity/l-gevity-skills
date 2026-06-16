---
name: continuous-improvement
description: >-
    Protocol for updating skills based on user feedback and root-cause analysis
    to prevent recurring mistakes. Use this skill when deciding HOW and WHEN to
    evaluate or update other agent skills.
---

# Continuous Improvement Protocol (Meta-Learning)

This protocol governs the agent's **meta-learning process** (Kaizen). It ensures
that SKILL files evolve organically, preventing recurring errors through
systemic, root-cause adjustments, without growing bloated.

> **Core Directives**
>
> 1. **Automation Before Prose**: Before adding a manual instruction to a SKILL
>    document, check whether the lesson can be encoded as a test, linter,
>    schema, type, build gate, or template. If automation is infeasible or too
>    costly, record why and add the smallest useful prose rule.
> 2. **Density Over Volume**: Prefer replacing, merging, or tightening existing
>    rules before adding new ones. Prune only rules proven obsolete,
>    contradicted, or owned elsewhere.
> 3. **Root-Cause Focus**: Do not preserve a symptom as the rule. Trace the
>    error to its root cause (e.g., misunderstood framework, missing boundary
>    rule) and fix the most upstream reusable guidance.
> 4. **Single Owner, Explicit References**: Keep each rule's primary authority
>    in one SKILL. Other SKILLs may mention it briefly as a cross-reference when
>    routing users to the owner would prevent misuse.

## When to use this skill

- Triggered by user corrections, systemic failures, or regression triggers
  that are likely to recur beyond the current conversation (full catalogue in
  §1).
- **Out of scope:** This skill dictates the _triggers, analysis, and mindset_
  for updating SKILLs. It does NOT dictate the _formatting/layout_ of the SKILLs
  (follow your project's skill-authoring conventions) nor does it define the
  architectural code rules themselves (see `architecture-guidelines`).

---

## 1. Triggers for Learning

Initiate this protocol to examine and update existing `SKILL.md` files when
encountering:

| Trigger Type         | Scenario                                                                              |
| :------------------- | :------------------------------------------------------------------------------------ |
| **Correction**       | User explicitly corrects an architectural pattern, approach, or rule.                 |
| **Regression**       | A fix for one issue breaks another, indicating an undocumented system boundary.       |
| **New Pattern**      | A new, validated structural standard is successfully introduced to the codebase.      |
| **Systemic Failure** | The same class of anti-pattern or fragile workaround is attempted repeatedly, or once with high blast radius. |
| **Process Break**    | Recurring CI/CD failures or linter bottlenecks indicating a broken foundational rule. |

## 2. Analyze Root Cause

Determine the underlying reason before writing a new rule. Ask:

- **Missing/Ambiguous**: Was the requirement undocumented, too broad, too
  absolute, or written with the wrong force?
- **Conflict**: Did two SKILL rules contradict each other?
- **Ignored Rule**: Was a rule clear but ignored due to lack of visibility in
  the file? Improve placement or wording before promoting it to a warning block.
- **Technical Constraint**: Was the failure due to a misunderstood platform or
  framework behavior?

## 3. The Update Execution

When generating the actual update to the relevant `SKILL.md` file:

- **Actionable Constraints**: Ensure new rules are testable, direct, scoped,
  and explicit about exceptions.
- **Review Sibling Skills**: Check existing skills to ensure you are not
  creating an ownership conflict or duplicating the rule's primary authority.
- **Eliminate Outdated Logic**: Replace or delete previous rules only when they
  contradict, overlap with, or are made obsolete by the new learning. Preserve
  useful exceptions and migration notes.
- **Maintain Mirrors**: When this library has both `.agents/skills` and
  `.claude/skills` copies, keep the matching `SKILL.md` files synchronized and
  align the corresponding `.documentation/READ-*.md` primer.

## 4. Verification & Notification

Ensure the learning "sticks":

- **Verification**: If applicable, add a unit test, lint rule, schema check, or
  perform an audit showing the previous mistake is now caught earlier or made
  less likely. Do not claim structural impossibility unless an enforced gate
  guarantees it.
- **Notify**: Conclude the improvement sequence with a concise summary back to
  the user:
    > _"Updated [Skill/Test] to prevent [issue] by mandating [new practice]."_

## 5. Output Contract

When applying this skill, emit:

```
Subject:        <skill / test / linter / schema / template>
Trigger:        <correction | regression | new pattern | systemic failure | process break>
Root cause:     <missing/ambiguous | conflict | ignored rule | technical constraint | ownership gap>
Owner:          <skill/test/linter/schema/template that should own the fix>
Automation:     <implemented | infeasible | deferred> - <reason>
Decision:       <replace | add | delete | cross-reference | no change>
Verification:   <test/lint/audit/search performed>
Next action:    <edit made, check added, follow-up owner, or stop>
Residual risk:  <what still depends on judgment or future enforcement>
```

## 6. See also

- **`architecture-guidelines`** — first-principles rules that updates from this skill propagate back into.
- **`defect-shift-left`** — when a recurring correction can be encoded as a Stage 0–5 gate instead of a SKILL rule (Directive 1).
