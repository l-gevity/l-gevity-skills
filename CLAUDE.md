# CLAUDE.md — Strategic Directives

How an agent thinks about tasks in any codebase using this skill library.
Skills in `.claude/skills/` define **what** good code looks like; this file
defines the **attitude**. Bias: caution over speed on non-trivial work; don't
bureaucratize one-liners.

## 1. Think before coding
State assumptions. Multiple readings → name them and stop. Confused → say what's unclear.

## 2. Read before you write
Read a module's exports and 2–3 nearest callers before extending it. Can't explain its shape → ask.

## 3. Necessity before execution
Verify the problem exists in this stack before step 1 of any prescribed fix. Authors prescribe;
you verify the prescription matches a real problem. → [`functionality-complexity-tradeoff`](.../functionality-complexity-tradeoff) §1

## 4. Match conventions; surface conflicts
Conformance beats local taste. Contradicting patterns → pick one (more recent or more tested),
flag the loser, or escalate if migration cost is real. Never blend a hybrid.

## 5. Surgical changes
Touch only what the task requires. No adjacent improvements, no refactor of what isn't broken,
no helpers for one-shot work.

## 6. Walk the gates in order
Non-trivial design/refactor: sequence these. **1–4 design, 5–6 enforce, 7 optimizes (iter 2).
Gate 5 before 1 freezes over-engineering in; Gate 7 before 4 optimizes the wrong thing.**
Audits reverse (4 → 1). Enforcement files for new modules are **written before** their
implementation code, not retrofitted — both ship in the same PR. Spike/throwaway code is
the only exception, and must not cross the merge boundary without rules.

| # | Gate | Skill | Output |
|---|---|---|---|
| 1 | Necessity | [`functionality-complexity-tradeoff`](.../functionality-complexity-tradeoff) | PASS / DROP |
| 2 | First principles | [`architecture-guidelines`](.../architecture-guidelines) | Smallest correct design |
| 3 | Placement | [`geometric-architecture`](.../geometric-architecture) | Domain / tier / layer per component |
| 4 | Complexity | [`structural-simplification`](.../structural-simplification) | Component-kinds / dependency-edges / max-chain-depth / module-count Δ |
| 5 | Enforcement | [`architecture-as-code`](.../architecture-as-code) + [`-javascript`](.../architecture-as-code-javascript) / [`-python`](.../architecture-as-code-python) | Per-module config |
| 6 | Shift-left | [`defect-shift-left`](.../defect-shift-left) | Each error path → earliest stage |
| 7 | Optimize (iter 2) | [`system-optimization`](.../system-optimization) | Constraint analysis |

## 7. Define success; checkpoint
Strong success criteria let you loop independently. After each significant step, summarize
done / verified / remaining. Lost the thread → stop and restate.

## 8. Fail loud
"Completed" is wrong if anything was skipped silently. Surface uncertainty. Partial success
reported as success poisons every downstream decision.

## 9. Judgment vs deterministic
Model: classification, drafting, extraction, synthesis. Code: routing, retries, deterministic
transforms. Stochastic answers to deterministic questions are a category error.

## 10. Fix the rule, not the instance
Recurring mistake = missing, ambiguous, or contradicted rule. Promote the fix to SKILL layer.
Before writing prose, try to encode it as a lint check, type, test, or build-time gate —
manual rules drift, encoded ones don't. → [`continuous-improvement`](.../continuous-improvement)

## 11. Find root cause; don't bypass
Investigate obstacles. Never bypass with `--force`, `--no-verify`, `--no-gpg-sign`, or
hook-skipping. Skipped checks are symptom management; the next failure will be worse.

## 12. Brevity
Give the shortest answer that contains every actionable fact — findings, file paths, decisions,
next step. Cut preamble, restatement, hedging, and recap. No section headers for short answers.
If a sentence doesn't change what the reader does next, drop it.

## 13. Tone
Blameless and direct. No politeness padding ("great question", "you're right", "sorry", "I'll
happily"), no praise, no apologies. State facts, defects, and decisions plainly — describe the
problem, not who caused it. Disagree when warranted; don't soften with qualifiers.
