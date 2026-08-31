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

## Field Authority

Each field answers one question. Never let a field decide outside its
authority, however strong its numbers are.

| Field | Can establish | Cannot establish |
| --- | --- | --- |
| Static dependency | Direction, reachability, forbidden cycles, layer/tier violations, adapter and SDK ownership | Whether an allowed edge is used, how often, or what it costs |
| Runtime flow | Which edges carry load, where latency and criticality concentrate, which declared edge is dead in production | Semantic ownership, or permission for a static cycle |
| Change affinity | Which components currently share a reason to change inside the declared window | Causality, ownership, or that the coupling will persist |
| Shared data | Write ownership, transaction and schema coupling, migration cost | That co-located data implies one domain |
| Failure propagation | Blast radius, single points of failure, recovery dependence | That a rare incident justifies permanent restructuring |

When two fields disagree, do not average them. Name the disagreement, prefer
the field with authority over the question being asked, and return **DEFER**
when the deciding field is the one that is **Not measured**. A probationary
acceptance under SKILL.md §5 is unavailable here: a disagreement between
measured fields is measured contradiction, which always blocks probation.

At Low reversibility, two fields count as agreement only when both meet their
declared policy and support the same boundary, and at least one has authority
over the dominant reversal-cost driver. Imports plus traffic cannot approve an
irreversible data split while shared-data evidence is **Not measured**.

Use this authority mapping for the dominant driver:

| Reversal-cost driver | Field with relevant authority |
| --- | --- |
| External or cross-team consumers; published/versioned contract | Static dependency/ownership for declared caller and contract edges; runtime flow for active routes |
| Irreversible data migration | Shared data for schema, transaction, write-ownership, and migration coupling |
| Separate deployment boundary | Runtime flow for coordination and latency; failure propagation for recovery dependence and blast radius |
| Separate ownership boundary | Static dependency/ownership for authority direction; change affinity may support but cannot establish ownership |

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
| Reversal cost | The high / medium / low grade and dominant driver, or Unknown with the missing facts; it sets the field-agreement and window requirements in SKILL.md §5 |

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

Record which evidence produced the generator-free baseline, then add at most
one indexed contribution and name its observable falsifier in an unused
independent field or held-out window, as required by
[natural-pattern-atlas.md](natural-pattern-atlas.md). Test the baseline and
contribution under the same policy on that validation surface. Discovery
observations cannot be reused as prospective validation. A natural analogy is
neither an observed field nor independent boundary evidence, and its name or
mechanism may not appear in **Boundary evidence**. A lens that adds nothing,
or that has no unused or held-out validation surface, supplies no second
candidate and is not reported. Fibonacci, sacred geometry, and cymatics never
supply one.

## Confidence

Report confidence as:

- **High** — complete static graph or representative production evidence across
  a relevant window; independent fields agree.
- **Medium** — partial evidence with known gaps; domain meaning and one field
  agree.
- **Low** — sampled, stale, contradictory, or single-field evidence.

Permit hard static invariant findings at High confidence without runtime data.
Require instrumentation before moving a boundary on Low-confidence pressure.
Low confidence is measured evidence: re-measure a stale field inside the
declared window, widen coverage for a sampled one, add a second field for
single-field evidence, and DEFER a contradictory one under **Field Authority**
above. Low confidence is never eligible for probation. Only a field that is
**Not measured** and cannot be measured within the decision window may carry
its instrumentation into a probationary acceptance under SKILL.md §5.
One-field evidence cannot accept a Low-reversibility end state; DEFER that end
state and independently grade any separately specified precursor.
