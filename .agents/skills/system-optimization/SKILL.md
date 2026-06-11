---
name: system-optimization
description: >-
    Applies Lean, Kaizen, Six Sigma, Theory of Constraints, and DevOps
    principles to eliminate waste and improve flow across all aspects of a
    software project. Use when scanning for optimizations in CI/CD pipelines,
    developer workflows, code structure, testing strategy, documentation, or the
    overall value stream. Activate when a review is requested to identify waste,
    bottlenecks, and improvement opportunities across the project.
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

---

## Order of Operations

Apply these steps **in order**. The most expensive mistake is optimizing or
automating something that should have been deleted — work done out of order is
work to undo later.

1. **Question the requirement.** The requirement is the most upstream waste.
   Strip it to first principles before touching the implementation; the cheapest
   step is the one that no longer needs to exist.
2. **Probe deletion.** Try removing the step, file, stage, or component behind
   a reversible branch, feature flag, dry run, or narrow rollout. Restore
   anything proven load-bearing; keep only deletions backed by evidence.
3. **Simplify what remains.** Only optimize parts that survived deletion.
4. **Speed it up.** Parallelize, cache, batch — but only after simplification.
5. **Automate last.** Automating an unnecessary or unsimplified process locks in
   the waste.

## 1. Scan Layers

| Layer                      | Red flags                                                           |
| -------------------------- | ------------------------------------------------------------------- |
| **CI/CD & Automation**     | Sequential stages that could parallelize, manual steps, flaky gates |
| **Developer Workflow**     | Large PRs, long-lived branches, slow feedback loops                 |
| **Code Structure**         | Dead code, duplication, divergent patterns                          |
| **Testing Strategy**       | Coverage gaps, flaky tests, defects caught late                     |
| **Tooling & Dependencies** | Unused packages, outdated tooling, manual steps                     |
| **Documentation**          | Stale docs, missing ADRs, over-documentation                        |
| **Observability**          | Missing metrics, silent failures, unclear alerts                    |

## 2. Waste Scan (Lean — TIMWOODS)

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

Flag every step where **wait time > cycle time** — that is queued inventory.

## 3. Constraint Identification (ToC — 5 Steps)

1. **Identify** the current constraint: the step or shared resource with the
   lowest effective throughput or largest queue.
2. **Exploit** — maximize its output without adding resources.
3. **Subordinate** — ensure upstream steps don't feed it faster than it can
   consume.
4. **Elevate** — if still a bottleneck, invest in capacity.
5. **Repeat** — re-measure after each change; the constraint may move.

## 4. Diagnostic Reasoning Chain

For identifying constraints, waste, and root causes in operational analysis:

- **First Principles**: Strip legacy assumptions. Rebuild from observed facts,
  current requirements, and explicit constraints.
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

## 5. CI/CD

- **Bottleneck first (ToC)**: Optimize the measured constraint before adjacent
  stages.
- **Parallelize safely**: Independent tests, builds, and linting can run
  concurrently when artifacts, caches, rate limits, and shared environments are
  isolated. Keep dependent or resource-contentious stages sequential.
- **Idempotent environments**: Deployment state must be reproducible from source
  control.
- **Shift-left gates**: Linting and unit tests run before integration tests.
- **Measure**: Track build duration, failure rate, and flakiness. Regressions
  are bugs.
- **Zero-downtime secret rotation**: Always create the new credential first,
  apply it to all environments, then delete the old one. Never delete before
  applying — the gap causes downtime and broken deployments.

## 6. Developer Workflow

- **Small PRs**: Faster merge, smaller blast radius, better review quality.
  Large PRs are inventory.
- **Short feedback loops**: Fast local test results reduce context-switching
  cost.
- **Eliminate toil**: Recurring manual tasks should be removed, simplified, or
  automated only after the task is necessary, stable, and cheaper to automate
  than to perform manually.
- **One-piece flow**: Work moves design → build → review → deploy without
  sitting idle.

## 7. Testing

- **Detection distance**: Bugs caught closest to their source are usually
  cheapest. Use the earliest check that can actually detect the defect; some
  boundary and workflow failures require integration or e2e tests.
- **Flakiness is a defect**: A flaky test erodes trust and masks real failures.
- **Confidence over coverage**: Optimize for critical-path confidence, not line
  percentages.
- **Shift-left security**: Static analysis, dependency audits, and secret
  scanning run in CI.

## 8. Documentation

- **Executable specs over text**: Tests and self-documenting code are living
  documentation.
- **JBGE**: Minimal, concise, audience-specific. Documents with no owner,
  current reader, legal/compliance need, or incident value should be archived or
  deleted after confirming they are not load-bearing.
- **ADRs**: Document _why_, not _what_. Prevents future rework from revisiting
  settled decisions.

## 9. Continuous Improvement (Kaizen / PDCA)

- Every optimization is a hypothesis — validate before declaring permanent.
- After resolving a bottleneck, explicitly identify the current constraint
  before the next cycle.
- Use the four axes (D, K, P, n) from `structural-simplification` to compare
  per-axis deltas before and after each improvement.

> **Litmus Test**: If a change worsens any complexity axis (D, K, P, n) from
> `structural-simplification` without measurably improving flow, reliability,
> cost, or another complexity axis, it is not an optimization.

## 10. Output Contract

When applying this skill, emit a coder-facing optimization decision record:

```
Scope:          <repo / pipeline / workflow / module / time window>
Constraint:     <measured bottleneck or Not measured + reason>
Decision:       Delete | Simplify | Stabilize | Optimize | Automate | Defer | Reject
Evidence:       <metric, log, queue, test result, file path, or user workflow checked>
Next action:    <one concrete edit, experiment, measurement, or owner question>
Verification:   <before/after metric, command, CI run, or Not run + reason>
Residual risk:  <risk left for judgment, rollout, or future measurement>
```

## 11. See also

- **`structural-simplification`** — per-axis complexity comparison used for Kaizen Δ scoring.
- **`defect-shift-left`** — placement of each error detection at the earliest possible stage (operationalizes "Build Quality In").
- **`ci-cd-reliability-architecture`** — pipeline-reliability prerequisites that stabilize a process before optimization.
