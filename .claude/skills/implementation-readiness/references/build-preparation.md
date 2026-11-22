# Build Preparation — Vehicles and Templates

Read when `implementation-readiness` schedules an assumption vehicle or derives a
build-preparation artifact. The skill decides readiness; these are the shapes
its derived artifacts take.

## Assumption vehicles

| Vehicle | Invalidates | Constraint |
| --- | --- | --- |
| Proof of concept | One named feasibility or technical assumption | Any technology, disposable; throwaway code never crosses the merge boundary without the enforcement `architecture-as-code` requires |
| Prototype | A functional or interaction assumption, with stakeholders | One-off, without the non-functional obligations; demonstrates, never ships |
| Minimum viable product | The linked outcome hypothesis, through real use | Complete enough for one full build-measure-learn turn, and the first end-to-end exercise of the delivery path |

## Derived artifact templates

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
Implementation increment:
- Outcome:
- Requirement IDs:
- Actor workflow:
- Prerequisites:
- In scope / out of scope:
- Acceptance-test references:
- Data touched and ownership:
- Aspects touched:
- Roles and permissions:
- Evidence and operations:
- Parallel-ready: yes | no + missing criterion
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

## Readiness package

A complete readiness package additionally contains:

```text
Implementation readiness:
- Meta-context:                 # standalone artifacts only
- Canonical grounding/topology:
- Readiness decision:           # ready | partly ready | not ready
- Blocking gaps and owners:
- Capability map:
- Workstreams or epics:
- Implementation order:         # riskiest assumption first; parallel-ready groups marked
- Smallest coherent increment:
- Aspects:                      # aspect × capability matrix, projected from topology
- Data ownership and lifecycle:
- Evidence and operational needs:
- Contract candidates:
- Domain-model seeds:
- ADR seeds:
- Acceptance-test references:
- Technical questions:
- Traceability:
```
