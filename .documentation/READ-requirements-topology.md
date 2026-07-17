# Requirements Topology

A requirements document is a list; delivery depends on a graph. Requirements
Topology makes prerequisites, constraints, evidence, conflicts, and shared
foundations explicit without turning them prematurely into software architecture.

## Why use this

- Normalize compound or inconsistent requirements into atomic nodes.
- Preserve readable IDs and source lineage through splits and merges.
- Replace prose-only dependencies with typed, evidenced edges.
- Detect cycles, orphans, duplicates, conflicts, stale references, and missing
  verification.
- Derive dependency order from the graph instead of document order or intuition.

## Fundamental principle

The graph is a derived view of grounded requirements. It may expose defects in the
source, but it does not become a competing requirements source and it does not
change meaning to produce a neater diagram.

Default graph direction is explicit:

```text
A -> B means A depends_on B
```

Other edge types express `enables`, `constrains`, `verifies`, `produces`,
`duplicates`, `conflicts_with`, and `refines`. Inferred edges remain labeled as
inferences.

## How to use

Ask the agent to analyze or package a grounded requirement set:

> “Build a typed requirements topology from these validated requirements. Find
> cycles, hidden constraints, duplicates, conflicts, and missing verification.”

> “Derive the dependency order for this requirement scope without inventing
> service or API boundaries.”

Use analysis mode for diagnosis, hybrid mode for small safe source corrections,
patch mode only when meaning is settled, and graph-package mode for implementation
readiness.

## One place per fact

- Requirement meaning and complete-when conditions remain in grounding.
- Relationship evidence lives in the edge list.
- Dependency order is a lean derived view.
- A diagram is included only when it faithfully represents the edge list.
- Issues, decisions, and watch items share one typed attention list.

This prevents three nearly identical representations from drifting apart.

## Repository enforcement

When requirements live in a repository, one canonical model should drive four
separate checks: file schema, cross-record semantic validation, deterministic
generated views, and generated-drift detection. Semantic checks cover unique
IDs, stable criterion references, aliases and lineage, unresolved edges,
dependency cycles, ownership, and other invariants a single-file schema cannot
prove.

Run the aggregate requirements check at the earliest project validation stage
and as a blocking CI backstop. Generated registers, diagrams, dependency order,
and code constants are read-only views. During migrations, freeze the imported
source, retain an old-to-new map, prove equivalence, and retire temporary import
code after the canonical source is durable.

## Output

The full package contains reader context, source lineage, genuine transformations,
graph vocabulary, normalized records, an evidenced edge list, dependency order,
an optional faithful diagram, and one attention list. Every use starts with a
`STABLE`, `NEEDS-REFACTOR`, or `BLOCKED` decision record containing graph size,
cycle status (`Pass`, `Fail`, or `Not evaluated`), blocking issues, the next
action, and verification performed. Unknown graph state is not a cycle failure.

## When to skip

Skip when the problem, actors, source basis, or completion conditions are still
unclear; use `requirements-grounding`. Skip when the topology is stable and the
task is to prepare developers and architects; use `implementation-readiness`.

## Next steps

- Read the operational [`requirements-topology` SKILL.md](../.claude/skills/requirements-topology/SKILL.md).
- Ground uncertain inputs with [`requirements-grounding`](../.claude/skills/requirements-grounding/SKILL.md).
- Maintain implementation evidence with [`requirements-traceability`](../.claude/skills/requirements-traceability/SKILL.md).
- Measure proposed regrouping with [`structural-simplification`](../.claude/skills/structural-simplification/SKILL.md).
