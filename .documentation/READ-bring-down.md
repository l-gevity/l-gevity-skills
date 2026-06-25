# Bring-Down

An improvement SKILL for moving bespoke, duplicated, or over-local code down
into externally maintained reusable capability: framework-native features,
approved libraries, external standards, platform products, or managed services.

## Why use this

- It gives the third axis in the improvement trio:
  `defect-shift-left`, `push-out`, and `bring-down`.
- It prevents premature platform/library moves by requiring maintenance-burden,
  repetition, commodity-fit, or risk evidence.
- It rejects same-owner componentization and patternization; those belong to
  the architecture skills unless an external/library/platform landing exists.
- It makes replacement accountable by requiring migration and custom-code
  retirement.
- It searches the current technology stack first for existing lower placements
  before creating or buying anything new.
- It searches current external services only after L0 SRVC managed-service
  replacement is plausible.
- It separates reuse altitude from geometric placement: `bring-down` chooses
  reuse level; `geometric-architecture` chooses coordinates and dependency
  rules.

## The scale

| Level | Name |
| ----- | ---- |
| **L4 CODE** | Custom code maintained by this codebase/team |
| **L3 LIB** | Approved package, framework API, SDK feature, or shared capability |
| **L2 STD** | External standard, framework convention, generator, policy, or reference architecture |
| **L1 PLP** | Internal platform product maintained outside this codebase |
| **L0 SRVC** | External service or managed commodity |

The useful question is: what is the lowest responsible level this capability
can live at without hiding real variation?

## How to use

1. Define the scope: repos, modules, services, teams, or workflows.
2. Find copy/paste code, repeated scripts, repeated PR shapes, local wrappers,
   and one-off infra/app patterns.
3. Delete obsolete or non-problem-solving code first.
4. Search the current stack for lower owner-changing placements: approved
   libraries, framework-native capabilities, external standards, platform
   products, or approved services.
5. Compare commonality and variation.
6. Assign current level and target level with evidence.
7. Name the exact landing capability and maintenance owner.
8. Exclude same-team shared helpers, templates, manifests, scripts, or patterns;
   hand them to architecture/refactor skills instead.
9. Move down one level, unless an intermediate level is already satisfied.
10. Migrate at least one real consumer and retire the old custom path.

When target L0 SRVC is plausible and the user asks for service alternatives,
first check whether the current stack already has an approved service. If not,
search current primary sources: official docs, pricing, SLA, security,
compliance, and migration guides. Compare external managed services against
keeping the capability local, using L3 LIB, or using L1 PLP.

Example prompt:

> "Use `bring-down` to review repeated deployment scripts across these repos.
> Identify current level, target level, exact landing capability, owner change,
> variation risk, and custom paths to retire."

## When to combine it

- Use `functionality-complexity-tradeoff` before replacing code to confirm the
  duplicated functionality should exist.
- Use `structural-simplification` to verify the externalization lowers real
  complexity.
- Use `geometric-architecture` after bring-down chooses a reuse level, so the
  resulting component gets the correct domain/tier/layer placement.
- Use `push-out` when the issue is recurring manual work rather than code
  shape.
- Use `defect-shift-left` when the issue is late defect detection.
- Use `architecture-as-code` when an accepted pattern should be enforced.

## Next steps

- See [SKILL.md](../.claude/skills/bring-down/SKILL.md) for the full scale,
  triggers, protocol, anti-patterns, and output contract.
