# Push-Out

A DevOps improvement SKILL for moving recurring operational work out of
individual memory, manual execution, ticket queues, and local team practice
into durable standards, platforms, self-service controls, and feedback loops.

## Why use this

- It exposes where toil lives today: individual, team, repo, platform,
  self-service, or adaptive system.
- It prevents automating chaos by requiring deletion and standardization before
  automation.
- It prunes prose documentation that only repeats code, config, tests,
  generated output, CI, policy-as-code, or architecture-as-code.
- It mirrors `defect-shift-left`: shift-left moves defect detection earlier;
  push-out moves recurring operational work outward.
- It pairs with `bring-down`: push-out moves work outward; bring-down lowers
  bespoke implementation into reusable capability.

## The ladder

| Rank | Location |
| ---- | -------- |
| **0** | Individual memory |
| **1** | Team procedure |
| **2** | Repo standard |
| **3** | Shared platform |
| **4** | Self-service control |
| **5** | Adaptive system |

## How to use

1. Define the scope: product, repo, platform, teams, environments, and time
   window.
2. Inventory recurring work: manual steps, tickets, approvals, deploy chores,
   incident repeats, dashboard checks, and hand-maintained config.
3. Delete work that no longer serves a real purpose.
4. Assign current push-out rank with evidence.
5. Set target rank by frequency, risk, blast radius, compliance, toil cost, and
   dependency count.
6. Emit one next move: document, standardize, platform, self-serve, or add
   feedback.
7. Prove the new path, then retire same-scope manual duplicates.
8. When executable sources already cover documentation mechanics, keep only
   intent, ownership, rationale, external constraints, rollback notes, and a
   link to the executable source.

Example prompt:

> "Use `push-out` to reduce deploy toil in this repo. Identify recurring manual
> work, current rank, target rank, evidence, next push-out action, and any
> manual duplicate to retire."

## When to combine it

- Use `defect-shift-left` when the improvement is about moving a check earlier.
- Use `bring-down` when the improvement is about replacing custom duplicated
  implementation with an approved library, external standard, platform product,
  or managed service.
- Use `system-optimization` when many push-out candidates compete and the
  constraint is unclear.
- Use `ci-cd-reliability-architecture` for deploy-path reliability findings.
- Use `continuous-improvement` when a recurring finding should become a skill,
  template, check, or build-time rule.

## Next steps

- See [SKILL.md](../.claude/skills/push-out/SKILL.md) for the full ladder,
  protocol, move patterns, anti-patterns, and output contract.
