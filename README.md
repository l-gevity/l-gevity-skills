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

### Architectural foundations — *what should the system look like?*

- **[architecture-guidelines](./architecture-guidelines/SKILL.md)** —
  ([primer](../documentation/READ-architecture-guidelines.md)) A
  first-principles ruleset for module design. Minimalism, modularity,
  functional core, resilience, naming, concurrency — the things every module
  decision should test against before code is written.

- **[geometric-architecture](./geometric-architecture/SKILL.md)** —
  ([primer](../documentation/READ-geometric-architecture.md)) A 3-D spatial
  coordinate system for your dependency graph. Every component gets an
  address `(X, Y, Z)` and may only couple to face-adjacent neighbors;
  long-range and cyclic dependencies become structurally hard to express — the
  way a building's geometry resists impossible plumbing.

### Architectural enforcement — *how do we make the rules stick?*

- **[architecture-as-code-javascript](./architecture-as-code-javascript/SKILL.md)**
  — ([primer](../documentation/READ-architecture-as-code-javascript.md)) A
  build step that enforces your architectural rules (the dependency graph).
  You declare which modules may import from which; violations fail the build.

- **[architecture-as-code-python](./architecture-as-code-python/SKILL.md)** —
  ([primer](../documentation/READ-architecture-as-code-python.md)) A build
  step that enforces your architectural rules in Python. You declare which
  packages may import from which via per-package `architecture.toml` files; an
  assembler turns them into `import-linter` contracts and the build fails on
  violations.

### Pipeline reliability — *how do we catch defects early and ship safely?*

- **[defect-shift-left](./defect-shift-left/SKILL.md)** —
  ([primer](../documentation/READ-defect-shift-left.md)) A pipeline-design
  SKILL that places every defect-detection check at the earliest stage it can
  technically run. The cost of catching a defect grows geometrically with
  stage; catching it later is always a regression.

- **[ci-cd-reliability-architecture](./ci-cd-reliability-architecture/SKILL.md)**
  — ([primer](../documentation/READ-ci-cd-reliability-architecture.md)) A
  pipeline-design SKILL for builds and deployments that are safe to run any
  number of times, build artifacts once, deploy without downtime, and
  authenticate without storing secrets.

### Complexity & worth — *is this complexity earning its keep?*

- **[structural-simplification](./structural-simplification/SKILL.md)** —
  ([primer](../documentation/READ-structural-simplification.md)) Most refactors
  claim to simplify; most just relocate complexity. A four-axis vector —
  diversity, coupling, depth, parts — turns "simpler" from a feeling into a
  falsifiable claim.

- **[functionality-complexity-tradeoff](./functionality-complexity-tradeoff/SKILL.md)**
  — ([primer](../documentation/READ-functionality-complexity-tradeoff.md)) A
  first-principles SKILL for deciding whether a piece of functionality is
  worth keeping or building. Two stages: a *necessity gate* ("does the problem
  this code addresses actually occur in this stack?") followed by a *worth
  ledger* ("does the value justify the cost?").

### System flow — *is the work itself the right work?*

- **[system-optimization](./system-optimization/SKILL.md)** —
  ([primer](../documentation/READ-system-optimization.md)) Most optimization
  effort makes systems worse — because it speeds up the wrong thing, in the
  wrong order, at the wrong time. The correct sequence: question, delete,
  simplify, speed up, automate.

### Meta-layer — *how do the skills themselves improve?*

- **[continuous-improvement](./continuous-improvement/SKILL.md)** —
  ([primer](../documentation/READ-continuous-improvement.md)) A protocol for
  updating SKILL files when the agent makes a mistake. Trace each correction
  to its root cause; prefer a test or linter over a written rule; shrink the
  file before you grow it.

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
