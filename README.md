# L-GEVITY Skills

Open-source [Claude Code](https://claude.ai/claude-code) skills for software
architecture, CI/CD reliability, structural simplification, system optimization,
and continuous improvement.

These skills are platform-agnostic and can be used in any software project.

## About L-GEVITY

[L-GEVITY](https://l-gevity.com) is a longevity-focused health platform that
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
| [architecture-guidelines](./architecture-guidelines/SKILL.md) | Core architectural principles: consistency, minimalism, reliability, and traceability. Use when designing or modifying any system component. |
| [ci-cd-reliability-architecture](./ci-cd-reliability-architecture/SKILL.md) | Idempotency, self-containment, immutable artifacts, self-healing, zero-downtime, and zero-knowledge security for CI/CD pipelines. |
| [continuous-improvement](./continuous-improvement/SKILL.md) | Meta-learning protocol for evolving skills based on user feedback and root-cause analysis. |
| [structural-simplification](./structural-simplification/SKILL.md) | First-principles framework for reducing structural complexity in any domain — code, data models, workflows, UI layouts, org structures. |
| [system-optimization](./system-optimization/SKILL.md) | Lean, Kaizen, Six Sigma, Theory of Constraints, and DevOps principles to eliminate waste and improve flow. |

### Workflow

The architecture skills form a natural pipeline:

```
architecture-guidelines → structural-simplification → system-optimization
       (create)                  (evaluate)                 (improve)
```

Use `continuous-improvement` as a meta-layer to evolve the skills themselves.

## Usage

### As a git submodule (recommended)

Add this repo as a submodule inside your project's `.claude/skills/` directory:

```bash
git submodule add https://github.com/l-gevity/l-gevity-skills .claude/skills/l-gevity-skills
```

Then reference skills from your `CLAUDE.md`:

```markdown
- [architecture-guidelines](./.claude/skills/l-gevity-skills/architecture-guidelines/)
- [structural-simplification](./.claude/skills/l-gevity-skills/structural-simplification/)
```

For new clones, initialize the submodule:

```bash
git clone --recurse-submodules <your-repo>
# or if already cloned:
git submodule update --init
```

To pull the latest skill updates:

```bash
git submodule update --remote .claude/skills/l-gevity-skills
```

### Manual copy

Alternatively, copy individual skill directories into your `.claude/skills/`
folder.

## License

[MIT](./LICENSE)
