# L-GEVITY Software Architecture Skills
 
[![image](overview-abstract.png)](overview.png)
 
**The architect for your AI coding agent.**
 
Most agent skills teach an AI *how* to do specific tasks — write tests, scaffold
boilerplate, format code. **L-GEVITY skills do something different.** They teach
an agent how to *think* about software at a structural level. They are the
architect on your project: the voice that asks whether a feature earns its
complexity, whether a pipeline is truly idempotent, whether a structure can be
simpler before it's optimized.
 
Open-source, platform-agnostic skills for software architecture, CI/CD
reliability, structural simplification, system optimization, and continuous
improvement. Drop them into any project, and any compatible agent.
 
## Compatible with the open Agent Skills standard
 
These skills follow the [Agent Skills standard](https://agentskills.io/) — a
lightweight, open format originally developed by Anthropic and now adopted across
the agent ecosystem. They work natively with:
 
- [**Claude Code**](https://claude.ai/claude-code) — Anthropic's coding agent
- [**Google Antigravity**](https://antigravity.google) — Google's agent-first IDE
- [**OpenCode**](https://opencode.ai) — open-source terminal agent
- Any other tool that supports `SKILL.md` (Cursor, Codex CLI, Gemini CLI,
  Kimi CLI, and a [growing list](https://agentskills.io/clients) of others)
## What makes these different
 
Most skill libraries are **tactical**: recipes for specific tasks. **L-GEVITY
skills are strategic.** They encode the architect's job:
 
- **Decide what to build** — `functionality-complexity-tradeoff` forces the
  question "is this feature worth its cost?" before code gets written, and
  again after, when deciding what to keep, simplify, or delete.
- **Decide how to structure it** — `architecture-guidelines` enforces
  consistency, minimalism, reliability, and traceability across every component
  touched.
- **Decide how to simplify it** — `structural-simplification` reduces complexity
  from first principles, across code, data, workflows, and UI.
- **Decide how to keep it reliable** — `ci-cd-reliability-architecture` builds
  pipelines that are idempotent, self-healing, and zero-downtime by default.
- **Decide how to improve it** — `system-optimization` applies Lean, Kaizen,
  Six Sigma, Theory of Constraints, and DevOps to eliminate waste and improve
  flow.
- **Decide how the skills themselves should evolve** — `continuous-improvement`
  makes the skill set self-correcting through feedback and root-cause analysis.
The result: an agent that doesn't just *write* your code, but argues with you
about whether the code should exist — and whether it should look the way you
proposed.
 
## Quick start
 
### As a git submodule (recommended)
 
```bash
git submodule add https://github.com/l-gevity/l-gevity-skills \
  .claude/skills/l-gevity-skills
```
 
For Antigravity, replace `.claude/skills/` with `.agent/skills/`. For OpenCode,
either path works (it discovers both).
 
Reference the skills you want from your agent's instructions file
(`CLAUDE.md`, `AGENT.md`, `AGENTS.md`, etc.):
 
```markdown
- [architecture-guidelines](./.claude/skills/l-gevity-skills/architecture-guidelines/)
- [functionality-complexity-tradeoff](./.claude/skills/l-gevity-skills/functionality-complexity-tradeoff/)
- [structural-simplification](./.claude/skills/l-gevity-skills/structural-simplification/)
```
 
For new clones, initialize the submodule:
 
```bash
git clone --recurse-submodules <your-repo>
# or, if already cloned:
git submodule update --init
```
 
Pull the latest skill updates:
 
```bash
git submodule update --remote .claude/skills/l-gevity-skills
```
 
### Manual copy
 
Alternatively, copy individual skill directories straight into your skills
folder.
 
## Use cases
 
A few of the situations these skills are built for:
 
- **Before adding a feature.** You ask the agent to build something new. Instead
  of jumping to code, it weighs the feature's value against its complexity cost
  and proposes a smaller version — or pushes back entirely.
  *(`functionality-complexity-tradeoff`)*
- **Reviewing a pull request.** You ask the agent to review a diff. It checks
  the change against architectural principles — consistency with existing
  patterns, minimalism, reliability, traceability — and flags structural
  problems, not just style.
  *(`architecture-guidelines`)*
- **Cleaning up a tangled module.** You point the agent at code that has grown
  unwieldy. It applies a first-principles complexity reduction pass — collapsing
  redundant structures, flattening unnecessary indirection — before any
  optimization work begins.
  *(`structural-simplification`)*
- **Hardening a CI/CD pipeline.** You ask why deploys are flaky. The agent
  audits the pipeline for non-idempotent steps, mutable artifacts, hidden state,
  and missing self-healing — then proposes the minimum set of fixes for
  zero-downtime reliability.
  *(`ci-cd-reliability-architecture`)*
- **Speeding up a slow system.** You ask the agent to make something faster.
  It identifies the actual constraint using Theory of Constraints and Lean
  principles, instead of optimizing whatever happens to be most visible.
  *(`system-optimization`)*
- **Deciding what to delete.** You ask "should we keep this?" about an
  underused feature or legacy module. The agent evaluates it the same way it
  evaluates new features — and gives you a defensible keep / simplify / delete
  call.
  *(`functionality-complexity-tradeoff`)*
- **Improving the skills themselves.** When a skill gives bad advice, you say
  so. The agent runs root-cause analysis on the skill's instructions and
  proposes an edit, so the same mistake doesn't recur.
  *(`continuous-improvement`)*

## Skills

Eleven skills, organized into seven groups by the question each one answers.
Every skill ships as a `SKILL.md` (the operational reference); a matching
`READ-<skill>.md` primer in [`./.documentation/`](./.documentation/) gives the
plain-English overview.

### The orchestrator — *which skills to run, in which order?*

| Skill | Readme | Use it to |
| :---- | :----- | :-------- |
| [design-and-refactor](./design-and-refactor/SKILL.md) | [READ](./.documentation/READ-design-and-refactor.md) | Sequence the other skills into a deterministic seven-gate flow — necessity → first principles → placement → complexity → enforcement → shift-left → optimization — so enforcement never precedes design and speculative generality is caught at Gate 1, not after a rewrite. |

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

`design-and-refactor` is the orchestration layer above all of the above. It
codifies the order in which the other skills fire — upstream gates (necessity,
first principles, placement, complexity) shape what gets built; downstream
gates (architecture-as-code, defect-shift-left) enforce what was decided. The
audit-mode inversion runs the same skills in reverse to drive
delete-or-simplify verdicts on existing code.

`continuous-improvement` is the meta-layer that evolves the skills themselves
when reality disagrees with them.

## License

[MIT](./LICENSE)


