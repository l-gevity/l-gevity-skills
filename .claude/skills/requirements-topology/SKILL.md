---
name: requirements-topology
description: >-
    Structures validated requirements into an atomic, traceable, typed dependency
    graph and derives a trustworthy dependency order. Use when normalizing
    requirement wording, preserving stable IDs, splitting or merging requirements,
    modeling dependencies and constraints, detecting duplicates, conflicts,
    cycles, orphans, stale references, or missing verification, refining
    requirement-scope boundaries, or producing a graph package. Do not use for
    initial problem discovery or implementation planning.
---

# Requirements Topology

Turn grounded requirement candidates into a stable graph whose structure can be
inspected, challenged, and used for sequencing without changing requirement
meaning.

> **Core Directives**
>
> 1. **Grounding remains canonical.** The topology is a derived view, not a new
>    source of truth.
> 2. **Reuse stable IDs.** Preserve readable slugs through every derived artifact.
> 3. **One node, one obligation or outcome.** Split compound nodes before adding
>    edges.
> 4. **Type and evidence every relationship.** Prose-only dependencies are hidden
>    coupling.
> 5. **Order is derived, not authored.** Compute build order from `depends_on`
>    edges; never infer dependencies from document order.
> 6. **Graph structure is not software architecture.** An edge does not imply an
>    API, event, service, or deployment boundary.
> 7. **Operationalize one canonical model.** Schemas, semantic checks, generated
>    views, and CI gates must derive from the same requirement source instead of
>    creating parallel authorities.

## Boundary

Use `requirements-grounding` first when the problem, actor, basis, scope,
priority, complete-when conditions, or validation decision is unclear. Use
`implementation-readiness` after this skill when developers and architects need
capabilities, slices, contracts, ADR seeds, tests, or a readiness decision.

Read project instructions, domain glossaries, source catalogs, and policy files
before structuring domain requirements. Preserve project terminology and source
hierarchy, but keep domain policy out of this generic model.

This topology describes requirement relationships, not component placement. Do
not assign Domain / abstraction tier / layer coordinates here; use
`morphogenetic-architecture` when software components need placement,
observed-field analysis, or import constraints.

## Requirement Record

Normalize each requirement into this minimal record:

```yaml
id: readable-slug
statement: One atomic, solution-free outcome or obligation
actor: one actor
role: foundation | workflow | output | constraint | evidence-primitive | decision-input
kind: capability | business-rule | data | integration | security | compliance | operational
requirement_scope: owning problem scope or foundation capability
priority: must | should | could | won't-now
status: draft | accepted | deprecated | superseded
basis: authoritative | interpreted | evidenced | hypothesized
source_refs: []
complete_when_ref: requirement source location
notes: ""
```

Use project-defined labels when present. Keep the structural role and the domain
kind separate: `constraint` explains how a node behaves in the graph; `security`
may explain its subject.

Do not create a second acceptance-criterion scheme. Grounding's complete-when
conditions are the acceptance criteria. Reference them and flag gaps.

## Edge Taxonomy

Use typed directed edges and keep direction consistent:

```text
A depends_on B      # A cannot be satisfied unless B exists first
A enables B         # A makes B possible but is not strictly required
A constrains B      # A limits valid ways to satisfy B
A verifies B        # A proves or checks B
A produces B        # A creates an output or state consumed by B
A duplicates B      # A likely overlaps B
A conflicts_with B  # A and B cannot both hold without a decision
A refines B         # A is a more specific expression of B
```

Default presentation direction: `A -> B` means “A depends on B.” Label the
direction wherever ambiguity is possible. Mark inferred edges and state why the
inference is necessary.

Treat `depends_on` as an acyclic projection. Runtime or business feedback loops
may exist, but they must not be disguised as static prerequisite cycles.

## Workflow

1. Inventory grounded requirements and their source artifacts.
2. Reuse current readable slug IDs. Mint new slugs only for genuine splits,
   merges, or newly inferred requirements; record lineage.
3. Normalize each statement into one atomic outcome without changing meaning.
4. Reference the existing complete-when conditions and flag unusable or missing
   verification.
5. Assign role, kind, requirement-scope owner, priority, status, basis, and source
   lineage.
6. Add typed edges supported by source evidence or an explicit inference note.
7. Run graph checks before deriving order.
8. Refine module boundaries by cohesion: data ownership, decision owner,
   lifecycle, change reason, and test surface.
9. Topologically sort the `depends_on` projection.
10. Produce the smallest output mode that answers the user's decision.

## Graph Checks

Check explicitly for:

- missing, duplicate, or opaque IDs;
- compound requirements that need splitting;
- orphan nodes with no justified independence;
- cycles in the prerequisite projection;
- duplicate or conflicting requirements;
- requirements without usable complete-when conditions;
- stale references after renames, splits, or merges;
- constraints hidden inside workflow prose;
- external prerequisites without an owner or minimal contract;
- source references that no longer match the grounding artifact;
- requirement-scope clusters with mixed owners, lifecycles, or test surfaces.

Do not delete a requirement merely because it looks redundant. Mark the edge,
preserve lineage, and propose the consolidation decision.

## Repository Operationalization

When requirements live in a repository, keep four concerns explicit:

1. **Canonical inputs** own meaning and accepted relationships. Human-authored
   requirement text and structured metadata must agree or fail validation.
2. **Schema validation** checks record shape, required fields, enums, and ID
   syntax as early as editor tooling permits and again in blocking CI.
3. **Semantic validation** checks global uniqueness, criterion IDs, reference
   resolution, alias ambiguity, lineage, dependency cycles, ownership, and
   cross-record invariants that a file schema cannot prove.
4. **Generated views** such as registers, diagrams, dependency order, code
   constants, and summaries are deterministic, marked read-only, and checked for
   drift in CI.

Keep requirement status, approval, readiness, implementation, and verification
as independent facts. For example, an approval state may require an approval
date, but it never implies implementation or passed evidence.

Use stable acceptance-criterion IDs when downstream tests or evidence must
reference individual completion conditions. Preserve active IDs across edits;
record aliases, splits, merges, replacements, and deprecated criteria without
recycling identifiers.

For migrations, freeze the imported source with a revision or checksums, keep an
old-to-new ID/path map, prove structural and semantic equivalence, and remove the
temporary importer after the canonical source and rollback evidence are durable.

The repository gate should expose separate commands or phases for validation,
generation, generated-drift checking, and traceability. A single aggregate
requirements check should run them at the earliest project validation stage and
again as an unbypassable CI backstop. Use `requirements-traceability` for live
implementation and executed-evidence relationships.

## Requirement-Scope Heuristics

Group requirements when they share data ownership, decision ownership,
lifecycle, change reason, and test surface. Split when outputs, owners,
persistence lifecycles, or verification strategies differ materially.

Promote a shared foundation only when multiple requirement scopes genuinely depend on it.
If the second consumer is speculative, keep the prerequisite local until the
reuse is real.

Use `structural-simplification` when a proposed regrouping claims to reduce
complexity. Report its exact coder-facing fields: Component-kinds Δ,
Dependency-edges Δ, Max-chain-depth Δ, and Module-count Δ. Do not substitute
visual neatness for those measurements.

## Modes

- **Analysis**: report inventory, proposed nodes and edges, graph issues, and
  recommended changes without editing the source.
- **Hybrid**: produce analysis, then apply only small unambiguous source edits
  such as IDs, headings, or explicit constraint labels.
- **Patch**: update canonical requirements directly only when the user requests
  source edits and the meaning is settled.
- **Graph package**: produce the normalized topology consumed by
  `implementation-readiness`.

## Output Contract

Every application emits a decision record before any longer graph package:

```text
Subject:           <requirement scope or source set>
Mode:              analysis | hybrid | patch | graph-package
Decision:          STABLE | NEEDS-REFACTOR | BLOCKED
Canonical source:  <grounding artifact and version>
Graph size:        <node count / typed-edge count>
Cycle:             Pass | Fail | Not evaluated
Blocking issues:   <IDs, cycles, conflicts, verification, ownership, or lineage>
Inferred edges:    <count and evidence status>
Repository gate:   <schema / semantics / generated drift / not configured>
Next action:       <split, merge, source, decide, fix cycle, or run implementation-readiness>
Verification:      <graph checks and source comparisons run, or Not run + reason>
```

A full graph package additionally contains:

```text
Requirements topology:
- Meta-context:             # standalone artifacts only
- Reader guide:
- Source and lineage:
- Transformations:          # real splits, merges, inferred requirements
- Vocabulary:               # roles, edge types, graph direction
- Requirement records:
- Edge list:                # single source for relationships + evidence
- Dependency order:         # lean derived view of depends_on
- Diagram:                  # optional faithful derived view
- Attention list:           # issue | decision | watch
```

Keep one place per fact:

- Put relationship evidence in the edge list, not in repeated dependency columns.
- Keep dependency order as an ordered list without repeating its edges.
- Include a Mermaid diagram only when it faithfully represents the relevant edge
  list; omit a decorative or lossy graph.
- Keep historical slugs in lineage only. Use current slugs everywhere active.
- Collapse graph issues, open decisions, and source-watch items into one typed
  attention list.

For a standalone artifact, state audience, purpose, completion date, canonical
source, source currency, and caveats once near the top.

## Guardrails

- Do not rewrite legal, contractual, product, or stakeholder meaning to make the
  graph cleaner.
- Do not infer service boundaries, synchronous calls, or event flows from graph
  edges.
- Do not hide uncertainty by converting an inference into a source fact.
- Do not claim the graph is stable while cycles, must-have verification gaps, or
  unresolved ID transformations remain.
- Do not report a cycle failure without inspecting the `depends_on` projection;
  use `Not evaluated` and name the missing graph input instead.
- Do not hand-edit generated views or let them become a competing requirement
  source.
- If grounding changes materially, refresh the topology or state exactly what is
  stale.
