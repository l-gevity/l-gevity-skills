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
>    schema, type, build gate, or template; `defect-shift-left` places such a
>    gate at the earliest stage that can enforce it. Observe a new check
>    failing without the rule before calling it enforced; a check never seen
>    to fail is a hypothesis, not a safeguard. If automation is infeasible or too costly,
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
>    revision, then repin the consumer; keep project facts in a local overlay:
>    its project profile and other domain-specific skills.

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

## Consumer-to-Library Promotion

When the subject is the skills themselves, or a lesson a consumer project
proved, decide in this order; the skill library's own contribution rules give
its maintenance steps:

1. **Evidence.** Name the observed failure the change prevents — a correction,
   transcript, incident, or scenario — or, from a consumer, the repeated
   successful pattern, with its verification evidence captured where it
   happened. Preferred wording, or a request to extend or complete a skill, is
   not one; without it, return a proposal with an M verdict instead of editing.
2. **Check.** Ask whether validation can catch it: frontmatter, output contract
   presence, owner/routing conflicts, template shape, or drift between copies.
3. **Owner.** Extract the smallest behavior that applies without the project
   name, private paths, roles, domain taxonomy, local commands, or provider
   assumptions, and update the one canonical generic owner in the skill
   library. Add a skill only when the capability has a distinct trigger,
   lifecycle, and output contract. Edit the owning `SKILL.md` only; sibling
   skills get cross-references unless they must make a routing decision.
4. **Never the vendored copy.** Do not overwrite a generic library from a
   consumer tree or treat byte-identical vendored files as locally owned. If a
   local emergency patch is unavoidable, mark it as temporary divergence with
   an upstream owner and remove it when the published fix is repinned or
   reinstalled.

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
- **Maintain and Validate**: update everything that travels with the skill in
  the same change, as the library's contribution rules require; extend its
  validation when a drift pattern can be detected mechanically.

## 4. Verification & Notification

Ensure the learning "sticks":

- **Verification**: If applicable, add a unit test, lint rule, schema check, or
  perform an audit showing the previous mistake is now caught earlier or made
  less likely. Do not claim structural impossibility unless an enforced gate
  guarantees it; `gate-lifecycle` keeps that gate proven after it lands. For
  skill-library changes, run the library's validation. A changed decision rule
  is a behavioral hypothesis: record the originating miss as a scenario that
  fails before the change and passes after, and apply the new rule to the
  change itself before calling it ready.
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
