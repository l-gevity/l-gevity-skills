# The L-GEVITY Software Architecture AI Skills

**SKILLs that put 30+ years of software development expertise in an AI assistant**

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

Ten skills, organized into six groups by the question each one answers. Every
skill ships as a `SKILL.md` (the operational reference); a matching
`READ-<skill>.md` primer in [`./.documentation/`](./.documentation/) gives the
plain-English overview.

### Architectural foundations — *what should the system look like?*

| Skill | Readme | Use it to |
| :---- | :----- | :-------- |
| [architecture-guidelines](./architecture-guidelines/SKILL.md) | [READ](./.documentation/READ-architecture-guidelines.md) | Test every module decision — minimalism, modularity, functional core, resilience, naming, concurrency — against a first-principles checklist before code is written. |
| [geometric-architecture](./geometric-architecture/SKILL.md) | [READ](./.documentation/READ-geometric-architecture.md) | Place a component on the `(X, Y, Z)` grid, and audit existing graphs for layer skips, cycles, god cells, and cross-domain coupling. |

### Architectural enforcement — *how do we make the rules stick?*

| Skill | Readme | Use it to |
| :---- | :----- | :-------- |
| [architecture-as-code-javascript](./architecture-as-code-javascript/SKILL.md) | [READ](./.documentation/READ-architecture-as-code-javascript.md) | Encode allowed imports between modules so architectural violations fail `eslint` instead of slipping through review. |
| [architecture-as-code-python](./architecture-as-code-python/SKILL.md) | [READ](./.documentation/READ-architecture-as-code-python.md) | Encode allowed imports between Python packages — via per-package `architecture.toml` — so violations fail `import-linter` instead of slipping through review. |

### Pipeline reliability — *how do we catch defects early and ship safely?*

| Skill | Readme | Use it to |
| :---- | :----- | :-------- |
| [defect-shift-left](./defect-shift-left/SKILL.md) | [READ](./.documentation/READ-defect-shift-left.md) | Audit a pipeline for shift-left opportunities, and decide where any new check belongs — type system, lint, pre-commit, CI gate, or beyond. |
| [ci-cd-reliability-architecture](./ci-cd-reliability-architecture/SKILL.md) | [READ](./.documentation/READ-ci-cd-reliability-architecture.md) | Design or audit a CI/CD pipeline against six rules: idempotent, self-contained, immutable artifacts, self-healing, zero-downtime, zero-knowledge. |

### Complexity & worth — *is this complexity earning its keep?*

| Skill | Readme | Use it to |
| :---- | :----- | :-------- |
| [structural-simplification](./structural-simplification/SKILL.md) | [READ](./.documentation/READ-structural-simplification.md) | Compare two designs along four independent axes — diversity, coupling, depth, parts — so "this is simpler" becomes a measurable claim instead of a feeling. |
| [functionality-complexity-tradeoff](./functionality-complexity-tradeoff/SKILL.md) | [READ](./.documentation/READ-functionality-complexity-tradeoff.md) | Decide whether to BUILD / DEFER / DROP a proposed feature, or KEEP / SIMPLIFY / DELETE / OBSOLETE existing code — via a necessity gate followed by a worth ledger. |

### System flow — *is the work itself the right work?*

| Skill | Readme | Use it to |
| :---- | :----- | :-------- |
| [system-optimization](./system-optimization/SKILL.md) | [READ](./.documentation/READ-system-optimization.md) | Run optimization in the right order — question, delete, simplify, speed up, automate — instead of caching or parallelizing work that should have been deleted. |

### Meta-layer — *how do the skills themselves improve?*

| Skill | Readme | Use it to |
| :---- | :----- | :-------- |
| [continuous-improvement](./continuous-improvement/SKILL.md) | [READ](./.documentation/READ-continuous-improvement.md) | Decide whether a correction becomes a test, a linter rule, or a SKILL edit — and which SKILL owns it — without letting the SKILL library bloat. |

## How the skills compose

```
geometric-architecture → architecture-guidelines → structural-simplification → system-optimization
   (place / locality)         (build cleanly)         (evaluate complexity)        (improve flow)
```

`geometric-architecture` answers **where** a component belongs — its address on
the grid and which neighbors it may couple to. `architecture-guidelines`
answers **how** to build it. `structural-simplification` answers **whether**
the result is too complex. `system-optimization` answers **how to make its
operations flow**.

The two `architecture-as-code-*` skills are the enforcement mechanism for the
first two — they convert prose architectural rules into build-time failures.

`functionality-complexity-tradeoff` complements the pipeline by deciding
**whether** a piece of functionality is worth its cost — both prospectively
(build / defer / drop) and retrospectively (keep / simplify / delete) —
consuming complexity measurements from `structural-simplification`.

`defect-shift-left` and `ci-cd-reliability-architecture` apply the same
discipline to the pipeline that produces and ships the code: catch defects
early, ship safely.

`continuous-improvement` is the meta-layer that evolves the skills themselves
when reality disagrees with them.

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
