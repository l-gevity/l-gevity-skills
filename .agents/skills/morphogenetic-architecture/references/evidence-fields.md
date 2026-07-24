# Evidence Fields

Read this reference only when an architecture audit uses repository history,
runtime telemetry, weighted relationships, or graph partitioning.

## Evidence Record

Record every field independently:

| Field | Nodes | Edges | Useful weight |
| --- | --- | --- | --- |
| Static dependency | Components | Import/package/build edge | Count, direction, forbidden/allowed |
| Runtime flow | Services/components | Call/message route | Volume, latency, criticality |
| Change affinity | Files/components | Co-change relation | Shared commits over a stated window |
| Shared data | Components/datasets | Read/write/ownership relation | Access mode, transaction dependence |
| Failure propagation | Components | Causal incident edge | Frequency, impact, recovery time |

For every dataset, record its source, time window, coverage, known blind spots,
and confidence. Mark absent evidence **Not measured**.

## Decision Policy

Declare a policy for each weighted field before generating or inspecting a
preferred candidate:

| Policy field | Record |
| --- | --- |
| Baseline | Prior accepted architecture, control period, or explicit reference |
| Metric | One field-specific measure; never a sum of incompatible units |
| Acceptance rule | Operator and numeric/ordinal threshold |
| Evidence window | Minimum time, samples, commits, traces, or incidents |
| Candidate size | Minimum group size or fraction that prevents trivial isolation |
| Sensitivity | Perturbation size and minimum stable membership for generated partitions; metric stability only for fixed supplied partitions |
| Basis | Why the policy was chosen before candidate generation |

Hard invariants such as a forbidden static cycle do not need a threshold. For
all weighted candidates, a missing, retrofitted, or unstable policy requires
**DEFER**.

## Weight Discipline

- Do not add raw values with incompatible units.
- Normalize only within one declared comparison and retain the original values.
- Prefer ordinal `low / medium / high` when precision would be invented.
- Declare weights before inspecting a preferred partition.
- Run sensitivity checks: if a small weight change reverses the proposed
  boundary, return **DEFER**.
- Keep semantic ownership as a hard constraint; do not let traffic volume move
  business meaning into infrastructure.

## Boundary Discovery

Use graph algorithms to propose boundaries only after defining nodes, edge
meaning, and excluded relationships.

1. Build and retain one graph input per evidence field.
2. Freeze the field's decision policy before candidate generation.
3. Compute SCCs or candidate cuts with the bundled script or a named equivalent.
4. Retain tool/version, command, input identity, configuration, and result.
5. Compare stable candidate cuts across independent fields.
6. Compare stable candidates with declared domain boundaries.
7. Ask whether each candidate has one domain name, lifecycle, owner, public
   contract, and reason to change.

Use spectral partitioning, normalized cuts, or community detection only as
candidate generators. Reject partitions that merely isolate a high-degree
utility, split one transaction invariant, or mix unrelated edge meanings.

Read [graph-analysis.md](graph-analysis.md) for the executable contract. If no
reproducible output exists, report graph analysis **Not measured**. Never
hand-calculate or narrate an SCC, Fiedler vector, cut metric, or sensitivity
result.

## Natural-Lens Boundary

Use [natural-pattern-atlas.md](natural-pattern-atlas.md) to generate a candidate,
then return here to test it. A natural analogy is neither an observed field nor
independent boundary evidence. Fibonacci, sacred geometry, and cymatics remain
`inspiration only` unless the software shares a measurable mechanism, objective,
and constraints with the source system.

## Confidence

Report confidence as:

- **High** — complete static graph or representative production evidence across
  a relevant window; independent fields agree.
- **Medium** — partial evidence with known gaps; domain meaning and one field
  agree.
- **Low** — sampled, stale, contradictory, or single-field evidence.

Permit hard static invariant findings at High confidence without runtime data.
Require instrumentation before moving a boundary on Low-confidence pressure.
