---
name: morphogenetic-architecture
description: >-
    Design and audit evolving, evidence-weighted software topology. Start with
    a rapid declared-topology scan; escalate to full analysis for
    restructuring, multi-field evidence, broad scope, ambiguity, or a deep
    audit. Place subsystems by domain, abstraction tier, and layer; preserve
    directed interfaces; compare imports, runtime flow, co-change, shared data,
    and failure propagation; then place, keep, move, split, merge, or introduce
    a boundary. TRIGGER when placing a subsystem/service/layer, refactoring
    dependency topology, discovering bounded contexts, diagnosing cycles,
    god-subsystems, cross-domain tangles, or hidden runtime coupling, or
    comparing observed behavior with declared architecture, or revisiting a
    closed prediction window. SKIP for routine
    in-boundary logic, isolated bug fixes, content/CSS edits, dependency bumps,
    and trivial renames. Use `architecture-guidelines` for subsystem internals,
    `structural-simplification` for complexity deltas, and
    `architecture-as-code` for enforceable dependency rules.
---

# Morphogenetic Architecture

Shape software topology through local rules, declared boundaries, and measured
pressure. Preserve the Domain / abstraction tier / layer placement model as the
declared skeleton; use observed relationships to test and evolve that skeleton
instead of treating the initial grid as permanent truth.

## Core Directives

1. **Declare before observing.** Record intended placement and allowed
   dependency direction before using telemetry or history to challenge it.
2. **Keep projections distinct.** Keep static imports, runtime interaction,
   change affinity, shared data, and failure propagation as separate graphs.
   Never hide an invalid static edge inside an acceptable runtime cycle.
3. **Prefer local rules.** Make each subsystem depend on a small, named neighbor
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
   whole-graph or service-graph architecture audit. A bare Alchemy `FULL` dispatch
   traverses gates but does not override this skill's selector.
2. Otherwise start in **Rapid**: read
   [references/rapid-topology-scan.md](references/rapid-topology-scan.md)
   and [references/position-legality.md](references/position-legality.md)
   before declaring a position. Rapid's procedure, hard tests, and decision
   guard and the legality clause table live only there; this file
   summarizes them.
3. Escalate from Rapid to Full before selecting a decision when any of these
   conditions appears:
   - MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY becomes a candidate;
   - a decision depends on runtime pressure, co-change, shared data, failure
     propagation, weighting, or graph partitioning rather than merely
     declaring one bounded runtime loop;
   - the scope crosses several domains/subsystems or a material ownership,
     security, compliance, or failure boundary;
   - placement is ambiguous, observed signals conflict, or the Rapid result
     cannot be justified from declared topology and hard invariants alone.
4. Once Full begins, do not downgrade because evidence is unavailable. Record
   missing fields as **Not measured** and emit DEFER when the proof requirement
   cannot be met.
5. On entering Full, read
   [references/full-analysis.md](references/full-analysis.md) before §3. It
   holds §§3–7's full-mode procedure and routes to
   [references/evidence-fields.md](references/evidence-fields.md),
   [references/graph-analysis.md](references/graph-analysis.md), and
   [references/natural-pattern-atlas.md](references/natural-pattern-atlas.md).
   A run that stays in Rapid reads only the two files step 2 names.

An explicit `rapid` or `quick` request may select the starting mode, but it
cannot authorize a restructuring decision. Rapid must either finish with one
of its four decisions or record `Rapid → Full` and continue at Full. Do not
rerun checks already completed unless Full requires a broader evidence scope.

## Reporting Vocabulary

Use coder-facing terms in every report:

| Meaning | Coder-facing field |
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
| Thing being placed | **Subsystem** — a part of the system produced by decomposition; where change lands |
| Its declared address | **Position** |
| Property holding across positions | **Aspect** — one obligation, one mechanism subsystem |
| Positions an aspect binds | **Holds across** — declared at subsystem granularity here; the scope → subsystem mapping is this skill's placement decision |

Keep **layer** and **abstraction tier** separate. Keep **subsystem** (the thing)
and **position** (where it belongs) separate.

## 1. Declare the Skeleton

Assign every subsystem a position:

```text
Domain / abstraction tier / layer
```

Apply these placement rules:

- Place one cohesive capability at one primary position.
- Model subdomains as nested domain paths; do not force a naturally nested
  capability into a flat domain list.
- Connect an outbound interface only to an allowed inbound interface.
- Expose internals only through the subsystem's inbound interface.

Preserve dependency inversion: source-code imports may point toward an
abstraction even when runtime control flows toward infrastructure.

### Position Legality

Check the edges of the subsystem being placed: a design-time check on a
proposed or changed position, a handful of edges at a time, never a
whole-codebase audit from three axes. Each proposed edge satisfies one clause
per axis — **layer** (ordinal: same layer, one step toward infrastructure, or
toward the consumer only through dependency inversion), **abstraction tier**
(ordinal: same tier, or a higher tier calling a lower one), and **domain**
(categorical: the same path, a nested path, or the target's declared inbound
interface). Two whole-graph clauses complete it: the static projection is
acyclic, reported in **Static cycle**, and code reaches an external SDK only
inside its owning adapter. The clauses need no observed field, run before §3,
and decide the seven findings §5 names; turn every result into
`architecture-as-code` rules that name each edge and its reason. Read
[references/position-legality.md](references/position-legality.md) for the
clause table, the definitions of inbound interface, re-export module, and
external SDK, the composition-root exemption, **placement ambiguity**, and the
**Not applicable** rule. Legality is necessary, never sufficient — a legal
edge can still be wrong for reasons only §3's fields expose.

## 2. Separate Static and Runtime Topology

Define the projection before judging a cycle:

| Projection | Required shape | Typical evidence |
| --- | --- | --- |
| Static dependency | Directed, acyclic per subsystem, shallow | Imports, package edges, build references |
| Ownership / authority | Directed, acyclic per aspect | Declared owners, handoffs, decision records |
| Runtime request flow | Directed; cycles allowed only when named and bounded | Traces, RPC calls, message routes |
| State transition / feedback | Cycles allowed with explicit semantics | State machines, retries, event loops |
| Change affinity | Undirected weighted evidence | Co-change history |
| Shared-data coupling | Directed or undirected, declared per dataset | Schema ownership, reads/writes |
| Failure propagation | Directed weighted evidence | Incidents, retry storms, cascading errors |

Reject every forbidden static cycle. For an intentional runtime cycle, name its
termination condition, retry/loop bound, owner, and observability. Do not
use a queue, registry, callback, or event bus to conceal static ownership.

Authority is acyclic **per aspect**, not per subsystem. Two subsystems may
each defer to the other on a different aspect — one owning meaning while
the other owns measurement, say — and that is a clean partition, not a
cycle. Name the aspect on every authority edge; a cycle exists only when two
subsystems claim authority over the same one. Import cycles have no such
escape: a build cannot order them however the aspects are split.

## 3. Observe Pressure

Full only. Rapid records proposed or current static edges and may declare one
already-identified runtime loop; needing any other observed field triggers
escalation. Full collects static, runtime, change, data, and failure pressure,
marks missing fields **Not measured**, and declares each field's decision
policy before computing a candidate: see `references/full-analysis.md` §3.

## 4. Generate a Second Candidate

Full only; Rapid skips this section. Before accepting a Medium- or
Low-reversibility restructuring, record the generator-free baseline and one
independent second candidate, or `none` with the generators attempted: see
`references/full-analysis.md` §4.

## 5. Diagnose Mismatches

§1's position legality already decides seven findings without any observed
field: **layer-skip violation**, **layer inversion**, **tier inversion**,
**cross-domain coupling**, **forbidden import cycle**, **external SDK
bypass**, and **placement ambiguity** when the check cannot run. Those are
enforced by `architecture-as-code` as named edges; report the violation and
fix it, and do not re-argue them from evidence here.

Findings that need observed evidence — god subsystem, hidden runtime
coupling, boundary-pressure mismatch, false boundary, resilience bottleneck,
topology drift — and the evidence bar a boundary change must clear are Full
only: the reversibility grade, which never authorizes a Rapid restructuring,
and the probationary path, which exists only in Full. See
`references/full-analysis.md` §5.

## 6. Choose the Smallest Evolution

Select one decision:

| Decision | Apply when |
| --- | --- |
| **PLACE** | A new subsystem has one clear position, interface, and allowed neighbor set |
| **KEEP** | Declared placement and observed evidence agree |
| **MOVE** | One subsystem has a clear primary position elsewhere |
| **SPLIT** | Independent capability/change/failure clusters occupy one subsystem |
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

- Attach a new subsystem to the nearest semantically coherent parent whose
  public contract can own the relationship.
- Preserve sibling symmetry by default; specialize only when lifecycle,
  constraints, or measured pressure differ.

Restructuring growth rules (split, prune, retire, probation, staged steps,
reassessment triggers) are in `references/full-analysis.md` §6.

## 7. Measure and Enforce

Hand every static dependency constraint to `architecture-as-code`, §1's
position-legality clauses first — they are rules, not report rows. Before
accepting MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY, Full also measures the
structural deltas, records **Prediction**, and closes the loop when its window
ends: see `references/full-analysis.md` §7.

Use this handoff shape:

```text
Principle:   <locality | direction | interface | SDK ownership | aspect ownership>
Constraint:  <subsystem-pattern> may/must not depend on <subsystem-pattern>
Enforcement: add/update architecture rule: <exact constraint>
```

Introduce new lint rules at `warn`; promote each rule to `error` after its
violations clear.

For an aspect mechanism, **Declared topology** carries `Holds across` as an
indented continuation line, never a top-level line. The mechanism's exclusivity
edges are the handoff; the coverage check over the governed set routes to
`defect-shift-left`, like the probationary register in Full.

## 8. Audit Output

For a simple PLACE with no finding, omit the findings table. Otherwise, emit one
row per finding:

| Subsystem / edge | Declared position | Observed pressure | Finding | Evidence / confidence | Decision | Next action | Verification |
| --- | --- | --- | --- | --- | --- | --- | --- |

Then emit one summary block. Its first fourteen lines appear in every report;
the last seven, after `Verification`, are the restructuring set:

```text
Subject:             <subsystem / service / dependency graph>
Mode:                Design | Audit
Analysis mode:       Rapid | Full | Rapid → Full
Selection reason:    <bounded static check | explicit Full request | exact escalation condition>
Decision:            PLACE | KEEP | MOVE | SPLIT | MERGE | INTRODUCE-BOUNDARY |
                     DECLARE-RUNTIME-CYCLE | DEFER
Declared topology:   <Domain / abstraction tier / layer + allowed interfaces>
Position legality:   Pass | Fail: <violation + edge> | Not evaluated
Observed fields:     <static | runtime | change | data | failure | Not measured>
Static cycle:        Pass | Fail | Not evaluated
Runtime cycles:      <none | named cycle + bound/owner/observability>
Boundary evidence:   <domain reason + independent field | probationary —
                     reason + why unmeasurable + expiry + instrumentation +
                     reversal path | insufficient>
Enforcement:         <none | add/update architecture rule: exact constraint>
Next action:         <move, split, merge, add interface, instrument, recheck, or stop>
Verification:        <graph/lint/test/telemetry check>
Decision policy:     <field: baseline + metric/operator/threshold + window + sensitivity | hard invariant | Not declared>
Graph analysis:      <script/tool + version + input/result hash | Not measured | Not required>
Candidate baseline:  <generator-free candidate | none>
Second candidate:    <candidate or exposed risk + generator | none + generators
                     attempted + why each produced nothing | Not required + reason>
Reversibility:       <high | medium | low + dominant reversal-cost driver |
                     Unknown — Low bar applies + missing facts | Not required + reason>
Prediction:          <field + direction + window + recheck trigger |
                     Not required + reason>
Measurement:         <structural-simplification result | Not required + reason>
```

Seven fields form the **restructuring set**: `Decision policy`, `Graph
analysis`, `Candidate baseline`, `Second candidate`, `Reversibility`,
`Prediction`, and `Measurement`. Emit them on the same trigger as the §5
reversibility grade — before accepting MOVE, SPLIT, MERGE, or
INTRODUCE-BOUNDARY, and when DEFER withholds one of them. PLACE, KEEP, and
DECLARE-RUNTIME-CYCLE omit all seven; Rapid never emits them. Their record
ends at `Verification`: omit the lines, never fill them with `Not required`,
which is a value for a restructuring record only. A KEEP that rejected a
restructuring candidate is still a KEEP; put the rejected candidate and its
evidence in **Boundary evidence** and **Next action**. Every other field
appears in every report.

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

- **`architecture-guidelines`** — decide what belongs inside a subsystem.
- **`structural-simplification`** — measure whether an evolution is simpler.
- **`architecture-as-code`** — enforce static dependency constraints.
- **`defect-shift-left`** — move each topology defect to its earliest reliable check.
- **`continuous-improvement`** — route a systematic prediction miss to its rule.
