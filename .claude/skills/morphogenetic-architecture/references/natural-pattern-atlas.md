# Natural Pattern Atlas

Use this atlas after declaring topology and recording the discovery evidence
that produced the question, finding, and lens-free baseline, but before choosing
a topology decision. The atlas is one of SKILL.md §4's second-candidate
generators; an algorithmic cut or a manual alternative decomposition may serve
instead. The analogy may add one candidate or expose one missed
risk; an unused independent field or held-out evidence window must be able to
reject it.

## Candidate-Contribution Test

For every operational lens:

1. Record the lens-free baseline candidate from domain meaning, declared
   topology, hard-invariant checks, and discovery evidence; `none` is valid.
2. Enter through the Operational Lens Index and select its one routed lens.
3. Name the natural mechanism and the shared software objective, pressure, and
   constraint.
4. Record one alternative candidate or newly exposed risk that differs from the
   baseline.
5. Name an unused independent field or predeclared held-out window, then state
   the observable condition in it that would reject the contribution.
6. State where the analogy breaks.
7. Test the baseline and contribution under the same independent software
   evidence policy on that validation surface.

Freeze this record before inspecting the validation surface:

```text
Baseline:            <generator-free candidate | none>
Natural system:      <system and pattern>
Mechanism:           <what produces or preserves the natural form>
Software match:      <shared objective, pressure, and constraint>
Contribution:        <one distinct alternative or newly exposed risk>
Falsifier:           <observable rejection condition + unused field or window>
Break point:         <where the analogy stops>
```

The record stays in the working notes. A lens that passes this test supplies
one `Second candidate` entry in the SKILL.md §8 report, tagged with the
`natural lens` generator; nothing else about the analogy is reported. A lens
that fails supplies no second candidate.

Return `none` when the lens adds nothing to the baseline or lacks a concrete
falsifier. When no unused independent field or held-out window remains, mark
the lens `explanation only`: it may clarify the result but cannot claim
candidate contribution. Evidence used to discover the baseline cannot be
reused as prospective validation. The lens name and mechanism may never appear
in **Boundary evidence**.

## Operational Lens Index

Enter through the question or the SKILL.md §5 finding name. Each row routes to
one lens to limit motivated selection. A hard invariant needs no lens: report
and fix it.

| Question or finding | Use |
| --- | --- |
| Where does one new component belong?; **placement ambiguity** | Cell differentiation |
| **god component**, SPLIT candidate | Segmentation |
| **false boundary**, repeated independent implementations | Convergent evolution |
| **cross-domain coupling**, **external SDK bypass** | Hierarchical branching |
| **hidden runtime coupling** | Stigmergy |
| External capability: absorb, adapt, or keep independent? | Endosymbiosis |
| **boundary-pressure mismatch**, **topology drift** | Bone remodeling |
| **resilience bottleneck** | Leaf venation |
| Should this runtime loop exist, and inside what bound? | Homeostasis |
| Should this edge be removed? | Physarum |
| Should this component be retired? | Apoptosis |
| Do these independent peers now need a coordinator? | Quorum sensing |
| **forbidden import cycle**, **layer-skip violation**, **tier inversion** | Hard invariant — no lens |

## Mechanism Atlas

Three families answer three different questions: what a component becomes, how
components reach each other, and what holds, changes, or removes form over
time.

### Pattern and Differentiation

*What should this component become, and where is the seam?*

| Natural architecture | Transferable mechanism | Software use | Required evidence | Reject when |
| --- | --- | --- | --- | --- |
| **Cell differentiation** | Shared rules produce specialized cells according to position and signals | Place or split components by domain position and responsibility instead of cloning bespoke variants | Domain meaning plus responsibility/change evidence | Domain meaning and responsibility/change evidence do not reveal distinct positions or reasons to change |
| **Segmentation and compartments** | Repeated segments acquire distinct identity from positional genes, and compartment lineages do not mix across a boundary | Keep sibling modules symmetric with one varying positional parameter, and forbid direct peer-to-peer crossing between compartments such as tenant, region, or plugin | The sibling contract, the parameter that legitimately varies, and observed cross-peer edges | The siblings lack a stable shared contract or legitimate operation requires the proposed peer crossings |
| **Convergent evolution** | Unrelated lineages under the same pressure independently evolve similar structures without shared ancestry | Read independently reinvented solutions in separate components as a signal for one missing shared capability, or as duplication that the shared pressure justifies | The shared pressure, both contracts, and change/failure history for each implementation | The contracts, lifecycles, or failure semantics differ materially despite surface similarity |

### Transport and Connection

*How should components reach each other?*

| Natural architecture | Transferable mechanism | Software use | Required evidence | Reject when |
| --- | --- | --- | --- | --- |
| **Hierarchical branching** | Repeated branching distributes material while retaining trunks and local twigs | Nest domains and route infrastructure access through named trunks/adapters | Ownership, call paths, and bottleneck evidence | The proposed trunk has no clear owner or creates a bottleneck without a recovery path |
| **Physarum adaptive transport** | Valuable routes reinforce while costly routes weaken under an efficiency/cost/fault-tolerance trade-off | Consolidate high-value interfaces and propose pruning demonstrably unused edges | Runtime volume, change history, reachability, and failure impact | The edge remains reachable or required, or pruning increases material failure impact |
| **Leaf venation** | Loops trade transport cost for resilience under damage and fluctuating loads | Add runtime redundancy or alternate delivery paths while keeping static ownership acyclic | Failure injection, incident paths, load variation, and recovery behavior | Failure injection and load variation show no recovery benefit proportionate to the added route |
| **Stigmergy** | Agents coordinate by modifying a shared environment rather than by addressing each other | Decide whether coordination through shared state, queues, artifacts, or registries is a declared contract or an undeclared edge, then name its owner and make the route traceable | Write/read ownership of the shared medium, runtime routes, and the inventory of undeclared edges | The medium is a separate component needing its own position, or its owner and routes cannot be stated |
| **Endosymbiosis** | An absorbed organism keeps some machinery but loses autonomy while the host takes over control and interfaces | Decide whether an external capability is absorbed behind an owned adapter, kept external with its own lifecycle, or hosted internally | Ownership, failure isolation, upgrade cadence, and data/contract coupling with the external system | Ownership, upgrade cadence, failure isolation, or data coupling requires an independent lifecycle |

### Persistence and Renewal

*What keeps this form stable, what should change it, and what should leave?*

| Natural architecture | Transferable mechanism | Software use | Required evidence | Reject when |
| --- | --- | --- | --- | --- |
| **Homeostasis** | Negative feedback keeps a variable inside viable bounds | Declare retry, backpressure, autoscaling, or reconciliation cycles with setpoint, bound, owner, and observability | Runtime state transitions and telemetry | The loop lacks a stable setpoint, bound, owner, exit, or observable state |
| **Bone remodeling** | Structure accumulates along persistent load and recedes where load disappears | Move boundaries or prune edges only after sustained pressure across a meaningful window | Repeated co-change, traffic, or failure pressure | The signal disappears under a predeclared window change or authoritative fields disagree |
| **Quorum sensing** | Individuals act independently until a density signal crosses a threshold, then switch to coordinated collective behavior | Decide whether independent peers still need no coordinator, or whether measured contention justifies one explicit control point | Peer count, contention/conflict rate, coordination cost, and the failure profile of the added control point | Contention stays below the predeclared threshold or coordinator failure costs more than peer coordination |
| **Apoptosis** | Programmed, signal-triggered death removes cells cleanly and neighbors absorb the remains without inflammation | Retire a component through an explicit removal signal — deprecation marker, reachability proof, owner, and cleanup path — instead of leaving it to rot in place | Reachability, callers, runtime traffic across a stated window, and data-retention obligations | Callers, traffic, or retention duties remain, or no owner accepts the cleanup path |

## Reversibility Rationale

**Canalization** explains why committed paths resist perturbation and why later
divergence costs more. It motivates grading reversal cost, but it does not
generate a topology candidate and is not an operational lens. Derive the grade
only from software facts: consumers, contracts, data migration, ownership,
deployment coupling, and the reversal path. Do not claim a lens contribution
merely because reversibility was graded.

## Exploratory Appendix

These mechanisms may prompt research questions or diagrams, but they are not
available through the Operational Lens Index and can never supply a second
candidate. Mark them `inspiration only`.

| Natural architecture | Exploratory use | Why non-operational |
| --- | --- | --- |
| **Reaction–diffusion morphogenesis** | Ask whether small local activation/inhibition rules could expose a coherent global pattern | The mapping does not yet define a distinct topology operator and falsifier beyond ordinary local-rule analysis |
| **Phyllotaxis / Fibonacci spirals** | Explore how repeated peers grow around a constrained coordinator or resource | Measured contention and capacity already decide placement; Fibonacci form adds no admissible evidence |
| **Cymatics / Chladni figures** | Visualize stable low-pressure regions across traffic or change windows | Window sweeps and sensitivity analysis generate the candidate directly; the visual analogy adds no independent operator |

## Symbolic Geometry

Use sacred geometry as a visual and questioning vocabulary, not as optimization
evidence:

- **Circle** — ask what is inside one ownership boundary.
- **Vesica / overlap** — expose a shared concern that may need one owner.
- **Spiral** — show iterative growth or re-entry through a bounded loop.
- **Branch** — show distribution from an explicit trunk or contract.
- **Lattice** — show peer symmetry and repeated local rules.
- **Nodal line** — visualize a candidate low-pressure separation.

Mark the lens `inspiration only`. A symbolic form never supplies the domain
reason or independent observed field required for a boundary change.

## Worked Transfers

These examples are abbreviated. A real report distinguishes discovery evidence
from the unused field or held-out window named in its falsifier.

**SDK sprawl → hierarchical branching.** Several domains import one vendor SDK.
The lens-free baseline is one owned adapter. Branching contributes the risk that
one trunk could become a bottleneck; reject that contribution if ownership,
call-path, and failure evidence show no material concentration. Accept the
adapter only when the same evidence policy supports it and a recovery path owns
the residual concentration.

**Event retries → homeostasis.** A consumer republishes failed messages. Treat
the route as a feedback regulator and declare its setpoint, retry bound, owner,
dead-letter exit, and telemetry. This permits a bounded runtime cycle, never a
static ownership cycle.

**Co-changing monolith → differentiation plus remodeling.** Independent
capabilities repeatedly change and fail for different reasons inside one
component. Propose SPLIT; accept only when domain meaning and an independent
change or failure field agree.

**Shared status column → stigmergy.** Two services coordinate by writing and
polling one status field that neither declares as an interface. Name the medium,
give it a single writer and an explicit contract, and record the edge in the
declared topology. The analogy stops at intent: insects need no owner, software
does. Reject the lens when the medium is really a third component that deserves
its own position rather than a contract.

**Duplicate retry helpers → convergent evolution.** Two domains independently
grew equivalent retry-and-backoff code under the same failure pressure. The lens
proposes one shared capability and hands the target level to `bring-down`.
Accept only when both contracts and both failure histories match; reject when
the resemblance is superficial and the two lifecycles genuinely differ.

## Research Grounding

- Alan Turing, [The Chemical Basis of Morphogenesis](https://doi.org/10.1098/rstb.1952.0012)
- Lewis Wolpert, [Positional information and the spatial pattern of cellular differentiation](https://doi.org/10.1016/S0022-5193(69)80016-0)
- Edward B. Lewis, [A gene complex controlling segmentation in Drosophila](https://doi.org/10.1038/276565a0)
- Richard Smith et al., [A plausible model of phyllotaxis](https://doi.org/10.1073/pnas.0510457103)
- Atsushi Tero et al., [Rules for biologically inspired adaptive network design](https://doi.org/10.1126/science.1177894)
- Eleni Katifori et al., [Damage and fluctuations induce loops in optimal transport networks](https://doi.org/10.1103/PhysRevLett.104.048704)
- Lynn Sagan (Margulis), [On the origin of mitosing cells](https://doi.org/10.1016/0022-5193(67)90079-3)
- Rik Huiskes et al., [Effects of mechanical forces on maintenance and adaptation of form in trabecular bone](https://doi.org/10.1038/35015116)
- Conrad H. Waddington, [Canalization of development and the inheritance of acquired characters](https://doi.org/10.1038/150563a0)
- Melissa Miller and Bonnie Bassler, [Quorum sensing in bacteria](https://doi.org/10.1146/annurev.micro.55.1.165)
- John Kerr, Andrew Wyllie, Alastair Currie, [Apoptosis: a basic biological phenomenon with wide-ranging implications in tissue kinetics](https://doi.org/10.1038/bjc.1972.33)
- Guy Theraulaz and Eric Bonabeau, "A Brief History of Stigmergy", *Artificial Life* 5(2), 1999.
