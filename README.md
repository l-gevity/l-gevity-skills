# The L-GEVITY Essentail Software Architecture Skills

Open-source [Claude Code](https://claude.ai/claude-code) skills for software
architecture, CI/CD reliability, structural simplification, system optimization,
and continuous improvement.

These skills are platform-agnostic and can be used in any software project.

## About L-GEVITY

[L-GEVITY](https://l-gevity.nl) is a longevity-focused health platform that
translates peer-reviewed biomedical research into personalized, actionable
insights. By combining biometric data with epidemiological evidence, it helps
users understand how lifestyle choices — sleep, exercise, nutrition, stress — 
affect their long-term health outcomes.

This skills repository contains the platform-agnostic engineering principles we
developed while building L-GEVITY. They encode hard-won lessons about
architectural discipline, complexity reduction, and continuous improvement that
apply to any software project — not just ours.

## Skills

| Skill | Description |
| :---- | :---------- |
| [architecture-as-code-javascript](./architecture-as-code-javascript/SKILL.md) | JavaScript/ESLint mechanism for declaring and enforcing component boundaries via `eslint.architecture.mjs` files in the source tree. Each module declares its own internals; rules merge recursively into one ESLint flat-config rule set. Turns implicit architecture into lint-time enforcement. |
| [architecture-guidelines](./architecture-guidelines/SKILL.md) | Core architectural principles: consistency, minimalism, reliability, and traceability. Use when designing or modifying any system component. |
| [ci-cd-reliability-architecture](./ci-cd-reliability-architecture/SKILL.md) | Idempotency, self-containment, immutable artifacts, self-healing, zero-downtime, and zero-knowledge security for CI/CD pipelines. |
| [continuous-improvement](./continuous-improvement/SKILL.md) | Meta-learning protocol for evolving skills based on user feedback and root-cause analysis. |
| [defect-shift-left](./defect-shift-left/SKILL.md) | Places every error detection at the earliest pipeline stage technically capable of catching it. A 12-stage ladder, defect taxonomy, and decision protocol for choosing where a check belongs. |
| [functionality-complexity-tradeoff](./functionality-complexity-tradeoff/SKILL.md) | First-principles framework for deciding whether functionality is worth its complexity cost — applies to both proposed features (build/defer/drop) and existing code (keep/simplify/delete). |
| [geometric-architecture](./geometric-architecture/SKILL.md) | Maps software structure onto a 3D spatial grid (X=domain, Y=abstraction, Z=environment) where coupling is restricted to face-adjacent neighbors only — a cellular-automaton locality rule that makes long-range dependencies harder to express than short-range ones. |
| [structural-simplification](./structural-simplification/SKILL.md) | First-principles framework for reducing structural complexity in any domain — code, data models, workflows, UI layouts, org structures. |
| [system-optimization](./system-optimization/SKILL.md) | Lean, Kaizen, Six Sigma, Theory of Constraints, and DevOps principles to eliminate waste and improve flow. |

### In-depth explanations

For some of the skills, a longer essay accompanies the SKILL spec — useful
when you want the reasoning, not just the rules:

| Essay | Companion to |
| :---- | :----------- |
| [READ-architecture-as-code-javascript](./READ-architecture-as-code-javascript.md) | `architecture-as-code-javascript` — strategic guide: why move architecture rules from implicit agreements to enforced code, what it solves, and how it scales. |
| [READ-geometric-architecture](./READ-geometric-architecture.md) | `geometric-architecture` — why locality is a first principle, what emerges for free, and how to encode the rules as ESLint boundaries. |
| [READ-structural-simplification](./READ-structural-simplification.md) | `structural-simplification` — the deeper "why" behind the framework. |
| [READ-system-optimization](./READ-system-optimization.md) | `system-optimization` — extended rationale for Lean/TOC/DevOps integration. |

### Workflow

The architecture skills form a natural pipeline:

```
geometric-architecture → architecture-guidelines → structural-simplification → system-optimization
   (place / locality)         (build cleanly)         (evaluate complexity)        (improve flow)
```

`geometric-architecture` answers **where** a component belongs — its address on
the grid and which neighbors it may couple to. The remaining three skills then
answer **how** to build it, **whether** it is too complex, and **how to make
its operations flow**.

`functionality-complexity-tradeoff` complements this pipeline by deciding
**whether** a piece of functionality is worth its cost — both prospectively
(build / defer / drop) and retrospectively (keep / simplify / delete) —
consuming complexity measurements from `structural-simplification`.

Use `continuous-improvement` as a meta-layer to evolve the skills themselves.

## Usage

Copy the skills into your project's `.claude/skills/` directory (plain file
copy, no git repo is created):

```bash
git clone --depth 1 https://github.com/l-gevity/l-gevity-skills ~/.claude/skills && rm -rf ~/.claude/skills/.git
```

Then reference skills from your `CLAUDE.md`:

```markdown
- [architecture-guidelines](./.claude/skills/architecture-guidelines/)
- [structural-simplification](./.claude/skills/structural-simplification/)
```

To update to the latest skills, re-run the same command.

## License

[MIT](./LICENSE)
