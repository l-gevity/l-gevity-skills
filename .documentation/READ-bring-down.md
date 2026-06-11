# Bring-Down

An improvement SKILL for moving bespoke, duplicated, or over-local code down
into reusable components, patterns, platform primitives, or managed services.

## Why use this

- It gives the third axis in the improvement trio:
  `defect-shift-left`, `push-out`, and `bring-down`.
- It prevents premature abstraction by requiring repetition evidence.
- It distinguishes componentizing, patternizing, platformizing, and replacing
  with a managed service.
- It makes extraction accountable by requiring migration and duplicate removal.
- It searches the current technology stack first for existing lower placements
  before creating or buying anything new.
- It searches current external services only after Level 0 managed-service
  replacement is plausible.
- It separates reuse altitude from geometric placement: `bring-down` chooses
  reuse level; `geometric-architecture` chooses coordinates and dependency
  rules.

## The scale

| Level | Name |
| ----- | ---- |
| **5** | One-off custom code |
| **4** | Repeated local pattern |
| **3** | Componentized |
| **2** | Patternized / templated |
| **1** | Platform primitive |
| **0** | Managed service / commodity |

The useful question is: what is the lowest responsible level this capability
can live at without hiding real variation?

## How to use

1. Define the scope: repos, modules, services, teams, or workflows.
2. Find copy/paste code, repeated scripts, repeated PR shapes, local wrappers,
   and one-off infra/app patterns.
3. Delete obsolete or non-problem-solving code first.
4. Search the current stack for existing lower placements: components,
   templates, platform primitives, approved services, or framework-native
   capabilities.
5. Compare commonality and variation.
6. Assign current level and target level with evidence.
7. Move down one level, unless an intermediate level is already satisfied.
8. Migrate at least one real consumer and retire the old duplicate path.

When target Level 0 is plausible and the user asks for service alternatives,
first check whether the current stack already has an approved service. If not,
search current primary sources: official docs, pricing, SLA, security,
compliance, and migration guides. Compare external managed services against
keeping the capability local, componentized, or as a platform primitive.

Example prompt:

> "Use `bring-down` to review repeated deployment scripts across these repos.
> Identify current level, target level, repetition evidence, variation risk,
> next bring-down move, and duplicate paths to retire."

## When to combine it

- Use `functionality-complexity-tradeoff` before extracting to confirm the
  duplicated functionality should exist.
- Use `structural-simplification` to verify extraction lowers real complexity.
- Use `geometric-architecture` after bring-down chooses a reuse level, so the
  resulting component gets the correct domain/tier/layer placement.
- Use `push-out` when the issue is recurring manual work rather than code
  shape.
- Use `defect-shift-left` when the issue is late defect detection.
- Use `architecture-as-code` when an accepted pattern should be enforced.

## Next steps

- See [SKILL.md](../.claude/skills/bring-down/SKILL.md) for the full scale,
  triggers, protocol, anti-patterns, and output contract.
