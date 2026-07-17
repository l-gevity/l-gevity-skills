---
name: implementation-readiness
description: >-
    Determines whether graph-structured requirements are ready for architecture,
    development, and verification, then derives the smallest coherent
    build-preparation package without inventing requirement meaning. Use when
    producing capability maps, epics or workstreams, implementation slices,
    dependency sequencing, contract candidates, domain-model seeds, cross-cutting
    constraints, acceptance-test references, ADR seeds, technical questions, or
    explicit ready/partly-ready/not-ready decisions. Do not use for initial
    discovery or requirement graph normalization.
---

# Implementation Readiness

Convert a validated requirements topology into a traceable package developers,
architects, QA engineers, and technical product owners can use to prepare a build.

> **Core Directives**
>
> 1. **Readiness is a decision, not document polish.** Missing evidence,
>    permissions, dependencies, or acceptance conditions remain blockers.
> 2. **The requirements remain authoritative.** The handoff is a derived
>    build-preparation view.
> 3. **Do not turn uncertainty into design.** Preserve open product, domain,
>    policy, privacy, security, and architecture decisions.
> 4. **Graph edges guide sequence, not boundaries.** A dependency does not imply
>    an API, event, service, or synchronous call.
> 5. **Prefer the smallest coherent slice.** Prove an end-to-end outcome before
>    expanding implementation surface.

## Boundary

Use `requirements-grounding` when the problem, source basis, actor, scope,
priority, or complete-when conditions are unclear. Use `requirements-topology`
when stable IDs, typed edges, duplicate/conflict checks, or dependency order are
missing.

Read project instructions, architecture constraints, domain glossaries, source
catalogs, and policy files when present. Treat them as inputs; do not generalize
their domain rules into this skill.

After this skill admits a slice into implementation, use
`requirements-traceability` to maintain implementation anchors, executed test or
operational evidence, reverse traceability, and stale-reference checks. Readiness
defines the evidence obligation; traceability records whether later work fulfills
it.

## Minimum Inputs

Require enough information to make readiness falsifiable:

- stable requirement IDs and atomic statements;
- source lineage and validation status;
- usable complete-when conditions;
- owning problem scope or foundation capability;
- typed dependencies and dependency order;
- actors, permissions, and relevant constraints;
- external prerequisites and known decision/watch items.

If the user supplies raw requirements, do not pretend they are implementation
ready. Run a light grounding/topology pass and label the result incomplete, or
route to the missing stage.

## Workflow

1. Verify topology stability: no blocking cycles, unresolved ID transformations,
   likely duplicates, must-have verification gaps, or ownerless prerequisites.
2. Group requirements into cohesive capabilities and workstreams without changing
   meaning.
3. Pull foundation capabilities, cross-cutting constraints, data ownership, and
   evidence primitives early in the sequence.
4. Check every external prerequisite for an existing artifact or an explicit
   minimal contract. Mark dependent work partial or blocked when neither exists.
5. Convert prerequisite edges into implementation order while keeping architecture
   choices open.
6. Derive only supported domain-model seeds, contract candidates, integration
   points, data boundaries, and non-functional constraints.
7. Identify ADR candidates where multiple viable designs or unresolved forces
   remain.
8. Define the smallest coherent vertical slice that demonstrates the core outcome.
9. Reference grounding's complete-when conditions as acceptance tests; add only
   concrete fixtures, expected values, and edge cases still needed.
10. Separate ready work, blockers, risks, and technical questions.
11. Seed stable requirement and acceptance-criterion references for downstream
    traceability without claiming implementation or verification evidence yet.

## Readiness Gate

Mark a requirement or slice **ready** only when it has:

- stable, traceable requirement IDs;
- usable complete-when conditions;
- a clear owner and actor;
- known prerequisites with existing artifacts or named minimal contracts;
- identified data ownership and lifecycle;
- relevant security, privacy, accessibility, compliance, audit, and operational
  constraints;
- no unresolved decision that changes the required outcome;
- an accepted validation decision, or an explicitly reversible experiment.

Mark it **partly ready** when a bounded implementation can proceed behind an
explicit assumption, adapter, configuration point, or reversible decision.

Mark it **not ready** when source meaning, actor permission, data availability,
acceptance conditions, external ownership, or dependency order prevents a
responsible implementation decision.

Readiness, implementation, and verification are independent states. A `READY`
decision permits work to start; it does not mean an artifact exists or evidence
has passed.

Do not use architecture uncertainty alone as a blocker when the requirement is
clear and the design decision can be captured as an ADR. Do treat product or
policy uncertainty as a blocker when different answers change the required
outcome.

## Derived Artifacts

Produce only what the current audience needs:

```text
Capability:
- Purpose:
- Requirement IDs:
- Owner:
- Inputs and outputs:
- Constraints:
- Evidence:
- Prerequisites:
- Ready state:
```

```text
Implementation slice:
- Outcome:
- Requirement IDs:
- Actor workflow:
- Prerequisites:
- In scope / out of scope:
- Acceptance-test references:
- Data touched and ownership:
- Roles and permissions:
- Evidence and operations:
- Risks and watch items:
- Developer / architect questions:
```

```text
Contract candidate:
- Kind: command | query | event | import | export | API
- Purpose:
- Producer / consumer:
- Domain terms:
- Validation:
- Security and privacy:
- Evidence and operations:
- Requirement traceability:
```

```text
ADR seed:
- Decision needed:
- Requirement traceability:
- Forces and constraints:
- Viable options:
- Recommendation, if supported:
- Consequences:
- Enforcement candidate:
- Revisit trigger:
```

These are design inputs, not automatic commitments. Use
`architecture-guidelines` when turning them into module or service designs, and
use `functionality-complexity-tradeoff` when a proposed capability still needs a
worth decision.

## Output Contract

Every application emits a decision record before any longer readiness package:

```text
Subject:          <requirement scope, capability, or slice>
Decision:         READY | PARTLY-READY | NOT-READY
Requirement IDs:  <stable IDs covered by the decision>
Prerequisites:    <ready, assumed, or missing>
Blocking gaps:    <source, outcome, owner, data, permission, verification, or contract>
Smallest slice:   <smallest coherent outcome supported now, or none>
Open decisions:   <product / policy blockers versus architecture ADRs>
Next action:      <build, decide, source, contract, split, or return upstream>
Verification:     <readiness checks run, or Not run + reason>
Revisit when:     <required for PARTLY-READY or NOT-READY>
```

A complete readiness package additionally contains:

```text
Implementation readiness:
- Meta-context:                 # standalone artifacts only
- Canonical grounding/topology:
- Readiness decision:           # ready | partly ready | not ready
- Blocking gaps and owners:
- Capability map:
- Workstreams or epics:
- Implementation order:
- Smallest coherent slice:
- Cross-cutting constraints:
- Data ownership and lifecycle:
- Evidence and operational needs:
- Contract candidates:
- Domain-model seeds:
- ADR seeds:
- Acceptance-test references:
- Technical questions:
- Traceability:
```

For a standalone artifact, state audience, purpose, completion date, source
artifacts, source currency, and caveats once near the top. Keep every derived item
traceable to requirement IDs and keep blockers visible beside the readiness
decision.

## Guardrails

- Do not rewrite source requirements to fit a preferred architecture.
- Do not invent payloads, entities, integrations, or non-functional targets that
  the requirements do not support.
- Do not restate complete-when conditions as a competing acceptance-criteria set.
- Do not turn every graph edge into a contract or runtime dependency.
- Do not bury product, domain, security, privacy, compliance, or source-currency
  decisions inside developer notes.
- Do not mark a requirement implemented or verified in a readiness package; hand
  the admitted IDs and evidence obligations to `requirements-traceability`.
- If grounding or topology changes materially, refresh the readiness package or
  state exactly what is stale.

## See also

- `requirements-grounding` — problem, source, evidence, and canonical meaning.
- `requirements-topology` — stable IDs, typed graph, repository validation, and order.
- `requirements-traceability` — implementation and executed verification after readiness.
