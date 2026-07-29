# Morphogenetic Architecture

![Morphogenetic Architecture](morphogenetic_architecture.svg)

Design software topology as a declared structure that can be tested and evolved.
Start with a bounded Rapid scan, place each component at a
**Domain / abstraction tier / layer** position, and escalate to Full when the
decision requires restructuring, multi-field evidence, broad scope, or
resolution of ambiguity. Full analysis uses discovery evidence to declare a
lens-free baseline, may use one indexed natural mechanism to add a distinct
candidate or risk, and then tests both against an unused independent field or
held-out evidence window. Nature may propose; software evidence decides.

The operational source is
[`morphogenetic-architecture` SKILL.md](../.claude/skills/morphogenetic-architecture/SKILL.md).

## Why use this

- Preserve the original locality guarantees: explicit interfaces, bounded
  neighbor sets, no forbidden static cycles, and no unowned layer jumps.
- Keep simple placement and static-edge checks fast, while escalating
  automatically before any restructuring decision.
- Detect architecture that looks clean in imports but is coupled through event
  buses, registries, shared schemas, coordinated changes, or cascading failures.
- Discover candidate boundaries from evidence without letting an algorithm
  redefine domain meaning.
- Distinguish static dependencies, which remain directed and acyclic, from
  legitimate runtime feedback loops, which must be named and bounded.
- Scale the required proof to how expensive the change would be to undo, so a
  cheap internal move is not treated like an irreversible published contract.
- Place or evolve a component through an explicit PLACE, KEEP, MOVE, SPLIT, MERGE,
  INTRODUCE-BOUNDARY, DECLARE-RUNTIME-CYCLE, or DEFER decision.

## The model

```text
Mode selector
  Rapid by default for bounded placement and static checks
  Full for restructuring · multi-field evidence · broad scope · ambiguity
             ↓
Declared topology
  Domain / abstraction tier / layer
  Inbound and outbound interfaces
  Allowed static neighbors
             ↓ discover
Observed fields
  Static imports and package edges
  Runtime calls and messages
  Co-change history
  Shared-data ownership
  Failure propagation
             ↓ declare + compute
Decision policy + reproducible graph analysis
  baseline · threshold · window · sensitivity · input/result hashes
             ↓ record lens-free candidate
Operational natural pattern atlas
  one routed lens · distinct contribution · falsifier in unused/held-out evidence
             ↓ validate
Independent field or held-out window
             ↓ grade reversal cost
Reversibility
  high · medium · low · unknown → how much agreeing evidence the change must carry
             ↓ evidence decides
PLACE / KEEP / MOVE / SPLIT / MERGE / INTRODUCE-BOUNDARY /
DECLARE-RUNTIME-CYCLE / DEFER
```

Keep the observed fields separate. Traffic counts, shared commits, schema
ownership, and incident impact have different meanings and units; combining
them without a declared weighting policy creates false precision.

## How to use

The selector starts in Rapid unless the request already requires Full. Use a
bounded design request for a new component:

> Place `OrderShipmentNotifier`. Declare its Domain / abstraction tier / layer,
> inbound and outbound interfaces, allowed static dependencies, and any runtime
> feedback loop.

This can finish in Rapid with PLACE, KEEP, DECLARE-RUNTIME-CYCLE, or DEFER.
Rapid escalates to Full when MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY becomes
a candidate; when non-static evidence affects the decision; when scope crosses
several components or a material boundary; or when placement remains
ambiguous.

Use a Full audit when declared structure may have drifted:

> Audit `src/checkout`. Compare imports, traces, six months of co-change, shared
> schemas, and incident propagation with the declared domain boundaries.

An explicit `rapid` or `quick` request selects only the starting mode; it cannot
waive an escalation. Once Full begins, missing evidence is reported as
**Not measured** and produces DEFER when required proof is unavailable.

Every result also exposes:

```text
Analysis mode:    <Rapid | Full | Rapid → Full>
Selection reason: <bounded static check | explicit Full request | escalation condition>
Decision policy: <field + baseline + threshold + window + sensitivity>
Graph analysis:  <script/tool + version + input/result hash | Not measured>
Candidate baseline: <lens-free candidate | none>
Natural lens:       <pattern | none | explanation only | inspiration only>
Lens contribution:  <distinct alternative or risk | none>
Lens falsifier:     <rejection condition + unused field or held-out window | none>
Transfer:           <mechanism → contribution; break point; evidence result>
Reversibility:      <high | medium | low + driver |
                     Unknown — Low bar applies + missing facts |
                     Not required + reason>
```

## Reversibility sets the evidence bar

Not every topology change costs the same to undo, so not every one deserves the
same proof. The grade is read from declared facts — consumer count, published
contracts, data migration, deployment coupling — so it costs no extra analysis.

It applies only where a boundary actually moves: MOVE, SPLIT, MERGE,
INTRODUCE-BOUNDARY, and a DEFER that withholds one of them. PLACE, KEEP, and
DECLARE-RUNTIME-CYCLE report it as **Not required**.

| Grade | Typical situation | What the change must carry |
| --- | --- | --- |
| **High** | Internal callers only, no published contract, no data move | Domain reason plus one independent field; a shorter evidence window is acceptable when the reversal path is named |
| **Medium** | Several internal consumers, shared contract, coordinated deploy | Domain reason plus one independent field meeting its policy, plus the sensitivity check |
| **Low** | External or cross-team consumers, a published or versioned contract, irreversible data migration, or a separate deployment/ownership boundary | Domain reason plus two independent applicable fields that each meet their declared policy and support the same boundary; at least one field must have authority over the dominant reversal-cost driver. Also require a passing sensitivity check for any generated candidate and a staged path whose reversal step is explicit. If only one field is available, emit DEFER for the Low-reversibility end state; a separately specified precursor may proceed only after it is graded independently and meets its own evidence bar. |

Grade from the least-reversible known signal. When the facts needed to exclude a
Low signal cannot be stated, report **Reversibility: Unknown — Low bar applies**,
name the missing consumer, contract, data, deployment, or ownership facts in
**Next action**, and do not accept the Low-reversibility end state until they
are resolved. Grade any separately specified precursor independently.

Reversibility only moves the evidence bar: it never waives a hard invariant,
never lets Rapid accept a restructuring, and never replaces the
`structural-simplification` measurement.

## Important distinctions

- **Requirements topology** structures requirements and their prerequisites.
  Morphogenetic Architecture places implementation components.
- **Architecture guidelines** decide what belongs inside a component.
  Morphogenetic Architecture decides where it belongs and what may connect.
- **Structural simplification** measures complexity deltas for a proposed
  topology change.
- **Architecture as code** encodes deterministic static dependency constraints.

## Reproducible graph analysis

Weighted evidence cannot be narrated into existence. Before generating a cut,
declare a per-field baseline, metric, threshold, evidence window, minimum group
size, and sensitivity rule. Then run the bundled deterministic analyzer:

```text
python scripts/analyze_evidence_graph.py graph.json --pretty
```

It computes directed SCCs, spectral/Fiedler candidate cuts, normalized cut,
conductance, and deterministic perturbation sensitivity. Its hashes bind the
result to the exact input. The output deliberately reports
`architecture_decision: NOT_EVALUATED`: an eligible cut still needs domain
meaning and an independent observed field.

If no executable output exists, graph analysis is **Not measured**. If a policy
is missing, fitted after inspecting a preferred cut, or unstable under its
declared sensitivity rule, the architecture decision is **DEFER**.

## Natural pattern atlas

The operational atlas contains twelve candidate-generating mechanisms. Enter
through a one-to-one **operational lens index** keyed by the question or finding
name — `god component`, `hidden runtime coupling`, `topology drift` — rather
than browsing. Use at most one operational lens; a hard invariant such as a
forbidden import cycle needs none.

Before using the atlas, record the lens-free baseline candidate and the
discovery observations that produced it. The routed lens must add one distinct
alternative or expose one missed risk, then name its observable falsifier in an
unused independent field or predeclared held-out window. Test the baseline and
contribution under the same policy on that validation surface. Discovery
observations cannot be reused as prospective validation. When the lens adds
nothing, report `Natural lens: none`; when no unused or held-out validation
surface remains, mark it `explanation only`. Never cite the lens or mechanism
in **Boundary evidence**.

**Pattern and differentiation** — what should this component become, and where
is the seam?

| Natural architecture | Software question it helps ask |
| --- | --- |
| **Cell differentiation** | Should one component specialize or split because its position and signals imply different responsibilities? |
| **Segmentation** and compartments | Should these siblings stay symmetric around one varying parameter, and which peer-to-peer crossings are forbidden? |
| **Convergent evolution** | Two components independently grew the same solution — is that a missing shared capability or justified duplication? |

**Transport and connection** — how should components reach each other?

| Natural architecture | Software question it helps ask |
| --- | --- |
| **Hierarchical branching** | Which named trunks or adapters should distribute access into local twigs? |
| **Physarum** transport | Which valuable paths should strengthen, and which demonstrably unused edges can be pruned? |
| **Leaf venation** | Where is a runtime loop worth its cost because it provides measured resilience? |
| **Stigmergy** | Is coordination happening through shared state, a queue, or a registry rather than through a declared interface — and who owns that medium? |
| **Endosymbiosis** | Should this external capability be absorbed behind an owned adapter, or stay external with its own lifecycle? |

**Persistence and renewal** — what keeps this form, what should change it, and
what should leave?

| Natural architecture | Software question it helps ask |
| --- | --- |
| **Homeostasis** | Does a feedback cycle have a setpoint, bound, owner, exit, and observability? |
| **Bone remodeling** | Is pressure persistent enough to justify changing the structure? |
| **Quorum sensing** | Do these independent peers still need no coordinator, or does measured contention justify one control point? |
| **Apoptosis** | Is this component being retired through an explicit signal, owner, and cleanup path, or just left to rot? |

Each operational entry carries a concrete **Reject when** condition rather than
a general “do not infer” warning. The natural mechanism may change what the
agent tests, but it cannot count as boundary evidence.

### Rationale and exploratory material

**Canalization** remains the rationale for scaling proof to reversal cost, but
it is not a topology-candidate lens. Grade reversibility only from software
facts: consumers, contracts, data, deployment, ownership, and the reversal
path.

Reaction–diffusion, Phyllotaxis/Fibonacci, and Cymatics remain in an exploratory
appendix. They may prompt questions or visualizations, but they cannot populate
`Lens contribution` and are always `inspiration only`.

Keep the beauty. Use circles to discuss ownership, overlaps to expose shared
concerns, spirals to show iterative growth, branches to show distribution,
lattices to show peer symmetry, and nodal lines to visualize quiet candidate
boundaries.

Keep the epistemic boundary too. Golden ratios, Fibonacci counts, fractal depth,
and sacred figures are `inspiration only` unless the software shares the
natural system's measurable mechanism, objective, and constraints. A beautiful
shape never supplies the domain reason or independent observed field required
for a topology change.

## Next steps

- Read the
  [Rapid topology scan](../.claude/skills/morphogenetic-architecture/references/rapid-topology-scan.md)
  whenever the selector starts in Rapid; preserve its completed checks if the
  task escalates to Full.
- Read
  [evidence-fields.md](../.claude/skills/morphogenetic-architecture/references/evidence-fields.md)
  before using telemetry, history, weighting, or graph partitioning.
- Read
  [graph-analysis.md](../.claude/skills/morphogenetic-architecture/references/graph-analysis.md)
  and use the bundled analyzer before reporting SCCs, spectral cuts, cut
  metrics, or sensitivity.
- Use the
  [natural pattern atlas](../.claude/skills/morphogenetic-architecture/references/natural-pattern-atlas.md)
  through its operational index; record the baseline, one distinct
  contribution, its falsifier in unused or held-out evidence, the break point,
  and the software-evidence result.
- Use
  [`structural-simplification`](../.claude/skills/structural-simplification/)
  before accepting MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY.
- Hand static dependency constraints to
  [`architecture-as-code`](../.claude/skills/architecture-as-code/).
