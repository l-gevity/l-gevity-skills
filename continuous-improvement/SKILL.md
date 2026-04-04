---
name: continuous-improvement
description:
    Protocol for updating skills based on user feedback and root-cause analysis
    to prevent recurring mistakes. Use this skill when deciding HOW and WHEN to
    evaluate or update other agent skills.
---

# Continuous Improvement Protocol (Meta-Learning)

This protocol governs the agent's **meta-learning process** (Kaizen). It ensures
that SKILL files evolve organically, preventing recurring errors through
systemic, root-cause adjustments, without growing bloated.

> **TL;DR / Core Directives**
>
> 1. **Automation Over Rules**: Before adding a manual instruction to a SKILL
>    document, you MUST explicitly attempt to turn it into an automated test or
>    linter constraint.
> 2. **Shrink, Don't Grow**: Density over volume. Aggressively extract or prune
>    old rules when adding new ones to prevent bloated, unreadable files.
> 3. **Root-Cause Focus**: NEVER document symptoms. Trace the error to its root
>    cause (e.g., misunderstood framework, missing boundary rule) and fix the
>    systemic rule.
> 4. **Zero Redundancy**: Keep minimal overlap across SKILL files. Never
>    duplicate a rule that belongs elsewhere.

## When to use this skill

- When deciding HOW and WHEN to evaluate or update other agent skills.
- When reacting to user corrections, systemic failures, or regression triggers.
- **Out of scope:** This skill dictates the _triggers, analysis, and mindset_
  for updating SKILLs. It does NOT dictate the _formatting/layout_ of the SKILLs
  (see `skill-creation`) nor does it define actual architectural code rules (see
  `architecture-guidelines`).

---

## 1. Triggers for Learning

Initiate this protocol to examine and update existing `SKILL.md` files when
encountering:

| Trigger Type         | Scenario                                                                              |
| :------------------- | :------------------------------------------------------------------------------------ |
| **Correction**       | User explicitly corrects an architectural pattern, approach, or rule.                 |
| **Regression**       | A fix for one issue breaks another, indicating an undocumented system boundary.       |
| **New Pattern**      | A new, validated structural standard is successfully introduced to the codebase.      |
| **Systemic Failure** | The exact same anti-pattern or fragile workaround is attempted multiple times.        |
| **Process Break**    | Recurring CI/CD failures or linter bottlenecks indicating a broken foundational rule. |

## 2. Analyze Root Cause

Determine the underlying reason before writing a new rule. Ask:

- **Missing/Ambiguous**: Was the requirement undocumented or written softly
  ("should" instead of "MUST")?
- **Conflict**: Did two SKILL rules contradict each other?
- **Ignored Rule**: Was a rule clear but ignored due to lack of visibility in
  the file? Promote it to a `> [!WARNING]` or `> [!IMPORTANT]` block.
- **Technical Constraint**: Was the failure due to a misunderstood platform or
  framework behavior?

## 3. The Update Execution

When generating the actual update to the relevant `SKILL.md` file:

- **Actionable Constraints**: Ensure new rules are highly testable, direct, and
  definitive.
- **Review Sibling Skills**: Check existing skills to ensure you are not
  creating a redundant rule that violates DRY principles.
- **Eliminate Outdated Logic**: Relentlessly delete any previous rules that
  contradict or overlap with the new learning.

## 4. Verification & Notification

Ensure the learning "sticks":

- **Verification**: If applicable, add a unit test or perform a code audit
  proving the previous mistake is now structurally impossible.
- **Notify**: Conclude the improvement sequence with a concise summary back to
  the user:
    > _"Updated [Skill/Test] to prevent [issue] by mandating [new practice]."_
