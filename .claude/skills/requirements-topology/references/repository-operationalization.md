# Requirements Topology — Repository Operationalization

Reference for [SKILL.md](../SKILL.md). Read when requirements live in a
repository, before filling the `Repository gate` line of the decision record.

## Four Responsibilities

When requirements live in a repository, keep four responsibilities explicit:

1. **Canonical inputs** own meaning and accepted relationships. Human-authored
   requirement text and structured metadata must agree or fail validation.
2. **Schema validation** checks record shape, required fields, enums, and ID
   syntax as early as editor tooling permits and again in blocking CI.
3. **Semantic validation** checks global uniqueness, criterion IDs, reference
   resolution, alias ambiguity, lineage, dependency cycles, ownership, aspect
   coverage (every scope a node's `holds_across` names receives a `constrains`
   edge from it), and cross-record invariants that a file schema cannot prove.
   For lineage: a
   record that names a replacement has its predecessor retired or lapsing; a
   lapsing record carries an expiry condition; lineage announced only in prose
   fails.
4. **Generated views** such as registers, diagrams, dependency order, code
   constants, and summaries are deterministic, marked read-only, and checked for
   drift in CI.

Keep requirement status, approval, readiness, implementation, and verification
as independent facts. For example, an approval state may require an approval
date, but it never implies implementation or passed evidence.

## Criterion IDs and Migrations

Use stable acceptance-criterion IDs when downstream tests or evidence must
reference individual completion conditions. Preserve active IDs across edits;
record aliases, splits, merges, replacements, and deprecated criteria without
recycling identifiers. Every deprecation record also names the implementation
artifacts reviewed against the retirement and an accountability reference for
the decision.

For migrations, freeze the imported source with a revision or checksums, keep an
old-to-new ID/path map, prove structural and semantic equivalence, and remove the
temporary importer after the canonical source and rollback evidence are durable.

## The Repository Gate

The repository gate should expose separate commands or phases for validation,
generation, generated-drift checking, and traceability. A single aggregate
requirements check should run them at the earliest project validation stage and
again as an unbypassable CI backstop.
