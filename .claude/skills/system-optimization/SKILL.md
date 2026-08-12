---
name: system-optimization
description: >-
    Applies Lean, Kaizen, Six Sigma, Theory of Constraints, queueing/flow
    science, and DevOps delivery metrics (DORA) to eliminate waste and improve
    flow across all aspects of a software project. Use when scanning for
    optimizations in CI/CD pipelines, developer workflows, code structure,
    testing strategy, documentation, or the overall value stream. Activate when
    a review is requested to identify waste, bottlenecks, and improvement
    opportunities across the project.
---

# System Optimization Protocol

> **Core Directives**
>
> 1. **Eliminate Waste First (Lean)**: Remove non-value-adding activities before
>    optimizing what remains.
> 2. **Fix the Constraint (ToC)**: The weakest link sets the throughput ceiling.
>    Find it; subordinate everything else.
> 3. **Stabilize Before Optimizing (Six Sigma)**: An unstable process cannot be
>    meaningfully improved.
> 4. **Build Quality In — Shift Left (DevOps)**: Embed quality at the source via
>    automation, types, and linting.
> 5. **Small Steps (Kaizen)**: Many small validated improvements compound faster
>    than infrequent large redesigns.
> 6. **Decide Late (Lean)**: Defer irreversible commitments until you have the
>    most information.
> 7. **Manage Flow, Not Utilization (Queueing)**: Throughput is limited by
>    queues, batch size, and variability — not by how busy each resource is.
>    High utilization *creates* delay; it does not cure it.

---

## Order of Operations

Apply these steps **in order**. The most expensive mistake is optimizing or
automating something that should have been deleted — work done out of order is
work to undo later.

1. **Question the requirement.** The requirement is the most upstream waste.
   Strip it to first principles before touching the implementation; the cheapest
   step is the one that no longer needs to exist. Separate each requirement's
   *obligation* (the outcome, evidence, or restriction that must exist) from its
   *mechanism* (the specific rights, routes, roles, record types, or protocols
   it names). Obligations are floors; pinned mechanism is negotiable — audit
   within the current requirements first to establish the floor, then propose
   careful requirement edits scored like any change, and gate edits with real
   external trade-offs as explicit product decisions (see
   `functionality-complexity-tradeoff` §1e).
2. **Probe deletion.** Try removing the step, file, stage, or component behind
   a reversible branch, feature flag, dry run, or narrow rollout. Restore
   anything proven load-bearing; keep only deletions backed by evidence.
3. **Simplify what remains.** Only optimize parts that survived deletion.
4. **Speed it up.** Parallelize, cache, batch — but only after simplification,
   and only within the limits parallelism actually returns (§7).
5. **Automate last.** Automating an unnecessary or unsimplified process locks in
   the waste.

## 1. Scan Layers

| Layer                      | Red flags                                                           |
| -------------------------- | ------------------------------------------------------------------- |
| **CI/CD & Automation**     | Sequential stages that could parallelize, manual steps, flaky gates |
| **Developer Workflow**     | Large PRs, long-lived branches, slow feedback loops                 |
| **Code Structure**         | Dead code, duplication, divergent patterns                          |
| **Public Surface**         | One route per view of the same aggregate, same data at multiple addresses, rights/roles vocabulary larger than the behavior it guards, one-user wrappers around an existing primitive |
| **Testing Strategy**       | Coverage gaps, flaky tests, defects caught late                     |
| **Tooling & Dependencies** | Unused packages, outdated tooling, manual steps                     |
| **Documentation**          | Stale docs, missing ADRs, over-documentation                        |
| **Observability**          | Missing metrics, silent failures, unclear alerts                    |

## 2. Waste Scan (Lean — Muda / Mura / Muri)

Lean names three families of waste. **Muda** is non-value-adding work; the
TIMWOODS table below enumerates its eight forms. But Muda is usually
*manufactured* by two deeper causes — attack these at the source first:

| Cause                     | Meaning                                | In Software                                                          | Red Flag                                       |
| ------------------------- | -------------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------- |
| **Mura** (unevenness)     | Variable arrival or flow; batch-and-queue | Bursty merges, end-of-sprint crunch, alternating idle/overload   | Throughput swings run-to-run; queues form then drain |
| **Muri** (overburden)     | A resource driven past sustainable load | CI runner, reviewer, or on-call held at >80–90% utilization        | Wait time explodes (§4); retries, burnout, corner-cutting |

**Muda (TIMWOODS):**

| Waste               | In Software                    | Red Flag                                      |
| ------------------- | ------------------------------ | --------------------------------------------- |
| **Transport**       | Unnecessary artifact movement  | Copying outputs between tools manually        |
| **Inventory**       | Unprocessed work in queues     | Stale PRs, long-lived branches, unread alerts |
| **Motion**          | Context switching              | Navigating multiple tools for one task        |
| **Waiting**         | Idle time between steps        | Sequential stages that could parallelize      |
| **Overproduction**  | More than consumed             | Unused logs, reports, generated files         |
| **Overprocessing**  | More steps than value requires | Review gates on auto-generated files          |
| **Defects**         | Errors requiring rework        | Bugs linting/tests could have caught earlier  |
| **Skills (unused)** | Underutilized capability       | Manual tasks that should be automated         |

Flag every step where **wait time > cycle time** — that is queued inventory (§4).

## 3. Constraint Identification (ToC — 5 Steps)

1. **Identify** the current constraint: the step or shared resource with the
   lowest effective throughput or largest queue.
2. **Exploit** — maximize its output without adding resources.
3. **Subordinate** — ensure upstream steps don't feed it faster than it can
   consume.
4. **Elevate** — if still a bottleneck, invest in capacity.
5. **Repeat** — re-measure after each change; the constraint may move.

Most constraints are **policy**, not physical capacity (Goldratt): a batching
rule, a mandatory approval, an unlimited-intake WIP policy, a "single reviewer"
convention. Check for a policy constraint before buying capacity — elevating a
policy costs nothing but agreement.

## 4. Flow Economics (Queueing)

Queues, not busy resources, set delivery time. Three laws make flow measurable
and turn "improve flow" into concrete moves.

- **Little's Law** — for any stable queue, `cycle time = WIP / throughput`. To
  ship faster *without* adding capacity, cut work-in-progress: halving in-flight
  work halves average cycle time at the same throughput. This is why WIP limits
  beat exhortations to "go faster."
- **Utilization curve (Kingman)** — queue time rises non-linearly with
  utilization ρ, roughly `wait ∝ ρ / (1 − ρ)`; past ~80% it explodes:

  | ρ (utilization) | 0.5 | 0.8 | 0.9 | 0.95 |
  | --------------- | --- | --- | --- | ---- |
  | wait ≈ (× service time) | 1× | 4× | 9× | 19× |

  A resource pinned at 95% is not "efficient" — it is a delay generator (this is
  Muri, §2). Size shared resources (CI runners, reviewers, on-call) for
  headroom, not full utilization.
- **Batch size** — large batches inflate cycle time, delay feedback, and raise
  risk per release. Halving batch size roughly halves queue time and localizes
  failure. Small PRs, trunk-based flow, and incremental deploys are batch-size
  controls, not stylistic preferences.

| Lever              | Effect                              | Move                                                  |
| ------------------ | ----------------------------------- | ----------------------------------------------------- |
| **Limit WIP**      | ↓ cycle time (Little)               | Cap in-flight PRs/tickets per person and per stage    |
| **Add headroom**   | ↓ queue explosion (Kingman)         | Keep hot resources below ~80% utilization             |
| **Shrink batches** | ↓ queue + risk + feedback delay     | Smaller PRs, more frequent merges and deploys         |
| **Damp variance**  | ↓ Mura-driven queues                | Level intake; decouple bursty producers               |

## 5. Measure the System

You cannot optimize what you cannot measure, and you cannot measure an
improvement you cannot separate from noise. "Go and see" the real signal — logs,
queues, traces, timings — rather than optimizing from assumption.

### Delivery & flow metrics

Track a small, stable set; a regression in any of them is a bug (§7).

| Metric                            | Question it answers                          | Source     |
| --------------------------------- | -------------------------------------------- | ---------- |
| **Deploy frequency**              | How often value reaches users                | DORA       |
| **Lead time for change**          | Commit → production latency                  | DORA       |
| **Change-fail rate**              | Share of deploys causing a failure           | DORA       |
| **Failed-deploy recovery**        | Time to restore service after a bad change   | DORA       |
| **Flow efficiency**               | value-add time ÷ total lead time (often <15%) | VSM        |
| **WIP / throughput / cycle time** | The Little's-Law triangle (§4)               | Lean / Flow |

**Flow efficiency** is the highest-yield diagnostic: map the value stream, split
each step into work time vs wait time, and the wait total is your inventory. Low
flow efficiency means the fix is *removing queues*, not speeding up steps.

**Error budget (spend or stabilize)** turns the reliability metrics into a
decision rule that resolves the tension between Directives 3 and 7. Set an
explicit failure tolerance (an availability or change-fail-rate target); the gap
between target and actual is the budget. While budget remains, *spend* it — ship
faster, take risk, raise deploy frequency (Directive 7). Once it is exhausted,
freeze feature risk and stabilize until it recovers (Directive 3). This makes the
speed-vs-reliability trade-off explicit rather than political. The pipeline gates
that measure and enforce these signals live in `ci-cd-reliability-architecture`;
the budget-spend policy is an optimization decision and lives here.

### Variation: common vs special cause (Six Sigma)

Before reacting to any metric move, classify the variation:

| Cause      | Signature                                      | Correct response                                         |
| ---------- | ---------------------------------------------- | -------------------------------------------------------- |
| **Common** | Inherent run-to-run noise within stable bounds | Do **not** tamper; change the system, not the instance   |
| **Special**| An assignable, out-of-bounds event             | Investigate the specific cause; remove or contain it     |

Reacting to common-cause noise as if it were signal (tampering / over-adjustment)
*adds* variance — the classic Deming funnel error. Establish a baseline band
first; treat only out-of-band moves as regressions. This is what "stabilize
before optimizing" (Core Directive 3) demands operationally, and it is why flaky
tests are measurement-blockers, not nuisances.

Run structured improvement as **DMAIC** — Define, Measure, Analyze, Improve,
Control — the Six Sigma loop that complements Kaizen/PDCA (§11): PDCA drives many
small reversible bets; DMAIC governs a defect or variance that needs a
controlled, evidence-gated fix locked in by a Control step so it cannot regress.

## 6. Diagnostic Reasoning Chain

For identifying constraints, waste, and root causes in operational analysis:

- **First Principles**: Strip legacy assumptions. Rebuild from observed facts,
  current requirements, and explicit constraints.
- **5 Whys**: Ladder from the observed symptom to a systemic root cause. Stop at
  the first cause you can change in the *system*, not the instance.
- **Analogical Reasoning**: Apply patterns from other domains to local problems.
- **Constraint Removal**: Imagine the ideal solution with no legacy debt before
  committing.
- **Inversion**: "How do I guarantee failure?" — then build guardrails against
  it.
- **Simple Functional Refactor Over Complex Technical Solution**: Prefer
  reasonable functional or UX changes (clear a cache, reorder steps, show a
  waiting state) before technical solutions (polling, retries, new
  abstractions). Technical complexity carries hidden costs — validate that
  simple alternatives don't solve it first.
- **Pre-mortem**: Assume the fix already failed; work backward to find the
  oversight.
- **Side Effect Audit**: When eliminating redundancy, trace all downstream paths
  that depended on the original behavior.
- **Pattern Parity**: Do not let divergent legacy patterns coexist indefinitely
  with a newly established standard. Temporary migration overlap needs an
  owner, scope, and removal condition.

## 7. CI/CD

- **Bottleneck first (ToC)**: Optimize the measured constraint before adjacent
  stages.
- **Parallelize safely**: Independent tests, builds, and linting can run
  concurrently when artifacts, caches, rate limits, and shared environments are
  isolated. Keep dependent or resource-contentious stages sequential. Speedup is
  capped by the serial fraction (Amdahl); past a point, coordination and
  contention cost make more parallelism *slower* (Universal Scalability Law).
  Measure before widening a fan-out.
- **Idempotent environments**: Deployment state must be reproducible from source
  control.
- **Shift-left gates**: Linting and unit tests run before integration tests.
- **Measure**: Track build duration, failure rate, and flakiness. Regressions
  are bugs.
- **Zero-downtime secret rotation**: Always create the new credential first,
  apply it to all environments, then delete the old one. Never delete before
  applying — the gap causes downtime and broken deployments.

## 8. Developer Workflow

- **Small PRs**: Faster merge, smaller blast radius, better review quality.
  Large PRs are inventory and oversized batches (§4).
- **Short feedback loops**: Fast local test results reduce context-switching
  cost.
- **Limit work-in-progress**: Cap in-flight work per person and per stage; a
  lower WIP ceiling shortens cycle time more reliably than working faster (§4).
- **Eliminate toil**: Recurring manual tasks should be removed, simplified, or
  automated only after the task is necessary, stable, and cheaper to automate
  than to perform manually. For where the work should ultimately live, see
  `push-out`.
- **One-piece flow**: Work moves design → build → review → deploy without
  sitting idle.

## 9. Testing

- **Detection distance**: Bugs caught closest to their source are usually
  cheapest. Use the earliest check that can actually detect the defect; some
  boundary and workflow failures require integration or e2e tests.
- **Flakiness is a defect**: A flaky test erodes trust and masks real failures;
  it is also a measurement-blocker (§5).
- **Confidence over coverage**: Optimize for critical-path confidence, not line
  percentages.
- **Shift-left security**: Static analysis, dependency audits, and secret
  scanning run in CI.

## 10. Documentation

- **Executable specs over text**: Tests and self-documenting code are living
  documentation.
- **JBGE**: Minimal, concise, audience-specific. Documents with no owner,
  current reader, legal/compliance need, or incident value should be archived or
  deleted after confirming they are not load-bearing.
- **ADRs**: Document _why_, not _what_. Prevents future rework from revisiting
  settled decisions.

## 11. Continuous Improvement (Kaizen / PDCA)

- Every optimization is a hypothesis — validate before declaring permanent.
- After resolving a bottleneck, explicitly identify the current constraint
  before the next cycle.
- When several improvements compete and none is the constraint, sequence by
  **cost of delay ÷ effort** (WSJF): the change whose delay is most expensive
  per unit of work goes first. The constraint (§3) still outranks all of them.
- Use the four axes (D, K, P, n) from `structural-simplification` to compare
  per-axis deltas before and after each improvement.

> **Litmus Test**: If a change worsens any complexity axis (D, K, P, n) from
> `structural-simplification` without measurably improving flow, reliability,
> cost, or another complexity axis, it is not an optimization.

## 12. Output Contract

When applying this skill, emit a coder-facing optimization decision record:

```
Scope:          <repo / pipeline / workflow / module / time window>
Constraint:     <measured bottleneck or Not measured + reason>
Decision:       Delete | Simplify | Stabilize | Optimize | Automate | Defer | Reject
Flow signal:    <WIP / cycle time / utilization / flow efficiency / variation class, or Not measured>
Evidence:       <metric, log, queue, test result, file path, or user workflow checked>
Next action:    <one concrete edit, experiment, measurement, or owner question>
Verification:   <before/after metric, command, CI run, or Not run + reason>
Residual risk:  <risk left for judgment, rollout, or future measurement>
```

## 13. See also

- **`structural-simplification`** — per-axis complexity comparison used for Kaizen Δ scoring.
- **`defect-shift-left`** — placement of each error detection at the earliest possible stage (operationalizes "Build Quality In").
- **`ci-cd-reliability-architecture`** — pipeline-reliability prerequisites that stabilize a process before optimization; owns the delivery gates this skill only measures.
- **`push-out`** — where recurring operational work should live once flow is stable.
