---
name: morphogenetic-architecture
description: >-
    Design and audit evolving, evidence-weighted software topology. Start with
    a rapid declared-topology scan; escalate to full analysis for
    restructuring, multi-field evidence, broad scope, ambiguity, or a deep
    audit. Place components by domain, abstraction tier, and layer; preserve
    directed interfaces; compare imports, runtime flow, co-change, shared data,
    and failure propagation; then place, keep, move, split, merge, or introduce
    a boundary. TRIGGER when placing a module/service/layer, refactoring
    dependency topology, discovering bounded contexts, diagnosing cycles,
    god-components, cross-domain tangles, or hidden runtime coupling, or
    comparing observed behavior with declared architecture. SKIP for routine
    in-boundary logic, isolated bug fixes, content/CSS edits, dependency bumps,
    and trivial renames. Use `architecture-guidelines` for component internals,
    `structural-simplification` for complexity deltas, and
    `architecture-as-code` for enforceable dependency rules.
---

# Morphogenetic Architecture

Shape software topology through local rules, declared boundaries, and measured
pressure. Preserve the Domain / abstraction tier / layer placement model as the
declared skeleton; use observed relationships to test and evolve that skeleton
instead of treating the initial grid as permanent truth.

The workflow itself follows morphogenesis: the declared topology acts as a
genetic scaffold, observed fields expose developmental pressure, topology
decisions differentiate or remodel the structure, and verification maintains
homeostasis. Treat this as a disciplined transfer of mechanisms, not a claim
that software is literally alive.

## Core Directives

1. **Declare before observing.** Record intended placement and allowed
   dependency direction before using telemetry or history to challenge it.
2. **Keep projections distinct.** Keep static imports, runtime interaction,
   change affinity, shared data, and failure propagation as separate graphs.
   Never hide an invalid static edge inside an acceptable runtime cycle.
3. **Prefer local rules.** Make each component depend on a small, named neighbor
   set through explicit inbound and outbound interfaces.
4. **Evolve from evidence.** Move, split, or merge only when domain meaning and
   observed pressure support the same change. Treat algorithms as candidate-cut
   generators, never as domain authority. Accept computed graph evidence only
   from retained executable output, never from a narrated calculation.
5. **Transfer mechanisms, not silhouettes.** When selecting a natural lens,
   use its mechanism to generate and explain a candidate, then let software
   evidence accept or reject it. Never choose a topology because it resembles
   a spiral, tree, honeycomb, or sacred figure.
6. **Preserve one owner per rule.** Hand complexity measurement to
   `structural-simplification`, internal design to `architecture-guidelines`,
   and enforceable edges to `architecture-as-code`.
7. **Escalate proof monotonically.** Start with the smallest sufficient
   analysis mode, but never let a request for speed waive evidence,
   measurement, or hard-invariant checks.

## Select the Analysis Mode

Select and report the analysis mode before collecting evidence. User wording
chooses the starting mode; the rules below choose the minimum proof standard.

| Mode | Use for | Evidence surface | Available final decisions |
| --- | --- | --- | --- |
| **Rapid** | One bounded placement, a small static-edge check, or declaration of one already-identified runtime loop | Declared placement, static dependencies, and the named loop's bound / owner / observability | PLACE, KEEP, DECLARE-RUNTIME-CYCLE, DEFER |
| **Full** | Restructuring, multi-field evidence, broad topology, ambiguity, or a deep audit | Declared topology plus every available static, runtime, change, data, and failure field | All decisions in §6 |

Apply this deterministic selector:

1. Start in **Full** when the user explicitly requests a `full topology`
   analysis, `deep architecture` audit, evidence-driven redesign, or a
   subsystem/service-graph architecture audit. A bare Alchemy `FULL` dispatch
   traverses gates but does not override this skill's selector.
2. Otherwise start in **Rapid** and read
   [references/rapid-topology-scan.md](references/rapid-topology-scan.md).
3. Escalate from Rapid to Full before selecting a decision when any of these
   conditions appears:
   - MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY becomes a candidate;
   - a decision depends on runtime pressure, co-change, shared data, failure
     propagation, weighting, or graph partitioning rather than merely
     declaring one bounded runtime loop;
   - the scope crosses several domains/components or a material ownership,
     security, compliance, or failure boundary;
   - placement is ambiguous, observed signals conflict, or the Rapid result
     cannot be justified from declared topology and hard invariants alone.
4. Once Full begins, do not downgrade because evidence is unavailable. Record
   missing fields as **Not measured** and emit DEFER when the proof requirement
   cannot be met.

An explicit `rapid` or `quick` request may select the starting mode, but it
cannot authorize a restructuring decision. Rapid must either finish with one
of its four decisions or record `Rapid → Full` and continue at Full. Do not
rerun checks already completed unless Full requires a broader evidence scope.

## Reporting Vocabulary

Use coder-facing terms in every report:

| Concern | Coder-facing field |
| --- | --- |
| Business placement | **Domain** — a bounded context; allow nested paths such as `commerce/payments` |
| Responsibility scale | **Abstraction tier** — orchestrator → capability → primitive |
| Environment depth | **Layer** — consumer → application/domain → infrastructure |
| Entry surface | **Inbound interface** — the public contract callers use |
| Dependency surface | **Outbound interface** — declared calls, I/O, or infrastructure access |
| Vertical relationship | **Caller / callee** |
| Same-tier relationship | **Peer / sibling** |
| Intended structure | **Declared topology** |
| Measured relationships | **Observed fields** |
| Repeated evidence against a boundary | **Boundary pressure** |
| Low-pressure candidate separation | **Candidate boundary** |
| Thing being placed | **Component** |
| Its declared address | **Position** |

Keep **layer** and **abstraction tier** separate. Keep **component** (the thing)
and **position** (where it belongs) separate.

## Living-System Translation

In Full mode, keep the natural analogy visible throughout the workflow. In
Rapid mode, use `Natural lens: none` unless the user explicitly asks for a
candidate-generating analogy; an analogy request that affects the decision
escalates to Full.

| Morphogenetic role | Software meaning |
| --- | --- |
| **Genetic scaffold** | Declared topology, invariants, and allowed interfaces |
| **Morphogen fields** | Static, runtime, change, data, and failure pressure |
| **Differentiation** | PLACE, MOVE, or SPLIT into a clearer responsibility |
| **Remodeling / pruning** | MERGE, remove an edge, or retire an obsolete component |
| **Homeostasis** | Bounded feedback, observability, verification, and enforcement |

When Full uses a natural lens, choose it only after declaring the skeleton and
available evidence, but before selecting a topology decision. Read
[references/natural-pattern-atlas.md](references/natural-pattern-atlas.md) to
select and transfer a mechanism. Use `none` when no analogy preserves the
natural system's relevant objective and constraints.

## 1. Declare the Skeleton

Assign every component a position:

```text
Domain / abstraction tier / layer
```

Apply these placement rules:

- Place one cohesive capability at one primary position.
- Model subdomains as nested domain paths; do not force a naturally nested
  capability into a flat domain list.
- Connect an outbound interface only to an allowed inbound interface.
- Route cross-domain access through a named boundary component or public
  contract.
- Treat a layer jump greater than one as a **layer-skip violation** unless a
  named adapter owns the transition.
- Let lower abstraction tiers serve higher tiers; forbid lower tiers from
  orchestrating their callers.
- Expose internals only through the component's inbound interface.

Preserve dependency inversion: source-code imports may point toward an
abstraction even when runtime control flows toward infrastructure.

## 2. Separate Static and Runtime Topology

Define the projection before judging a cycle:

| Projection | Required shape | Typical evidence |
| --- | --- | --- |
| Static dependency / ownership / authority | Directed, acyclic, shallow | Imports, package edges, build references |
| Runtime request flow | Directed; cycles allowed only when named and bounded | Traces, RPC calls, message routes |
| State transition / feedback | Cycles allowed with explicit semantics | State machines, retries, event loops |
| Change affinity | Undirected weighted evidence | Co-change history |
| Shared-data coupling | Directed or undirected, declared per dataset | Schema ownership, reads/writes |
| Failure propagation | Directed weighted evidence | Incidents, retry storms, cascading errors |

Reject every forbidden static cycle. For an intentional runtime cycle, name its
termination condition, retry/iteration bound, owner, and observability. Do not
use a queue, registry, callback, or event bus to conceal static ownership.

## 3. Observe Pressure

Run this section in Full mode. Rapid records proposed or current static edges
and may declare one already-identified runtime loop; needing any other observed
field triggers escalation.

Use only evidence available for the system. Mark missing fields **Not measured**;
never replace absent telemetry with intuition.

Collect:

- **Static dependency pressure** — imports or calls that cross a declared
  boundary.
- **Runtime-flow pressure** — traffic volume, latency, or coordination across
  positions.
- **Change pressure** — files or components that repeatedly change together.
- **Data pressure** — shared schemas, state, transactions, or write ownership.
- **Failure pressure** — faults that propagate across boundaries or depend on a
  single critical path.

Read [references/evidence-fields.md](references/evidence-fields.md) when an audit
uses history, telemetry, weighted fields, or graph partitioning. Keep the core
placement workflow in this file.

Before calculating a weighted candidate, declare that field's baseline,
metric, threshold, evidence window, minimum candidate size, and sensitivity
rule. Do not tune the policy after seeing a preferred cut. A hard invariant
such as a forbidden static cycle does not need a numeric threshold, but its
graph result must still be reproducible.

Read [references/graph-analysis.md](references/graph-analysis.md) and run the
bundled analyzer when computing SCCs, Fiedler/spectral cuts, normalized cuts,
conductance, or sensitivity. If no executable output is available, mark graph
analysis **Not measured** and do not report an algorithmic candidate.

## 4. Select a Natural Lens

In Full mode, select at most two lenses from the natural pattern atlas. In
Rapid mode, skip this section and report `Natural lens: none` unless the
analysis has already escalated. State the transfer before using it:

```text
Natural system:  <system and pattern>
Mechanism:       <what produces or preserves the natural form>
Software match:  <shared objective, pressure, and constraint>
Candidate:       <placement or topology change the mechanism suggests>
Break point:     <where the analogy stops>
```

Use the candidate to direct observation, not to replace it. For example,
adaptive transport can suggest reinforcing a valuable interface and pruning an
unused edge, while runtime and change evidence determine whether either action
is justified. Mark the lens `inspiration only` when using sacred geometry,
Fibonacci forms, or cymatic imagery without an equivalent measurable mechanism.

## 5. Diagnose Mismatches

Use these finding names and tests:

| Finding | Test |
| --- | --- |
| **layer-skip violation** | A static edge crosses more than one layer without a named adapter |
| **tier inversion** | A primitive statically orchestrates a higher abstraction tier |
| **cross-domain coupling** | A caller bypasses the target domain's inbound interface |
| **forbidden import cycle** | The static dependency projection contains a cycle |
| **god component** | One component owns unrelated edge clusters or multiple independent change reasons |
| **hidden runtime coupling** | A bus, registry, callback, global, or shared state creates an undeclared edge |
| **external SDK bypass** | Code reaches an external SDK outside its owning adapter |
| **placement ambiguity** | Domain, tier, or layer cannot be stated independently |
| **boundary-pressure mismatch** | Multiple observed fields repeatedly cross a declared boundary |
| **false boundary** | Components share purpose, lifecycle, and strong affinity but are separated without an independent reason |
| **resilience bottleneck** | One component or edge carries disproportionate failure impact without an explicit recovery path |
| **topology drift** | Declared rules and current static/runtime evidence no longer agree |

Treat a single noisy signal as a review prompt. Require a domain reason plus an
independent observed field whose predeclared policy is met before changing a
boundary, unless a hard invariant such as an import cycle or ownership
violation already decides the case. Return DEFER when a threshold or sensitivity
rule is missing, retrofitted, or unstable.

## 6. Choose the Smallest Evolution

Select one decision:

| Decision | Apply when |
| --- | --- |
| **PLACE** | A new component has one clear position, interface, and allowed neighbor set |
| **KEEP** | Declared placement and observed evidence agree |
| **MOVE** | One component has a clear primary position elsewhere |
| **SPLIT** | Independent capability/change/failure clusters occupy one component |
| **MERGE** | A boundary separates one purpose and lifecycle without reducing coupling or risk |
| **INTRODUCE-BOUNDARY** | Cross-position access needs one explicit contract or adapter |
| **DECLARE-RUNTIME-CYCLE** | A legitimate feedback loop lacks bounds, ownership, or observability |
| **DEFER** | Evidence is missing, contradictory, or too noisy to justify movement |

Rapid may finish only with PLACE, KEEP, DECLARE-RUNTIME-CYCLE, or DEFER. If a
restructuring decision becomes plausible, record the candidate, set
`Analysis mode: Rapid → Full`, and continue in Full. If the Full evidence is
unavailable, remain in Full and emit DEFER with the missing proof in
**Next action**.

Apply these growth rules:

- Attach a new component to the nearest semantically coherent parent whose
  public contract can own the relationship.
- Preserve sibling symmetry by default; specialize only when lifecycle,
  constraints, or measured pressure differ.
- Split along the axis that explains the strongest independent clusters:
  domain, abstraction tier, or layer.
- Prune an edge only after checking reachability, callers, and relevant history.
- Prefer one explicit boundary over multiple peer-to-peer exceptions.
- Reassess after material domain, traffic, ownership, or deployment changes.

## 7. Measure and Enforce

Before accepting MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY:

1. Use `structural-simplification` to report Component-kinds Δ,
   Dependency-edges Δ, Max-chain-depth Δ, and Module-count Δ.
2. Reject a forbidden cycle even when another complexity axis improves.
3. Hand every static dependency constraint to `architecture-as-code`.
4. Keep runtime, co-change, data, and failure findings as review, telemetry, or
   runtime-policy checks unless a deterministic repository rule can encode them.

In standalone use, do not emit MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY while
that measurement is unavailable. Emit DEFER, name the candidate evolution in
**Next action**, and identify the graph or baseline needed to measure it. PLACE,
KEEP, DECLARE-RUNTIME-CYCLE, and DEFER do not require a restructuring delta.

Use this handoff shape:

```text
Principle:   <locality | direction | interface | SDK ownership>
Constraint:  <component-pattern> may/must not depend on <component-pattern>
Enforcement: add/update architecture rule: <exact constraint>
```

Introduce new lint rules at `warn`; promote each rule to `error` after its
violations clear.

## 8. Audit Output

For a simple PLACE with no finding, omit the findings table. Otherwise, emit one
row per finding:

| Component / edge | Declared position | Observed pressure | Finding | Evidence / confidence | Decision | Next action | Verification |
| --- | --- | --- | --- | --- | --- | --- | --- |

Then emit:

```text
Subject:             <module / service / dependency graph>
Mode:                Design | Audit
Analysis mode:       Rapid | Full | Rapid → Full
Selection reason:    <bounded static check | explicit Full request | exact escalation condition>
Decision:            PLACE | KEEP | MOVE | SPLIT | MERGE | INTRODUCE-BOUNDARY |
                     DECLARE-RUNTIME-CYCLE | DEFER
Declared topology:   <Domain / abstraction tier / layer + allowed interfaces>
Observed fields:     <static | runtime | change | data | failure | Not measured>
Decision policy:     <field: baseline + metric/operator/threshold + window + sensitivity | hard invariant | Not declared>
Graph analysis:      <script/tool + version + input/result hash | Not measured | Not required>
Natural lens:        <pattern | none | inspiration only>
Transfer:            <mechanism → candidate; break point; evidence accepted/rejected it>
Static cycle:        Pass | Fail | Not evaluated
Runtime cycles:      <none | named cycle + bound/owner/observability>
Boundary evidence:   <domain reason + independent field, or insufficient>
Enforcement:         <none | add/update architecture rule: exact constraint>
Measurement:         <structural-simplification result | Not required + reason>
Next action:         <move, split, merge, add interface, instrument, or stop>
Verification:        <graph/lint/test/telemetry check>
```

Always emit the summary block in Design and Audit mode. Keep values terse when
the user asks for a concise answer; do not omit fields. Make the natural
mechanism and its break point understandable to a coder; do not let it count as
an observed field. Emit exactly one decision from the vocabulary above and put
qualifications in **Boundary evidence** or **Next action**.

Do not claim that observed agreement proves an architecture optimal. Report the
evidence window and residual judgment.

## See Also

- **`architecture-guidelines`** — decide what belongs inside a component.
- **`structural-simplification`** — measure whether an evolution is simpler.
- **`architecture-as-code`** — enforce static dependency constraints.
- **`defect-shift-left`** — move each topology defect to its earliest reliable check.
