# Requirements Traceability

Requirements Traceability keeps a requirement connected to implementation and
executed evidence after readiness has admitted work into architecture and build.
It prevents two common false claims: that a code anchor means the behavior was
tested, and that a test definition means the test passed for this revision.

## Why use this

- Check requirement-to-evidence and artifact-to-requirement coverage.
- Preserve canonical requirement meaning while implementation evolves.
- Distinguish `implemented` from `verified` per acceptance criterion.
- Catch unknown IDs, removed criteria, ambiguous aliases, and stale anchors.
- Classify legitimate non-requirement work without hiding orphaned product work.
- Make operational evidence reproducible through revision and run identity.

## Fundamental principle

Trace links are evidence, not authority. Canonical requirements define what is
needed; implementation and executed checks show how much of that need is covered
and proven now.

The skill uses five evidence states:

| State | Meaning |
| --- | --- |
| `unmapped` | No accepted implementation or verification anchor |
| `implemented` | Code/contract anchor or executable test definition exists |
| `verified` | Implementation exists and accepted evidence passed for this revision |
| `blocked` | A named dependency, decision, environment, or evidence owner blocks proof |
| `not-applicable` | A scoped, owner-approved rationale excludes this slice |

## How to use

Apply it after a passing `implementation-readiness` decision:

> “Trace this implementation slice bidirectionally. Separate implementation
> anchors from executed verification, reject stale IDs, and classify every gap.”

> “Review this change for reverse-trace gaps: which changed artifacts have no
> canonical requirement or accepted platform/operations rationale?”

The project's requirements profile supplies repository paths, ID syntax,
evidence stores, commands, and local classifications. The generic skill supplies
the trace method.

## CI enforcement

Use editor validation where possible and a blocking full-repository CI backstop.
Static checks reject unknown requirements, criteria, aliases, and stale
references. Test result ingestion may promote an implemented criterion to
verified only when a matching executable test definition exists and passed.
Operational evidence must include revision, environment, run, and outcome.

Coverage percentages are diagnostic; they do not invent missing requirement
meaning or silently waive intentionally deferred work.

## Output

Every use returns `TRACEABLE`, `PARTIAL`, or `BLOCKED`, along with canonical
source/version, requirement IDs, implemented and verified counts, reverse-trace
gaps, stale references, owners, the next action, and checks performed.

## When to skip

Use `requirements-grounding` when meaning or source authority is unresolved,
`requirements-topology` when IDs/lineage/relationships are unstable, and
`implementation-readiness` when no slice has been admitted into build yet.

## Next steps

- Read the operational [`requirements-traceability` SKILL.md](../.claude/skills/requirements-traceability/SKILL.md).
- Repair unstable IDs and graph lineage with [`requirements-topology`](../.claude/skills/requirements-topology/SKILL.md).
- Place deterministic trace checks with [`defect-shift-left`](../.claude/skills/defect-shift-left/SKILL.md).
