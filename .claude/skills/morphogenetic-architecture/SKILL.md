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
    comparing observed behavior with declared architecture, or revisiting a
    closed prediction window. SKIP for routine
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
   from retained executable output, never from a narrated calculation. When
   pressure cannot yet be measured, the probationary path in §5 may apply;
   measured contradiction always blocks.
5. **Transfer mechanisms, not silhouettes.** When a natural mechanism supplies
   a second candidate, record the generator-free baseline first, use one
   indexed mechanism to generate a distinct alternative or expose a missed
   risk, and predeclare what would reject it. Then let software evidence
   accept or reject both candidates.
   Never choose a topology because it resembles a spiral, tree, honeycomb, or
   sacred figure.
6. **Preserve one owner per rule.** Hand complexity measurement to
   `structural-simplification`, internal design to `architecture-guidelines`,
   and enforceable edges to `architecture-as-code`.
7. **Escalate proof monotonically.** Start with the smallest sufficient
   analysis mode, but never let a request for speed waive evidence,
   measurement, or hard-invariant checks.
8. **Scale proof to reversibility.** Grade how expensive the change would be to
   undo, then require evidence proportional to that cost. A cheap-to-reverse
   change still obeys every hard invariant; a hard-to-reverse change is never
   accepted on one field.
9. **Close the loop.** Every accepted restructuring is a hypothesis: record
   the field it should improve, the window, and the recheck trigger, then
   re-enter Audit when the window closes. Route a systematic prediction miss
   to `continuous-improvement`.

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

In Full mode, keep the natural analogy visible throughout the workflow. It is
a way of thinking about the workflow, not a report field. An analogy request
that could affect the decision escalates to Full.

| Morphogenetic role | Software meaning |
| --- | --- |
| **Genetic scaffold** | Declared topology, invariants, and allowed interfaces |
| **Morphogen fields** | Static, runtime, change, data, and failure pressure |
| **Differentiation** | PLACE, MOVE, or SPLIT into a clearer responsibility |
| **Remodeling / pruning** | MERGE, remove an edge, or retire an obsolete component |
| **Homeostasis** | Bounded feedback, observability, verification, and enforcement |

A natural mechanism reaches the report only as a §4 **second candidate** with
generator `natural lens`, and only after it satisfies the atlas's
Candidate-Contribution Test. Read
[references/natural-pattern-atlas.md](references/natural-pattern-atlas.md)
before using one. A mechanism that adds nothing to the generator-free
baseline, or that no unused independent field or held-out window can falsify,
contributes nothing and is not reported.

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
- Expose internals only through the component's inbound interface.

Preserve dependency inversion: source-code imports may point toward an
abstraction even when runtime control flows toward infrastructure.

### Position Legality

Check the edges of the component being placed, not every edge in the
repository. This is a **design-time check on a proposed or changed
position** — its inbound and outbound edges, a handful at a time. Auditing a
whole codebase from three axes is an explicit non-goal: a derived rule loses
to one that states intent, so turn the result into `architecture-as-code`
rules that name each edge and its reason, and let those carry the standing
check. Positions belong in the repository as a reviewed artefact that fails
the build when a component arrives unpositioned; never re-derive them per
audit.

Each proposed edge satisfies one clause per axis. The clauses need no observed
field and run before §3. Layer and tier read from declared positions and the
static graph; the domain clause needs a third input, the target's declared
inbound interface, and cannot run without it.

| Axis | Kind | Legal edge | Violation |
| --- | --- | --- | --- |
| **Layer** | ordinal | Same layer; one step toward infrastructure; or toward the consumer when it points at an abstraction the target layer owns (dependency inversion) | **layer-skip violation** — more than one step, unless either endpoint is the declared adapter owning that transition. **layer inversion** — toward the consumer with no dependency inversion |
| **Abstraction tier** | ordinal | Same tier, or a higher tier calling a lower tier | **tier inversion** — a lower tier statically orchestrates its caller. A type-only edge is erased before runtime and can never orchestrate, so it cannot violate this clause |
| **Domain** | categorical | The same domain path; a path nested inside it; or the target domain's declared inbound interface | **cross-domain coupling** — a caller bypasses that inbound interface |

Layer and abstraction tier are ordinal, so "one step" is meaningful on them.
Domain is categorical: two paths are the same, one contains the other, or they
are unrelated. Containment is not distance — `commerce/payments` sits inside
`commerce`, but it is no closer to `commerce/shipping` than to `identity`, and
sibling paths never inherit permission from a shared prefix.

Three definitions the clauses stand on:

- **Inbound interface** — the contract a domain publishes for callers: a package
  entry point, an exported public surface, or a declared allowlist. Where it is
  a hand-maintained allowlist, the domain clause is a configuration file rather
  than a derived rule. Say so, and keep the list under review; the clause is
  never better than that list.
- **Re-export module** — a module that only re-exports. It takes no position of
  its own; resolve each edge through it to what it re-exports.
- **External SDK** — a third-party runtime dependency, not a language or runtime
  builtin. The clause is about reaching one at value granularity; importing its
  types is not a bypass.

Two whole-graph clauses complete the check:

- The static dependency projection must be acyclic; report the result in
  **Static cycle**.
- Code reaches an external SDK only inside its owning adapter; an escape is
  an **external SDK bypass**.

None of this is sliceable. Each per-axis clause needs a position for both
endpoints of every edge it judges, and acyclicity needs the whole dependency
closure, so placing one component still means positioning what it touches.

A **composition root** — a module whose whole job is wiring everything together
— is exempt from the domain and tier clauses by declaration. "One cohesive
capability at one primary position" has no answer for a module built to be
incohesive; name it as the composition root and move on rather than forcing a
position it cannot have.

When domain, tier, or layer cannot be stated independently for a component,
the check cannot run: report **placement ambiguity** and resolve the position
before continuing. The domain clause blocks the same way when a target domain
publishes no inbound interface — declare the interface rather than reading
every cross-domain edge as a violation, which is what an undeclared boundary
makes them all look like. When an axis does not apply to the system at hand,
record it as **Not applicable** with the reason; do not invent an ordering to
fill it. Legality is necessary, never sufficient — a legal edge
can still be wrong for reasons only §3's fields expose.

## 2. Separate Static and Runtime Topology

Define the projection before judging a cycle:

| Projection | Required shape | Typical evidence |
| --- | --- | --- |
| Static dependency | Directed, acyclic per component, shallow | Imports, package edges, build references |
| Ownership / authority | Directed, acyclic per concern | Declared owners, handoffs, decision records |
| Runtime request flow | Directed; cycles allowed only when named and bounded | Traces, RPC calls, message routes |
| State transition / feedback | Cycles allowed with explicit semantics | State machines, retries, event loops |
| Change affinity | Undirected weighted evidence | Co-change history |
| Shared-data coupling | Directed or undirected, declared per dataset | Schema ownership, reads/writes |
| Failure propagation | Directed weighted evidence | Incidents, retry storms, cascading errors |

Reject every forbidden static cycle. For an intentional runtime cycle, name its
termination condition, retry/iteration bound, owner, and observability. Do not
use a queue, registry, callback, or event bus to conceal static ownership.

Authority is acyclic **per concern**, not per component. Two components may
each defer to the other on a different concern — one owning meaning while
the other owns measurement, say — and that is a clean partition, not a
cycle. Name the concern on every authority edge; a cycle exists only when two
components claim authority over the same one. Import cycles have no such
escape: a build cannot order them however the concerns are split.

## 3. Observe Pressure

Run this section in Full mode. Rapid records proposed or current static edges
and may declare one already-identified runtime loop; needing any other observed
field triggers escalation.

Use only evidence available for the system. Mark missing fields **Not measured**;
never replace absent telemetry with intuition.

A greenfield or young system legitimately reports **Not measured** on every
historical and runtime field; that is absence of history, not a defect.
§1's position legality still runs at full strength there — it needs no
field — and it is this skill's whole contribution until the first field
becomes measurable. Decide placement from domain meaning, declared topology,
and position legality, and
for a placement that establishes a new cross-domain or cross-layer edge,
predeclare in **Prediction** the future validating field, its expected
direction, the evidence window, and the recheck trigger. A restructuring in
an evidence-poor system follows the probationary path in §5.

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

Record which field values and windows produced the question, finding, and
generator-free baseline. Discovery evidence may generate that baseline, but
the same observations cannot later count as prospective falsification of a
second candidate.

## 4. Generate a Second Candidate

In Full mode, first record the candidate suggested by declared topology, domain
meaning, hard-invariant checks, and the discovery evidence already inspected;
`none` is a valid baseline. Rapid skips this section.

Before accepting a Medium- or Low-reversibility restructuring, generate one
independent second candidate or record `Second candidate: none` with the
reason no generator produced a distinct viable alternative. Any generator
qualifies, each under its own discipline:

- an **algorithmic cut** from §3 — declared policy, sensitivity check, and
  retained executable output;
- a **natural lens** from
  [references/natural-pattern-atlas.md](references/natural-pattern-atlas.md)
  — enter through its Operational Lens Index, select at most one lens,
  and satisfy its Candidate-Contribution Test before the candidate counts;
- a **manual alternative decomposition** along a different axis (domain,
  abstraction tier, or layer) — its rejection condition named before its
  validation surface is inspected.

A High-reversibility change may mark the field
`Not required — high reversibility`. PLACE, KEEP, and
DECLARE-RUNTIME-CYCLE omit the field with the rest of the §8 restructuring
set, and Rapid never emits it; a DEFER that withholds a restructuring marks
it **Not required** with a short reason. A second candidate widens the option set;
it never lowers the evidence bar, and baseline and second candidate face the
same software-evidence policy. `Second candidate: none` must name which
generators were attempted and why each produced nothing distinct; a second
candidate that is produced and rejected records its rejection under the same
evidence policy as the baseline.

Whatever the generator, name the rejection condition and its validation
surface before inspecting that surface, then test baseline and second
candidate under the same software-evidence policy. Use a retained
contribution to extend the candidate set or expose risk, not to replace
evidence. A hard invariant such as a forbidden import cycle needs no second
candidate. The generator's name, mechanism, or analogy may never appear in
**Boundary evidence**.

## 5. Diagnose Mismatches

§1's position legality already decides seven findings without any observed
field: **layer-skip violation**, **layer inversion**, **tier inversion**,
**cross-domain coupling**, **forbidden import cycle**, **external SDK
bypass**, and **placement ambiguity** when the check cannot run. Those are
enforced by `architecture-as-code` as named edges; report the violation and
fix it, and do not re-argue them from evidence here.

The findings below need observed evidence. Use these names and tests:

| Finding | Test |
| --- | --- |
| **god component** | One component owns unrelated edge clusters or multiple independent change reasons |
| **hidden runtime coupling** | A bus, registry, callback, global, or shared state creates an undeclared edge |
| **boundary-pressure mismatch** | Multiple observed fields repeatedly cross a declared boundary |
| **false boundary** | Components share purpose, lifecycle, and strong affinity but are separated without an independent reason |
| **resilience bottleneck** | One component or edge carries disproportionate failure impact without an explicit recovery path |
| **topology drift** | Declared rules and current static/runtime evidence no longer agree |

Treat a single noisy signal as a review prompt. Require a domain reason plus an
independent observed field whose predeclared policy is met before changing a
boundary, unless §1's position legality already decides the case or the
probationary path below substitutes
its expiry, instrumentation, and reversal record for an absent field. That is
the floor; the reversibility grade below decides how much field agreement and
evidence window it takes to clear it. Return DEFER when a threshold or
sensitivity rule is missing, retrofitted, or unstable.

### Scale Proof to Reversibility

Grade the cost of undoing the proposed change before setting its evidence bar.
Grade only when a boundary actually moves: before accepting MOVE, SPLIT, MERGE,
or INTRODUCE-BOUNDARY, and when DEFER withholds one of them. PLACE, KEEP, and
DECLARE-RUNTIME-CYCLE omit the restructuring set entirely — they fill or
bound an existing position rather than change one.

The grade uses declared facts — consumers, published contracts, data, and
deployment coupling — so it needs no weighted evidence and no extra analysis
mode.

| Reversibility | Signals | Evidence bar for a boundary change |
| --- | --- | --- |
| **High** | One owner, internal callers only, no published contract, no data migration, one deployable | Domain reason plus one independent field; a shorter evidence window is acceptable when the reversal path is named |
| **Medium** | Several internal consumers, a shared internal contract, reversible data change, or a coordinated deploy | Domain reason plus one independent field meeting its declared policy, plus the sensitivity check for any generated candidate |
| **Low** | External or cross-team consumers, a published or versioned contract, irreversible data migration, or a separate deployment/ownership boundary | Domain reason plus two independent applicable fields that each meet their declared policy and support the same boundary; at least one field must have authority over the dominant reversal-cost driver. Also require a passing sensitivity check for any generated candidate and a staged path whose reversal step is explicit. If only one field is available, emit DEFER for the Low-reversibility end state; a separately specified precursor may proceed only after it is graded independently and meets its own evidence bar. |

Grade from the least-reversible known signal. When the facts needed to exclude a
Low signal cannot be stated, report **Reversibility: Unknown — Low bar applies**,
name the missing consumer, contract, data, deployment, or ownership facts in
**Next action**, and do not accept the Low-reversibility end state until they
are resolved. Grade any separately specified precursor independently.

Reversibility never lowers a hard invariant, never authorizes a Rapid
restructuring decision, and never substitutes for the §7 structural
measurement.

### Probationary Acceptance

When every hard invariant passes, the §7 structural measurement is met, and
the only missing proof is a required observed field that cannot be measured
within the decision window — no history yet, no instrumentation in place, or
an infeasible measurement cost — accept the restructuring probationarily
instead of holding an indefinite DEFER:

- Reversibility must be High, or Medium with a named reversal path. Low or
  Unknown reversibility never accepts probationarily.
- Probation covers absent evidence only. A measured field that contradicts
  the change, a failed declared policy, or a defective policy on a measured
  field still blocks; probation never overrides disagreement.
- Absent means unobtainable, not unfetched. A field derivable from the
  repository or VCS history already present — co-change and schema/data
  ownership above all — is never eligible for probation; measure it first.
- Record in **Boundary evidence**: `probationary — <domain reason> + <why
  the field cannot be measured> + expiry or revisit trigger + instrumentation
  task + reversal path`.
- Record in **Prediction** the field the instrumentation will measure, the
  expected direction, and the evidence window.
- At expiry, re-enter this skill in Audit mode on the bounded scope. A
  confirmed prediction upgrades the acceptance to measured; a miss triggers
  the reversal path or an explicit re-decision — never silent retention.
- The path exists only in Full; Rapid still finishes with its four decisions.

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
- Retire a component through an explicit removal signal — deprecation marker,
  reachability proof, owner, and cleanup path — never by leaving it unreferenced.
- Prefer one explicit boundary over multiple peer-to-peer exceptions.
- Prefer a probationary acceptance with instrumentation over an indefinite
  DEFER when evidence is absent and reversibility permits; when measured
  evidence contradicts the change, DEFER stands.
- At Low reversibility, take the smallest reversible step first: introduce the
  boundary or adapter, then move behind it once the contract holds.
- When reversibility is Unknown, DEFER the end state but independently grade
  any smaller precursor that could safely establish the missing facts.
- Reassess after material domain, ownership, or deployment changes, and when
  component count, team count, traffic, or data volume changes by an order of
  magnitude.

## 7. Measure and Enforce

Before accepting MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY:

1. Use `structural-simplification` to report Component-kinds Δ,
   Dependency-edges Δ, Max-chain-depth Δ, and Module-count Δ.
2. Reject a forbidden cycle even when another complexity axis improves.
3. Hand every static dependency constraint to `architecture-as-code`, §1's
   position-legality clauses first — they are rules, not report rows.
4. Keep runtime, co-change, data, and failure findings as review, telemetry, or
   runtime-policy checks unless a deterministic repository rule can encode them.
5. For a Low-reversibility change, record the staged path and its explicit
   reversal step in **Next action** before the change is accepted.
6. Record **Prediction** for every accepted MOVE, SPLIT, MERGE, or
   INTRODUCE-BOUNDARY: the observed field expected to improve, its direction,
   the evidence window, and the recheck trigger. Hand executed-evidence state
   and freshness to `requirements-traceability`.

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

### Close the Loop

Acceptance is not validation. When a prediction window or probationary expiry
closes, re-enter this skill in Audit mode scoped to the affected boundary and
compare the prediction with the new measurement. A confirmed prediction ends
the probation; a miss triggers the named reversal path or an explicit
re-decision. Route a systematic prediction miss — the same rule predicting
wrongly across decisions — to `continuous-improvement` as a skill defect.

Every probationary acceptance goes into a durable register that the standing
check reads, one row per open probation: subject, decision, expiry or revisit
trigger, instrumentation task, reversal path, and owner. Name the register's
location in **Next action**; `defect-shift-left` places the check that reads
it. A probation missing from the register has no trigger surface and is
silent retention by another name.

Keep drift detection standing rather than event-driven:

- Static drift fails the build once its `architecture-as-code` rule reaches
  `error`; until promotion, the rule's violations are carried by the
  scheduled comparison in the next bullet, and the promotion step is recorded
  in the accepted change's **Next action**.
- Everything the build does not fail on — new cross-boundary runtime edges,
  co-change outliers, expired predictions, and static rules still at `warn` —
  gets a scheduled declared-vs-observed comparison with a named owner; place
  it with `defect-shift-left` and leave pipeline execution to CI/CD.
- The §6 reassessment triggers (order-of-magnitude changes in components,
  teams, traffic, or data) feed that standing check; they are not prose to
  remember.

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
Position legality:   Pass | Fail: <violation + edge> | Not evaluated
Observed fields:     <static | runtime | change | data | failure | Not measured>
Decision policy:     <field: baseline + metric/operator/threshold + window + sensitivity | hard invariant | Not declared>
Graph analysis:      <script/tool + version + input/result hash | Not measured | Not required>
Candidate baseline:  <generator-free candidate | none>
Second candidate:    <candidate or exposed risk + generator | none + generators
                     attempted + why each produced nothing | Not required + reason>
Static cycle:        Pass | Fail | Not evaluated
Runtime cycles:      <none | named cycle + bound/owner/observability>
Boundary evidence:   <domain reason + independent field | probationary —
                     reason + why unmeasurable + expiry + instrumentation +
                     reversal path | insufficient>
Reversibility:       <high | medium | low + dominant reversal-cost driver |
                     Unknown — Low bar applies + missing facts | Not required + reason>
Prediction:          <field + direction + window + recheck trigger |
                     Not required + reason>
Enforcement:         <none | add/update architecture rule: exact constraint>
Measurement:         <structural-simplification result | Not required + reason>
Next action:         <move, split, merge, add interface, instrument, or stop>
Verification:        <graph/lint/test/telemetry check>
```

Seven fields form the **restructuring set**: `Decision policy`, `Graph
analysis`, `Candidate baseline`, `Second candidate`, `Reversibility`,
`Prediction`, and `Measurement`. Emit them on the same trigger as the §5
reversibility grade — before accepting MOVE, SPLIT, MERGE, or
INTRODUCE-BOUNDARY, and when DEFER withholds one of them. PLACE, KEEP, and
DECLARE-RUNTIME-CYCLE omit all seven; Rapid never emits them. Every other
field appears in every report.

Always emit the summary block in Design and Audit mode. Keep values terse when
the user asks for a concise answer; do not omit a field your decision
requires. Make the second
candidate and its generator understandable to a coder; never let a generator's
name, mechanism, or analogy count as an observed field or appear in **Boundary
evidence**. Emit exactly one decision from the vocabulary above and put
qualifications in **Boundary evidence** or **Next action**.

Do not claim that observed agreement proves an architecture optimal. Report the
evidence window and residual judgment.

## See Also

- **`architecture-guidelines`** — decide what belongs inside a component.
- **`structural-simplification`** — measure whether an evolution is simpler.
- **`architecture-as-code`** — enforce static dependency constraints.
- **`defect-shift-left`** — move each topology defect to its earliest reliable check.
- **`continuous-improvement`** — route a systematic prediction miss to its rule.
