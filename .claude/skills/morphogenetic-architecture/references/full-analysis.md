# Morphogenetic Architecture — Full Analysis

Read when the mode selector in [SKILL.md](../SKILL.md) starts in **Full** or a
Rapid scan records `Rapid → Full`. Rapid never needs this file. Section
numbers match the stubs in SKILL.md; §1, §2, §8, and the decision table of §6
stay there and apply in both modes.

## Living-System Translation

The workflow follows morphogenesis: the declared topology acts as a genetic
scaffold, observed fields expose developmental pressure, topology decisions
differentiate or remodel the structure, and verification maintains
homeostasis. Treat this as a disciplined transfer of mechanisms, not a claim
that software is literally alive.

In Full mode, keep the natural analogy visible throughout the workflow. It is
a way of thinking about the workflow, not a report field. An analogy request
that could affect the decision escalates to Full.

| Morphogenetic role | Software meaning |
| --- | --- |
| **Genetic scaffold** | Declared topology, invariants, and allowed interfaces |
| **Morphogen fields** | Static, runtime, change, data, and failure pressure |
| **Differentiation** | PLACE, MOVE, or SPLIT into a clearer responsibility |
| **Remodeling / pruning** | MERGE, remove an edge, or retire an obsolete subsystem |
| **Homeostasis** | Bounded feedback, observability, verification, and enforcement |

A natural mechanism reaches the report only as a §4 **second candidate** with
generator `natural lens`, and only after it satisfies the atlas's
Candidate-Contribution Test. Read
[natural-pattern-atlas.md](natural-pattern-atlas.md) before using one. A
mechanism that adds nothing to the generator-free baseline, or that no unused
independent field or held-out window can falsify, contributes nothing and is
not reported.

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
and position legality. For a placement that establishes a new cross-domain or
cross-layer edge, name in **Next action** the future validating field, its
expected direction, the evidence window, and the recheck trigger; a PLACE
record still carries no **Prediction** line (SKILL.md §8). A restructuring in
an evidence-poor system follows the probationary path in §5.

Collect:

- **Static dependency pressure** — imports or calls that cross a declared
  boundary.
- **Runtime-flow pressure** — traffic volume, latency, or coordination across
  positions.
- **Change pressure** — files or subsystems that repeatedly change together.
- **Data pressure** — shared schemas, state, transactions, or write ownership.
- **Failure pressure** — faults that propagate across boundaries or depend on a
  single critical path.

Read [evidence-fields.md](evidence-fields.md) when an audit uses history,
telemetry, weighted fields, or graph partitioning.

Before calculating a weighted candidate, declare that field's baseline,
metric, threshold, evidence window, minimum candidate size, and sensitivity
rule. Do not tune the policy after seeing a preferred cut. A hard invariant
such as a forbidden static cycle does not need a numeric threshold, but its
graph result must still be reproducible.

Read [graph-analysis.md](graph-analysis.md) and run the bundled analyzer when
computing SCCs, Fiedler/spectral cuts, normalized cuts, conductance, or
sensitivity. If no executable output is available, mark graph analysis
**Not measured** and do not report an algorithmic candidate.

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
- a **natural lens** from [natural-pattern-atlas.md](natural-pattern-atlas.md)
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

The seven position-legality findings in SKILL.md §5 need no observed field.
The findings below need observed evidence. Use these names and tests:

| Finding | Test |
| --- | --- |
| **god subsystem** ("god component") | One subsystem owns unrelated edge clusters or multiple independent change reasons |
| **hidden runtime coupling** | A bus, registry, callback, global, or shared state creates an undeclared edge |
| **boundary-pressure mismatch** | Multiple observed fields repeatedly cross a declared boundary |
| **false boundary** | Subsystems share purpose, lifecycle, and strong affinity but are separated without an independent reason |
| **resilience bottleneck** | One subsystem or edge carries disproportionate failure impact without an explicit recovery path |
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

## 6. Restructuring Growth Rules

The decision table and the placement rules stay in SKILL.md §6. These apply
once a restructuring is on the table:

- Split along the axis that explains the strongest independent clusters:
  domain, abstraction tier, or layer.
- Prune an edge only after checking reachability, callers, and relevant history.
- Retire a subsystem through an explicit removal signal — deprecation marker,
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
  subsystem count, team count, traffic, or data volume changes by an order of
  magnitude.

## 7. Measure a Restructuring

Before accepting MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY:

1. Use `structural-simplification` to report Subsystem-kinds Δ,
   Dependency-edges Δ, Max-chain-depth Δ, and Subsystem-count Δ.
2. Reject a forbidden cycle even when another complexity axis improves.
3. Hand every static dependency constraint to `architecture-as-code` per
   SKILL.md §7.
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
- The §6 reassessment triggers (order-of-magnitude changes in subsystems,
  teams, traffic, or data) feed that standing check; they are not prose to
  remember.
