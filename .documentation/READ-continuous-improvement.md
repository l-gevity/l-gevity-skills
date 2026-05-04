# Continuous Improvement (Meta-Learning)

A protocol for updating SKILL files when the agent makes a mistake. Trace each correction to its root cause; prefer a test or linter over a written rule; shrink the file before you grow it.

## Why use this

- **Recurring mistakes get fixed once.** A correction becomes a structural rule, not a sticky note that fades.
- **Skills don't bloat over time.** New rules force old ones to be pruned; density beats volume.
- **Symptoms aren't documented as rules.** Every change traces to the missing boundary, ambiguous wording, or misunderstood platform behavior — not to the surface error.
- **Automation is preferred over instruction.** Before adding a sentence to a SKILL, the protocol checks whether the rule could be a test or lint instead.
- **Skills stay non-redundant.** Cross-skill overlap is detected and removed; each rule has exactly one home.

## Fundamental principles

A SKILL file is operational memory. Without a discipline for updating it, two failure modes appear: the same mistake recurs because the lesson was never written down, or the file bloats with overlapping rules until nobody reads it. This protocol governs how SKILLs evolve.

- **Automation over rules.** A rule a linter can enforce should be a linter rule; a rule a test can enforce should be a test.
- **Shrink, don't grow.** Density over volume. Aggressively prune or extract before adding.
- **Root cause over symptom.** The fix is the missing invariant, not the surface error.
- **Zero redundancy.** A rule lives in exactly one SKILL; cross-references replace duplication.

## How to use

The skill activates when the agent is corrected, when a fix breaks something else, or when the same anti-pattern is attempted twice.

1. **Recognize a learning trigger.** User correction, regression, new validated pattern, repeated anti-pattern, or recurring CI/lint failure.
2. **Prompt the AI.**

   > *"I just corrected the agent on [X]. Apply continuous-improvement: trace the root cause, decide whether it should be automation or a SKILL update, and pick the right SKILL."*

3. **Read the diagnosis.** The skill names the root-cause category (missing/ambiguous, conflict, ignored rule, technical-constraint), the proposed fix (test, linter, or SKILL edit), and the SKILL that owns the change.
4. **Apply the update.** Add the test or rule, prune any contradicting older guidance, and verify with a unit test or audit that the previous mistake is now structurally impossible.

## Triggers for learning

| Trigger Type        | Scenario                                                                              |
|---------------------|---------------------------------------------------------------------------------------|
| **Correction**      | User corrects an architectural pattern, approach, or rule.                            |
| **Regression**      | A fix for one issue breaks another — an undocumented system boundary.                 |
| **New Pattern**     | A new, validated standard is successfully introduced to the codebase.                 |
| **Systemic Failure**| The same anti-pattern or workaround is attempted multiple times.                      |
| **Process Break**   | Recurring CI/CD or linter failures indicating a broken foundational rule.             |

## Root-cause questions

Before writing anything, ask:

- **Missing or ambiguous?** Was the requirement undocumented, or written softly ("should" instead of "MUST")?
- **Conflict?** Did two SKILL rules contradict each other?
- **Ignored due to invisibility?** Was the rule there but easy to miss? Promote it to `> [!WARNING]` or `> [!IMPORTANT]`.
- **Technical constraint?** Was the failure due to a misunderstood platform or framework behavior?

## When to skip

Single, idiosyncratic corrections that don't generalize. One-off task tweaks. Anything that belongs in conversation memory rather than the SKILL library — if the next contributor wouldn't trip on the same edge, it's not a SKILL update.

## Next steps

- See [SKILL.md](./SKILL.md) for the full protocol (triggers, root-cause analysis, update execution, verification, notification).
- For SKILL formatting and layout, see [`skill-creation`](../skill-creation/) (separate from this skill).
- For first-principles architectural rules referenced when triaging trigger root causes, see [`architecture-guidelines`](../architecture-guidelines/).
