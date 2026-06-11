---
name: push-out
description: >-
    Moves recurring DevOps and operational work out of individual memory,
    manual execution, ticket queues, and team-local practice into documented
    procedures, repo standards, shared platforms, self-service controls, and
    adaptive feedback loops. Use when reducing toil, designing an improvement
    roadmap, deciding what to standardize or automate, assessing where
    operational work currently lives, or asking how to move work from humans
    into durable systems.
---

# Push-Out

> **Purpose**: Move recurring operational burden outward from fragile human
> execution into durable system capability.

> **Improvement Trio**
>
> - `defect-shift-left`: move defect detection earlier.
> - `push-out`: move recurring operational work outward.
> - `bring-down`: move bespoke code down into reusable capability.

> **Core Directives**
>
> 1. **Push work, not responsibility.** The owner remains accountable; the
>    execution path moves into a more durable layer.
> 2. **Evidence before rank.** Assign no push-out rank without observed proof.
> 3. **Delete before pushing.** Remove unnecessary work before documenting,
>    standardizing, automating, or platforming it.
> 4. **Standardize before automating.** Automation over ad hoc practice
>    industrializes confusion.
> 5. **Self-service needs guardrails.** A platform without policy, validation,
>    observability, and rollback exports toil to users.
> 6. **Feedback closes the loop.** Dashboards and metrics are not improvement
>    until they trigger action.

---

## 1. Push-Out Ladder

The ladder names where recurring operational work currently lives.

| Rank | Location | Work lives in | Evidence |
| ---- | -------- | ------------- | -------- |
| **0** | Individual memory | Heroics, tribal knowledge, manual clicks | "Ask Alice", no runbook, no repeatable input/output |
| **1** | Team procedure | Runbook, checklist, documented handoff | Another team member can repeat it manually |
| **2** | Repo standard | Template, script, CI job, policy, config convention | The repo enforces or strongly guides the path |
| **3** | Shared platform | Golden path, reusable workflow, managed internal primitive | Multiple repos/teams consume the same capability |
| **4** | Self-service control | Guardrailed workflow developers can run without ops handoff | Users trigger it safely; policy, validation, audit, and rollback exist |
| **5** | Adaptive system | Metrics and feedback change the system | Thresholds, reviews, or automation drive continuous improvement |

```
push-out distance = target rank - current rank
```

Higher is not always better. Choose the target by frequency, risk, toil cost,
blast radius, and number of dependent teams.

---

## 2. Target-Rank Heuristics

| Condition | Minimum target |
| --------- | -------------- |
| Rare, low-risk internal task | Rank 1 |
| Repeated task inside one repo/team | Rank 2 |
| Repeated task across repos/teams | Rank 3 |
| Frequent developer-facing request or ticket queue | Rank 4 |
| High-volume, high-risk, regulated, or incident-prone path | Rank 5 |

Do not push work to Rank 4 or 5 unless the lower-rank foundations exist or are
created in the same change.

---

## 3. Push-Out Protocol

1. **Define scope.** Name the product, repo, platform, teams, environments, and
   time window.
2. **Inventory recurring work.** Find manual steps, tickets, approvals,
   incident repeats, deploy chores, dashboard checks, and hand-maintained
   config.
3. **Question necessity.** Delete work that no longer serves a real purpose.
4. **Locate current rank.** Assign rank 0-5 with evidence.
5. **Choose target rank.** Justify by frequency, risk, blast radius,
   compliance, toil cost, and dependency count.
6. **Compute distance.** Target rank - current rank.
7. **Choose the next move.** Emit one action that advances exactly one rank.
8. **Gate and retire.** Prove the new path works, then remove same-scope manual
   duplicates.

Prioritize by:

```
priority = push-out distance x frequency x blast radius x toil cost
```

If many candidates compete, apply `system-optimization` to find the constraint
before improving adjacent work.

---

## 4. Move Patterns

| Move | Use when | Action |
| ---- | -------- | ------ |
| **0 to 1** | Knowledge is tribal | Write owner, inputs, outputs, runbook, rollback |
| **1 to 2** | A runbook repeats | Convert to script, template, CI job, config schema, or policy |
| **2 to 3** | Many repos copy the same practice | Extract shared workflow, platform primitive, or golden path |
| **3 to 4** | Platform team is still a ticket queue | Add self-service UI/API/CLI with validation, permissions, audit, and rollback |
| **4 to 5** | Self-service exists but does not improve | Add SLOs, trend review, alert thresholds, incident learning, and removal loop |

When the move concerns deployment safety, apply `ci-cd-reliability-architecture`.
When the move concerns check placement, apply `defect-shift-left`. When the
move concerns duplicated custom implementation, apply `bring-down`.

---

## 5. Anti-Patterns

| Anti-pattern | Correction |
| ------------ | ---------- |
| Automating an undocumented process | Document and standardize first |
| Platform team as ticket queue | Push to guardrailed self-service |
| Self-service without policy or rollback | Add validation, permissions, audit, rollback, and observability |
| Dashboard called improvement | Define threshold, review cadence, and action |
| Tool adoption treated as maturity | Score the operational outcome, not the product installed |
| Golden path with no adoption signal | Measure usage, escape hatches, and support load |
| Manual approval called governance | Replace with policy-as-code where technically possible |
| Keeping manual duplicate forever | Retire same-scope duplicate after proof |

---

## 6. Output Contract

Emit results in this shape:

```
Scope:          <product/repo/platform/team/environment/time window>
Mode:           Assessment | Improvement | Roadmap
Decision:       Keep manual | Document | Standardize | Automate | Platformize | Reject
Summary:        <2-4 sentences: main toil source, best next push, key risk>
Verification:   <metrics, logs, workflow search, runbook check, or Not run + reason>

Work map:
| Work item | Current rank | Target rank | Distance | Evidence | Decision | Confidence | Next action |
| --------- | ------------ | ----------- | -------- | -------- | -------- | ---------- | ----------- |

Priorities:
| Rank | Work item | Why now | Push-out move | Validation | Duplicate to retire |
| ---- | --------- | ------- | ------------- | ---------- | ------------------- |

Gaps:
<Missing evidence, unknown ownership, absent metrics, excluded work, or risks>
```

---

## 7. See Also

- **`defect-shift-left`** - move defect detection earlier.
- **`bring-down`** - move bespoke code down into reusable capability.
- **`system-optimization`** - bottleneck and waste analysis before improvement.
- **`ci-cd-reliability-architecture`** - pipeline safety and deployment reliability patterns.
- **`continuous-improvement`** - promotion of recurring findings into skills, checks, or templates.
