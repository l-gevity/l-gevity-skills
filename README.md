# The L-GEVITY Essential Software Architecture Skills

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

## Overview

Ten skills, organized into five clusters. Each cluster answers a different
question about a system; together they cover the lifecycle from "where does
this component belong?" through "is it worth keeping?" to "how does the team
keep getting better?"

Each skill ships as a `SKILL.md` (the operational reference) paired with a
`READ-<skill>.md` primer in [`../documentation/`](../documentation/) (the
plain-English overview).

## Architectural foundations — *what should the system look like?*

### First principles for module design

| Name | Readme | Use it to |
| :--- | :----- | :-------- |
| [architecture-guidelines](./architecture-guidelines/SKILL.md) | [READ-architecture-guidelines.md](../documentation/READ-architecture-guidelines.md) | Test every module decision — minimalism, modularity, functional core, resilience, naming, concurrency — against a first-principles checklist before code is written. |

### Locality as a first principle

| Name | Readme | Use it to |
| :--- | :----- | :-------- |
| [geometric-architecture](./geometric-architecture/SKILL.md) | [READ-geometric-architecture.md](../documentation/READ-geometric-architecture.md) | Place a component on the `(X, Y, Z)` grid, and audit existing graphs for layer skips, cycles, god cells, and cross-domain coupling. |

## Architectural enforcement — *how do we make the rules stick?*

### Architecture as a build step (JavaScript / TypeScript)

| Name | Readme | Use it to |
| :--- | :----- | :-------- |
| [architecture-as-code-javascript](./architecture-as-code-javascript/SKILL.md) | [READ-architecture-as-code-javascript.md](../documentation/READ-architecture-as-code-javascript.md) | Encode the allowed imports between modules so architectural violations fail `eslint` instead of slipping through review. |

### Architecture as a build step (Python)

| Name | Readme | Use it to |
| :--- | :----- | :-------- |
| [architecture-as-code-python](./architecture-as-code-python/SKILL.md) | [READ-architecture-as-code-python.md](../documentation/READ-architecture-as-code-python.md) | Encode the allowed imports between Python packages — via per-package `architecture.toml` files — so violations fail `import-linter` instead of slipping through review. |

## Pipeline reliability — *how do we catch defects early and ship safely?*

### Catch every defect at the earliest stage it can technically run

| Name | Readme | Use it to |
| :--- | :----- | :-------- |
| [defect-shift-left](./defect-shift-left/SKILL.md) | [READ-defect-shift-left.md](../documentation/READ-defect-shift-left.md) | Audit your pipeline for shift-left opportunities, and decide where any new check belongs — type system, lint, pre-commit, CI gate, or beyond. |

### Pipelines safe to retry, immutable artifacts, no stored secrets

| Name | Readme | Use it to |
| :--- | :----- | :-------- |
| [ci-cd-reliability-architecture](./ci-cd-reliability-architecture/SKILL.md) | [READ-ci-cd-reliability-architecture.md](../documentation/READ-ci-cd-reliability-architecture.md) | Design or audit a CI/CD pipeline against six rules: idempotent, self-contained, immutable artifacts, self-healing, zero-downtime, zero-knowledge. |

## Complexity & worth — *is this complexity earning its keep?*

### Make "simpler" a measurable, falsifiable claim

| Name | Readme | Use it to |
| :--- | :----- | :-------- |
| [structural-simplification](./structural-simplification/SKILL.md) | [READ-structural-simplification.md](../documentation/READ-structural-simplification.md) | Compare two designs along four independent axes — diversity, coupling, depth, parts — so "this is simpler" becomes a measurable, comparable claim instead of a feeling. |

### Necessity gate, then worth ledger

| Name | Readme | Use it to |
| :--- | :----- | :-------- |
| [functionality-complexity-tradeoff](./functionality-complexity-tradeoff/SKILL.md) | [READ-functionality-complexity-tradeoff.md](../documentation/READ-functionality-complexity-tradeoff.md) | Decide whether to BUILD / DEFER / DROP a proposed feature, or KEEP / SIMPLIFY / DELETE / OBSOLETE existing code — via a necessity gate followed by a worth ledger. |

## System flow — *is the work itself the right work?*

### Question, delete, simplify, speed up, automate — in that order

| Name | Readme | Use it to |
| :--- | :----- | :-------- |
| [system-optimization](./system-optimization/SKILL.md) | [READ-system-optimization.md](../documentation/READ-system-optimization.md) | Run optimization in the right order — question, delete, simplify, speed up, automate — instead of caching or parallelizing work that should have been deleted. |

## Meta-layer — *how do the skills themselves improve?*

### Update the SKILLs at the root cause, not the symptom

| Name | Readme | Use it to |
| :--- | :----- | :-------- |
| [continuous-improvement](./continuous-improvement/SKILL.md) | [READ-continuous-improvement.md](../documentation/READ-continuous-improvement.md) | Decide whether a correction becomes a test, a linter rule, or a SKILL edit — and which SKILL owns it — without letting the SKILL library bloat. |

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
