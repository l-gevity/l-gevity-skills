---
name: requirements-traceability
description: >-
    Maintains bidirectional traceability between canonical requirements and
    implementation, verification, decision, and operational evidence. Use when
    planning, implementing, reviewing, or closing work that must prove which
    requirement authorized a change, where it is implemented, which executed
    evidence verifies it, what remains unmapped, or whether references have
    gone stale. Do not use to invent requirement meaning, normalize the
    requirement graph, or decide implementation readiness.
---

# Requirements Traceability

Keep requirement intent connected to implementation and executed evidence
without turning code, tests, or a trace registry into a second requirements
source.

> **Core Directives**
>
> 1. **Canonical requirements keep meaning.** Trace links identify evidence;
>    they never authorize new product, policy, legal, or domain behavior.
> 2. **Trace both directions.** Check requirement to evidence and changed
>    artifact to requirement or an explicit non-requirement rationale.
> 3. **Implementation is not verification.** A code anchor or test definition
>    proves coverage exists; only an executed passing result proves verification.
> 4. **Place anchors naturally.** Prefer stable IDs in contracts, tests, ADRs,
>    operations evidence, and issue closeout over a duplicate central registry.
> 5. **Fail on stale references.** Unknown IDs, removed criteria, ambiguous
>    aliases, and unverifiable success claims are blocking trace defects.

## Boundary

Use this skill after a passing `implementation-readiness` decision when work
enters architecture, implementation, verification, review, or closeout.

Use `requirements-grounding` to establish meaning and authority,
`requirements-topology` to own IDs, relationships, lineage, schemas, and
generated views, and `implementation-readiness` to decide whether work may
start. Apply the project's requirements profile for repository paths, ID
formats, evidence stores, commands, and classifications.

This skill owns live evidence relationships. It does not add another stage or
letter to A.L.C.H.E.M.Y.

## Minimum Inputs

Require:

- canonical requirement and acceptance-criterion IDs;
- the passing readiness decision and admitted slice;
- the changed implementation, contract, decision, or operations artifacts;
- the project's accepted anchor forms and executable verification sources;
- commit, build, run, or environment identity when operational evidence is
  offered as proof.

If canonical IDs or criterion references are unstable, return to
`requirements-topology`. If the admitted slice or acceptance conditions are
unclear, return to `implementation-readiness`.

## Evidence States

Classify every criterion independently:

| State | Required evidence | What it does not prove |
| --- | --- | --- |
| `unmapped` | No accepted implementation or verification anchor | Whether work is planned elsewhere |
| `implemented` | Stable implementation anchor or executable test definition | That the behavior passed |
| `verified` | Implemented anchor plus a passing test or accepted operational result for this revision | Continued correctness after later changes |
| `blocked` | Named missing dependency, decision, environment, or evidence owner | That the requirement may be silently skipped |
| `not-applicable` | Explicit scoped rationale approved by the requirement owner | A general waiver for other slices or actors |

A passed test tag without a matching test definition is not verification. A test
definition without a result is implementation evidence only. Operational
evidence without revision and run identity is an observation, not reproducible
proof.

## Workflow

1. Resolve the canonical requirement set, version, and admitted slice.
2. Inventory changed or planned artifacts at public boundaries: contracts,
   commands, events, exports, routes, domain rules, migrations, tests, ADRs,
   runbooks, and deployment evidence.
3. Reuse stable requirement and criterion IDs; resolve aliases only through the
   canonical lineage model.
4. Place the smallest useful anchor in the artifact a maintainer will inspect
   first.
5. Map each criterion to implementation and verification evidence separately.
6. Reverse-check each non-trivial changed artifact for a requirement ID or an
   explicit `platform`, `operations`, `technical-debt`, `spike`, or
   `product-gap` rationale.
7. Classify gaps and stale references.
8. Run the repository's blocking trace check and the closest behavior tests.
9. Emit the trace decision and unresolved owners before closeout.

## Anchor Placement

| Artifact | Preferred stable anchor |
| --- | --- |
| Contract or public API | Requirement ID in schema metadata, operation metadata, or contract test |
| Domain behavior | Named rule/function plus a criterion-tagged behavior test |
| UI or workflow | Stable route/action/state identifier plus acceptance test |
| Data or migration | Schema/migration identifier plus compatibility or migration test |
| ADR or architecture record | Requirement IDs in the decision context |
| Operations | Runbook/check identifier plus revision, environment, run, and outcome |
| Issue or change record | Canonical IDs, admitted slice, evidence links, and named gaps |

Do not add long requirement prose to source files when the ID and a nearby
contract or test already preserve the relationship.

## Gap Taxonomy

| Gap | Meaning |
| --- | --- |
| `missing-requirement` | Work may be justified but has no canonical requirement or accepted rationale |
| `missing-implementation` | Requirement exists but no implementation anchor covers it |
| `missing-test` | Implementation exists but no executable verification covers it |
| `stale-reference` | Anchor targets an unknown, replaced, or removed ID or criterion |
| `scope-deferred` | Work is intentionally later and cites an accepted deferral |
| `decision-blocked` | An unresolved product, policy, platform, or ownership decision blocks proof |
| `evidence-unreproducible` | Claimed evidence lacks revision, run, environment, or result identity |

## CI Enforcement

Put deterministic trace checks in the earliest capable blocking gate:

- validate anchor syntax while authoring when editor tooling can do so;
- reject unknown IDs, criteria, aliases, and stale references in static CI;
- require criterion-tagged tests to exist before accepting test-result tags;
- ingest executed test results before promoting `implemented` to `verified`;
- require operational evidence to carry revision and run identity;
- report coverage counts, but never convert a percentage target into invented
  requirement meaning.

Keep fast local checks for feedback and a full-repository CI backstop for
unbypassable coverage. Route gate placement through `defect-shift-left`.

## Output Contract

```text
Subject:             <change, slice, release, or requirement scope>
Decision:            TRACEABLE | PARTIAL | BLOCKED
Canonical source:    <requirement set and version>
Requirement IDs:     <IDs covered>
Implemented:         <criteria count and anchors>
Verified:            <criteria count and executed evidence>
Reverse-trace gaps:  <changed artifacts without requirement/rationale>
Stale references:    <none or exact references>
Other gaps:          <gap taxonomy entries and owners>
Next action:         <implement, test, decide, repair reference, or close>
Verification:        <trace check and tests run, or Not run + reason>
```

For implementation or review closeout, append a compact note:

```text
Trace:
- Source: <requirement set, issue, or admitted slice>
- IDs: <requirement and criterion IDs>
- Implementation: <stable artifacts>
- Evidence: <executed tests or operational results>
- Gaps/deferred: <none or named gaps>
```

## Guardrails

- Do not mark a requirement verified because code, a route shell, a fixture, or
  a test definition exists.
- Do not use issue text as canonical when it conflicts with requirements.
- Do not hide unrelated work under a convenient requirement ID.
- Do not duplicate every trace edge in a giant registry and nearby artifacts.
- Do not recycle IDs; follow topology lineage after splits, merges, and
  replacements.
- If grounding, topology, or readiness changes materially, invalidate or refresh
  affected trace decisions.

## See also

- `requirements-grounding` — requirement meaning, source authority, and evidence.
- `requirements-topology` — stable IDs, lineage, graph semantics, and repository gates.
- `implementation-readiness` — admitted implementation slice and verification obligations.
- `defect-shift-left` — earliest blocking placement for trace checks.
