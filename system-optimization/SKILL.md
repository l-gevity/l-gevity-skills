---
name: system-optimization
description:
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

1. **Identify** the single step with lowest throughput.
2. **Exploit** — maximize its output without adding resources.
3. **Subordinate** — ensure upstream steps don't feed it faster than it can
   consume.
4. **Elevate** — if still a bottleneck, invest in capacity.
5. **Repeat** — a new constraint always emerges.

## 4. Diagnostic Reasoning Chain

For identifying constraints, waste, and root causes in operational analysis:

- **First Principles**: Strip legacy assumptions. Rebuild from objective truth.
- **Analogical Reasoning**: Apply patterns from other domains to local problems.
- **Constraint Removal**: Imagine the ideal solution with no legacy debt before
  committing.
- **Inversion**: "How do I guarantee failure?" — then build guardrails against
  it.
- **Pre-mortem**: Assume the fix already failed; work backward to find the
  oversight.
- **Side Effect Audit**: When eliminating redundancy, trace all downstream paths
  that depended on the original behavior.
- **Pattern Parity**: Never let divergent legacy patterns coexist with a newly
  established standard — all sibling instances are defects.

## 5. CI/CD

- **Bottleneck first (ToC)**: Optimize the slowest stage before anything else.
- **Parallelize aggressively**: Tests, builds, and linting run concurrently,
  never sequentially.
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
- **Eliminate toil**: Any recurring manual task that can be automated must be
  automated.
- **One-piece flow**: Work moves design → build → review → deploy without
  sitting idle.

## 7. Structural Simplicity

> For structural analysis use `structural-simplification`.

## 8. Testing

- **Detection distance**: Bugs caught closest to their source are cheapest.
  Unit > integration > e2e.
- **Flakiness is a defect**: A flaky test erodes trust and masks real failures.
- **Confidence over coverage**: Optimize for critical-path confidence, not line
  percentages.
- **Shift-left security**: Static analysis, dependency audits, and secret
  scanning run in CI.

## 9. Documentation

- **Executable specs over text**: Tests and self-documenting code are living
  documentation.
- **JBGE**: Minimal, concise, audience-specific. A document not read in months
  should be deleted.
- **ADRs**: Document _why_, not _what_. Prevents future rework from revisiting
  settled decisions.

## 10. Continuous Improvement (Kaizen / PDCA)

- Every optimization is a hypothesis — validate before declaring permanent.
- After resolving a bottleneck, explicitly identify the new constraint before
  the next cycle.
- Use the four axes (D, K, P, n) from `structural-simplification` to compare
  per-axis deltas before and after each improvement.

> **Litmus Test**: Before adding any pipeline stage, automation, or process step
> — ask: _"Does this unequivocally increase velocity or quality of value
> delivered to the end user?"_ If not measurable, drop it. If the change worsens
> any complexity axis (D, K, P, n) without improving another, it is not an
> optimization.
