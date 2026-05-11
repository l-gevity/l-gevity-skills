# Design & Refactor

![Design and Refactor](design_and_refactor.svg)

A pure routing skill that sequences the architecture skills into a deterministic gate flow. Names the order, the trigger discipline, and the diagnostic signature for each common over-engineering pattern.

## Why use this

- **Order becomes deterministic.** The same gates fire in the same sequence every time, instead of "let me think about what to consider next."
- **Speculative generality is caught at Gate 1, not after a rewrite.** Every abstraction has to name a second concrete instance before it lives.
- **Enforcement never precedes design.** Architecture-as-code rules are written *with* the code, not after — drift between PRs becomes structurally impossible.
- **Audits invert cleanly.** Existing-code reviews run the gates in reverse; the same skills produce delete-or-simplify verdicts instead of build-or-defer verdicts.
- **Failure modes are nameable.** Symptom → skipped gate → recovery is a ten-row table, not a vibe.

## Fundamental principles

Most over-engineering is timing, not capability. Run enforcement before necessity and the architecture freezes whatever the design got wrong on the first pass. The gates exist because the failure modes are systematic.

- **Order matters.** Gates 1–4 shape *what* gets built. Gates 5–6 enforce *what was decided*. Run 5 before 1 and you machine-check a speculative design.
- **Name the second instance.** Rule of 3 is the null hypothesis; an abstraction without a named second concrete user is YAGNI.
- **Same PR, same gates.** `eslint.architecture.mjs` ships with the code it governs. Follow-up PRs to "add the rules" are drift.
- **Defer optimization.** `system-optimization` requires a stable baseline; running it on iteration 1 optimizes a system that has not yet faced real change.
- **Audit reverses.** Retrospective mode runs Gate 4 → Gate 1 first — observed complexity surfaces hot-spots before the necessity gate drives cuts.

## How to use

The skill applies in two situations: **designing** a new module, or **auditing** existing code for over-engineering.

1. **Identify the trigger.** Introducing a new module / service / library, refactoring across module boundaries, designing a new abstraction, extracting a sub-cell into a package, or auditing existing code for over-engineering.
2. **Prompt the AI.**

   > *Design:* "I'm extracting the import logic into its own module so it can ship to npm. Walk me through the design-and-refactor gates."
   >
   > *Audit:* "Run design-and-refactor in retrospective mode on `packages/shared-ui/js/biomarker-import/`. Flag any speculative generality."

3. **Read the verdict.** The skill names which gates passed, which gates were skipped (with rationale), the necessity-gate output (PASS / DROP), the complexity vector, and which `eslint.architecture.mjs` files need to land in the same PR.
4. **Apply the fix.** Drop everything Gate 1 flagged. Place each surviving cell at (X, Y, Z). Compute ΔD, ΔK, ΔP, Δn for the proposed structure. Write the architecture file. Move every error path to its earliest catchable stage.

## The seven gates at a glance

| #   | Gate                          | Skill                                                                                | Output                                       |
|-----|-------------------------------|--------------------------------------------------------------------------------------|----------------------------------------------|
| **1** | Necessity check               | [`functionality-complexity-tradeoff`](../.claude/skills/functionality-complexity-tradeoff/)                      | PASS / DROP per type, method, parameter      |
| **2** | First principles              | [`architecture-guidelines`](../.claude/skills/architecture-guidelines/)                             | Smallest correct design                      |
| **3** | Geometric placement           | [`geometric-architecture`](../.claude/skills/geometric-architecture/)                               | (X, Y, Z) per cell + allowed edges           |
| **4** | Complexity measurement        | [`structural-simplification`](../.claude/skills/structural-simplification/)                         | ΔD, ΔK, ΔP, Δn vector                        |
| **5** | Architecture as code          | [`architecture-as-code`](../.claude/skills/architecture-as-code/) (pattern); [`-javascript`](../.claude/skills/architecture-as-code-javascript/) / [`-python`](../.claude/skills/architecture-as-code-python/) (impl) | Per-module architecture config        |
| **6** | Shift defect detection left   | [`defect-shift-left`](../.claude/skills/defect-shift-left/)                                         | Each error path → earliest catchable stage   |
| **7** | Optimize the value stream     | [`system-optimization`](../.claude/skills/system-optimization/)                                     | Constraint analysis (deferred to iter 2)     |

The skill does not duplicate sibling content. Each gate is one row in this table; running a gate means invoking its sibling skill.

## The retrospective inversion

When auditing existing code, the order reverses:

| Step | Skill                                                          | Action                                                                              |
|------|----------------------------------------------------------------|-------------------------------------------------------------------------------------|
| **1** | [`structural-simplification`](../.claude/skills/structural-simplification/)   | Score current ΔD, ΔK, ΔP, Δn — surface hot-spots                                    |
| **2** | [`functionality-complexity-tradeoff`](../.claude/skills/functionality-complexity-tradeoff/) | Run necessity gate on every type / method / branch the audit covers                 |
| **3** | [`architecture-as-code`](../.claude/skills/architecture-as-code/) (pattern); [`-javascript`](../.claude/skills/architecture-as-code-javascript/) / [`-python`](../.claude/skills/architecture-as-code-python/) (impl) | Add lint rules so the pruned shape can't re-grow                          |
| **4** | [`defect-shift-left`](../.claude/skills/defect-shift-left/)                   | For each defect found, ask whether it could have been caught at an earlier stage    |

Forward flow assumes new design; reverse flow starts from observed state and works toward minimum sufficient structure. They meet at Gate 5.

## The failure-mode diagnostic

When a design ships overbuilt, the symptom usually points at one specific skipped gate. The skill carries an eleven-row table mapping symptom → skipped gate → recovery, including:

- Interface added "for the second implementation" but the second never lands → Gate 1, Rule of 3.
- Generic registry / plugin system with one entry → Gate 1, generality without instantiation.
- Empty config / config with one value across all envs → Gate 1, one-value config.
- `if (impossible_state)` runtime guards → Gate 1, impossible-state guard.
- Cross-domain imports across non-adjacent faces → Gate 3, placement violated.
- Refactor "felt simpler" but no measurement → Gate 4, complexity not scored.
- Eslint rules added in follow-up PR → Gate 5, same-PR discipline broken.
- Architecture file disagrees with code → Gate 5, drift.
- Defects caught at runtime that types could express → Gate 6, left-shift not applied.

Each row points back to the gate that would have caught it prospectively.

## When to skip

Bug fixes within an existing module, content/copy edits, CSS-only changes, dependency bumps, trivial renames. The skill earns its keep when module boundaries are being drawn, crossed, or audited — not for routine work inside a governed cell.

## Next steps

- See [SKILL.md](../.claude/skills/design-and-refactor/SKILL.md) for the full pre-flight checklist, gate sequence, and failure-mode diagnostic table.
- For the necessity gate (Gate 1) and what it catches in detail, see [`functionality-complexity-tradeoff`](../.claude/skills/functionality-complexity-tradeoff/).
- For first-principles rules driving Gate 2, see [`architecture-guidelines`](../.claude/skills/architecture-guidelines/).
- For the (X, Y, Z) placement model used at Gate 3, see [`geometric-architecture`](../.claude/skills/geometric-architecture/).
- For the per-axis complexity scoring used at Gate 4, see [`structural-simplification`](../.claude/skills/structural-simplification/).
- For the enforcement files produced at Gate 5, see [`architecture-as-code`](../.claude/skills/architecture-as-code/) (the pattern), with [`-javascript`](../.claude/skills/architecture-as-code-javascript/) and [`-python`](../.claude/skills/architecture-as-code-python/) as concrete implementations.
- For the shift-left hierarchy applied at Gate 6, see [`defect-shift-left`](../.claude/skills/defect-shift-left/).
- For the constraint analysis applied at Gate 7, see [`system-optimization`](../.claude/skills/system-optimization/).
- For the meta-loop that updates this skill when a gate is repeatedly skipped, see [`continuous-improvement`](../.claude/skills/continuous-improvement/).
