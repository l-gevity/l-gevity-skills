# Natural Pattern Atlas

Use this atlas after declaring topology and available evidence, but before
choosing a topology decision. Select the mechanism whose objective, pressure,
and constraints best match the software situation. The analogy proposes a
candidate; repository and operational evidence decide it.

## Transfer Test

For every lens:

1. Name the natural system and the mechanism that produces or preserves form.
2. Name the shared software objective, pressure, and constraint.
3. Generate one candidate placement or topology change.
4. State where the analogy breaks.
5. Accept or reject the candidate using independent software evidence.

Return `none` when steps 2 or 4 cannot be stated precisely.

## Mechanism Atlas

| Natural architecture | Transferable mechanism | Software use | Required evidence | Do not infer |
| --- | --- | --- | --- | --- |
| **Cell differentiation** | Shared rules produce specialized cells according to position and signals | Place or split components by domain position and responsibility instead of cloning bespoke variants | Domain meaning plus responsibility/change evidence | Components should imitate cell types or share one implementation |
| **Reaction–diffusion morphogenesis** | Local activation and inhibition can generate stable global pattern | Prefer small local dependency rules whose interaction yields coherent global topology | Static edges plus the field that exposes the instability | A reaction–diffusion algorithm is automatically optimal for software |
| **Phyllotaxis / Fibonacci spirals** | New organs appear through local growth and exclusion fields; Fibonacci counts can emerge from the process | Explore spacing of repeated peers around a constrained coordinator or resource | Measured contention, capacity, and placement constraints | Golden ratios, Fibonacci module counts, fan-out limits, or directory depth |
| **Hierarchical branching** | Repeated branching distributes material while retaining trunks and local twigs | Nest domains and route infrastructure access through named trunks/adapters | Ownership, call paths, and bottleneck evidence | Every topology should be a tree or repeat identically at every scale |
| **Physarum adaptive transport** | Valuable routes reinforce while costly routes weaken under an efficiency/cost/fault-tolerance trade-off | Consolidate high-value interfaces and propose pruning demonstrably unused edges | Runtime volume, change history, reachability, and failure impact | Traffic determines semantic ownership or permits static cycles |
| **Leaf venation** | Loops trade transport cost for resilience under damage and fluctuating loads | Add runtime redundancy or alternate delivery paths while keeping static ownership acyclic | Failure injection, incident paths, load variation, and recovery behavior | More loops are always safer or runtime redundancy justifies import cycles |
| **Homeostasis** | Negative feedback keeps a variable inside viable bounds | Declare retry, backpressure, autoscaling, or reconciliation cycles with setpoint, bound, owner, and observability | Runtime state transitions and telemetry | An unbounded feedback loop will stabilize itself |
| **Bone remodeling** | Structure accumulates along persistent load and recedes where load disappears | Move boundaries or prune edges only after sustained pressure across a meaningful window | Repeated co-change, traffic, or failure pressure | One hot trace or incident justifies permanent restructuring |
| **Cymatics / Chladni figures** | Frequency, material, geometry, and boundary conditions expose nodal regions | Sweep change or traffic windows to look for stable low-pressure candidate boundaries | Repeated measurements across windows and sensitivity checks | Sound, frequency, or a beautiful nodal shape is architectural evidence |

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

**SDK sprawl → hierarchical branching.** Several domains import one vendor SDK.
Treat the adapter as a vascular trunk and propose one outbound contract.
Accept only if ownership is clear and failure evidence does not turn the adapter
into an unmitigated bottleneck.

**Event retries → homeostasis.** A consumer republishes failed messages. Treat
the route as a feedback regulator and declare its setpoint, retry bound, owner,
dead-letter exit, and telemetry. This permits a bounded runtime cycle, never a
static ownership cycle.

**Co-changing monolith → differentiation plus remodeling.** Independent
capabilities repeatedly change and fail for different reasons inside one
component. Propose SPLIT; accept only when domain meaning and an independent
change or failure field agree.

## Research Grounding

- Alan Turing, [The Chemical Basis of Morphogenesis](https://doi.org/10.1098/rstb.1952.0012)
- Lewis Wolpert, [Positional information and the spatial pattern of cellular differentiation](https://doi.org/10.1016/S0022-5193(69)80016-0)
- Richard Smith et al., [A plausible model of phyllotaxis](https://doi.org/10.1073/pnas.0510457103)
- Atsushi Tero et al., [Rules for biologically inspired adaptive network design](https://doi.org/10.1126/science.1177894)
- Eleni Katifori et al., [Damage and fluctuations induce loops in optimal transport networks](https://doi.org/10.1103/PhysRevLett.104.048704)
- Rik Huiskes et al., [Effects of mechanical forces on maintenance and adaptation of form in trabecular bone](https://doi.org/10.1038/35015116)
