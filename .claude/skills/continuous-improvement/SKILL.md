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
>    schema, type, build gate, or template. Observe a new check failing without
>    the rule before calling it enforced; a check never seen to fail is a
>    hypothesis, not a safeguard. If automation is infeasible or too costly,
>    record why and add the smallest useful prose rule.
> 2. **Density Over Volume**: Prefer replacing, merging, or tightening existing
>    rules before adding new ones. Prune only rules proven obsolete,
>    contradicted, or owned elsewhere.
> 3. **Root-Cause Focus**: Do not preserve a symptom as the rule. Trace the
>    error to its root cause (e.g., misunderstood framework, missing boundary
>    rule) and fix the most upstream reusable guidance.
> 4. **Single Owner, Explicit References**: Keep each rule's primary authority
>    in one SKILL. Other SKILLs may mention it briefly as a cross-reference when
>    routing users to the owner would prevent misuse.
> 5. **Operationalize Before Broadening**: For skill-library updates, add or
>    extend validation, templates, or primer checks before broad prose changes.
>    If prose is still needed, keep the rule at the owning SKILL and route
>    siblings to it.
> 6. **Promote Before Repinning**: When a consumer project proves a reusable
>    lesson, update the canonical generic skill library first. Publish that
>    revision, then repin the consumer; keep project facts in a local overlay.

## When to use this skill

- Triggered by user corrections, systemic failures, or regression triggers
  that are likely to recur beyond the current conversation (full catalogue in
  §1).
- Triggered when the user asks to improve, optimize, prune, or audit the skill
  library itself.
- **Out of scope:** This skill dictates the _triggers, analysis, and mindset_
  for updating SKILLs. It does NOT dictate the _formatting/layout_ of the SKILLs
  (follow your project's skill-authoring conventions) nor does it define the
  architectural code rules themselves (see `architecture-guidelines`).

---

## Skill-Library Optimization Mode

When the subject is the skills themselves, optimize in this order:

1. Define the behavioral failure, bottleneck, or drift risk; do not start from
   preferred wording.
2. Check whether validation can catch it: mirror sync, frontmatter, primer
   backlinks, output contract presence, owner/routing conflicts, or template
   shape.
3. Edit the owning `SKILL.md` only. Sibling skills get cross-references unless
   they must make a routing decision.
4. Keep `.agents/skills`, `.claude/skills`, and the matching
   `.documentation/READ-*.md` primer aligned in the same change. If the skill's
   public role or trigger changed, update the `README.md` skill index too.
5. Run `python scripts/validate-skills.py`. If no mechanical check can cover
   the lesson, record why in the output contract.

## Consumer-to-Library Promotion

Use this sequence when learning originates in a consumer project:

1. Capture the concrete failure, correction, or repeated successful pattern and
   its verification evidence in the consumer.
2. Extract the smallest behavior that applies without the project name, private
   paths, roles, domain taxonomy, local commands, or provider assumptions.
3. Update the one canonical generic owner in the skill library. Add a skill only
   when the capability has a distinct trigger, lifecycle, and output contract.
4. Update mirrors, primers, indexes, root routing guidance, and validation in the
   same library change.
5. Validate and publish the library revision.
6. Repin or reinstall that revision in the consumer, then retain only its
   project profile and other domain-specific skills locally.

Do not overwrite a generic library from a consumer tree or treat byte-identical
vendored files as locally owned. If a local emergency patch is unavoidable,
mark it as temporary divergence with an upstream owner and remove it when the
published fix is repinned.

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
| **Skill Optimization** | User asks to optimize, prune, audit, or increase efficiency of the skill library itself. |

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
  align the corresponding `.documentation/READ-*.md` primer and any affected
  `README.md` skill-index text.
- **Validate Shape**: Run the repo's skill validator after edits; extend it
  when a drift pattern can be detected mechanically.

## 4. Verification & Notification

Ensure the learning "sticks":

- **Verification**: If applicable, add a unit test, lint rule, schema check, or
  perform an audit showing the previous mistake is now caught earlier or made
  less likely. Do not claim structural impossibility unless an enforced gate
  guarantees it. For skill-library changes, run
  `python scripts/validate-skills.py`.
- **Notify**: Conclude the improvement sequence with a concise summary back to
  the user:
    > _"Updated [Skill/Test] to prevent [issue] by mandating [new practice]."_

## 5. Output Contract

When applying this skill, emit:

```
Subject:        <skill / test / linter / schema / template>
Trigger:        <correction | regression | new pattern | systemic failure | process break | skill optimization>
Root cause:     <missing/ambiguous | conflict | ignored rule | technical constraint | ownership gap>
Owner:          <skill/test/linter/schema/template that should own the fix>
Automation:     <implemented | infeasible | deferred> - <reason>
Decision:       <replace | add | delete | cross-reference | no change>
Verification:   <checks performed, and the observed failure without the rule>
Next action:    <edit made, check added, follow-up owner, or stop>
Residual risk:  <what still depends on judgment or future enforcement>
```

## 6. See also

- **`architecture-guidelines`** — first-principles rules that updates from this skill propagate back into.
- **`defect-shift-left`** — when a recurring correction can be encoded as a Stage 0–5 gate instead of a SKILL rule (Directive 1).
