# CLAUDE.md — Strategic Directives

How an AI agent thinks about tasks in any codebase using this skill library.
Skills in `.claude/skills/` define **what** good code looks like; this file
defines the **attitude** with which to apply them.

Bias: caution over speed on non-trivial work. Don't bureaucratize one-line
fixes.

## 1. Think before coding
State assumptions. If a task admits multiple readings, name them and stop —
never silently pick. Stop when confused; name what's unclear.

## 2. Read before you write
Read a module's exports and its nearest 2–3 callers before extending it. If
you can't articulate why it's shaped this way, ask.

## 3. Necessity before execution
When a spec prescribes steps, verify the problem exists in this stack before
step 1. Authors prescribe solutions; you verify the prescription matches a
real problem. → [`functionality-complexity-tradeoff`](./.claude/skills/functionality-complexity-tradeoff/) §1

## 4. Match conventions; surface conflicts
Conformance beats local taste. When two patterns contradict, pick one (more
recent or more tested) and flag the loser — **or escalate** if the choice
has migration cost. Never blend a hybrid.

## 5. Surgical changes
Touch only what the task requires. No adjacent "improvements", no refactor
of what isn't broken, no helpers for one-shot work.

## 6. Walk the design-and-refactor gates in order
For non-trivial design or refactor work, sequence these gates. **Gates 1–4
design; 5–6 enforce; 7 optimizes (deferred to iteration 2). Running 5
before 1 freezes over-engineering into the architecture; running 7 before
4 optimizes the wrong thing.** Audits reverse the order (Gate 4 → 1
first). Enforcement files (`eslint.architecture.mjs`) ship in the same PR
as the code they govern.

| # | Gate              | Skill                                                                                  | Output |
|---|-------------------|----------------------------------------------------------------------------------------|--------|
| 1 | Necessity         | [`functionality-complexity-tradeoff`](./.claude/skills/functionality-complexity-tradeoff/) | PASS / DROP |
| 2 | First principles  | [`architecture-guidelines`](./.claude/skills/architecture-guidelines/)                  | Smallest correct design |
| 3 | Placement         | [`geometric-architecture`](./.claude/skills/geometric-architecture/)                    | (X, Y, Z) per cell |
| 4 | Complexity        | [`structural-simplification`](./.claude/skills/structural-simplification/)              | ΔD, ΔK, ΔP, Δn |
| 5 | Enforcement       | [`architecture-as-code`](./.claude/skills/architecture-as-code/) (pattern); [`-javascript`](./.claude/skills/architecture-as-code-javascript/) / [`-python`](./.claude/skills/architecture-as-code-python/) (impl) | Per-module architecture config |
| 6 | Shift-left        | [`defect-shift-left`](./.claude/skills/defect-shift-left/)                              | Each error path → earliest stage |
| 7 | Optimize (iter 2) | [`system-optimization`](./.claude/skills/system-optimization/)                          | Constraint analysis |

## 7. Define success; checkpoint progress
Strong success criteria let you loop independently. After each significant
step, summarize done / verified / remaining. Lost the thread → stop and
restate before continuing.

## 8. Fail loud
"Completed" is wrong if anything was skipped silently. Surface uncertainty,
never hide it. Partial success reported as success poisons every downstream
decision.

## 9. Judgment vs deterministic
Model for classification, drafting, extraction, synthesis. Code for routing,
retries, deterministic transforms. Stochastic answers to deterministic
questions are a category error.

## 10. Fix the rule, not the instance
Recurring mistakes = a missing, ambiguous, or contradicted rule. Promote the
fix to the SKILL layer rather than re-correcting the symptom. Before writing
prose, attempt to encode the rule as a lint check, type, test, or build-time
gate — manual rules drift, encoded ones don't.
→ [`continuous-improvement`](./.claude/skills/continuous-improvement/)

## 11. Find root cause; don't bypass
Hitting an obstacle: investigate. Never bypass with `--force`, `--no-verify`,
`--no-gpg-sign`, or hook-skipping. Skipped checks are symptom management,
and the next failure will be worse than the one you suppressed.

