---
name: devops-capability-matrix
description: >-
    A three-axis DevOps assessment and roadmap framework: CI/CD pipeline phase
    (X), technology stack component (Y), and maturity level (Z). Use when
    assessing DevOps capability, creating a maturity matrix, comparing current
    vs target operating state, prioritizing CI/CD improvements, or converting
    vague "DevOps maturity" claims into evidence-backed capability cells.
---

# DevOps Capability Matrix

> **Purpose**: Convert DevOps maturity from a single vague score into a
> cell-by-cell capability map: pipeline phase x stack component x maturity
> level. Use the matrix to audit current state, set targets, and choose the
> next improvement step.

> **Core Directives**
>
> 1. **Score capabilities, not organizations.** Maturity belongs to a specific
>    phase/component cell, not to the whole team.
> 2. **Evidence before level.** Assign no maturity level without naming the
>    observed proof.
> 3. **Target by risk and value.** Not every cell needs Level 5. Critical,
>    high-change, high-blast-radius cells need higher targets.
> 4. **Advance one level at a time.** A roadmap item must move a cell to the
>    next maturity level, not leap over missing foundations.
> 5. **Automate after standardizing.** Level 4/5 optimization built on ad hoc
>    Level 1/2 practice is theatre.

---

## 1. Axes

| Axis | Name | Typical values | Question |
| ---- | ---- | -------------- | -------- |
| **X** | Pipeline phase | Plan, Build, Test, Deploy, Monitor, Operate | Where in the delivery lifecycle is the capability used? |
| **Y** | Stack component | Infrastructure, Databases, Application framework, APIs, Security, Observability, Data/ML, Developer tooling | Which technical surface does the capability govern? |
| **Z** | Maturity level | 1-5 | How repeatable, standardized, measured, and optimized is the capability? |

Extend X/Y only when the local system needs it. Do not invent phases or stack
components that have no owner, tool, risk, or recurring work in the target
organization.

---

## 2. Maturity Levels

| Level | Name | Evidence required | Typical next step |
| ----- | ---- | ----------------- | ----------------- |
| **1** | Manual / ad hoc | Work depends on individual memory, manual clicks, or one-off scripts | Document the process and define owner/input/output |
| **2** | Repeatable / documented | Procedure exists and can be repeated, but is weakly enforced | Standardize the workflow, template, or policy |
| **3** | Defined / standardized | Shared standard exists and is used across relevant teams/repos | Add measurement and blocking gates |
| **4** | Measured / quantified | Metrics, SLOs, failure rates, cycle times, or compliance signals are tracked | Use data to tune, reduce variance, and prioritize |
| **5** | Optimized / continuous improvement | Feedback loops regularly improve the capability; regressions trigger action | Keep improving via PDCA/Kaizen and retire obsolete steps |

### Level Boundaries

| Boundary | Required promotion evidence |
| -------- | --------------------------- |
| **1 to 2** | Written runbook, checklist, or script; named owner |
| **2 to 3** | Standard template/policy adopted by the relevant scope |
| **3 to 4** | Metrics collected automatically and reviewed |
| **4 to 5** | Measured feedback changes the system; improvement cadence exists |

If evidence is mixed, score the lower level and record the missing promotion
evidence.

---

## 3. Assessment Protocol

1. **Define scope.** Name the product, repo, platform, teams, environments, and
   time window under assessment.
2. **Choose X/Y cells.** Include only phases and stack components that are
   relevant to the scope.
3. **Gather evidence.** Inspect workflows, repos, IaC, dashboards, incident
   records, runbooks, deployment logs, test reports, and team practices.
4. **Score each cell.** Assign Z=1-5 with one evidence note and one confidence
   level.
5. **Set target level.** Choose the target by risk, change frequency,
   compliance need, operational load, and customer blast radius.
6. **Compute gap.** Gap = target level - current level.
7. **Prioritize.** Rank by gap x risk x frequency x dependency count.
8. **Roadmap the next step.** Emit the smallest action that moves each priority
   cell up exactly one level.

Do not average cell scores into a single maturity number unless the user
explicitly asks for executive reporting. If an aggregate is requested, label it
as a summary statistic and keep the cell-level findings as the source of truth.

---

## 4. Target-Level Heuristics

| Condition | Minimum target |
| --------- | -------------- |
| Low-risk internal tool, rare changes | Level 2 |
| Shared repo, regular changes, moderate blast radius | Level 3 |
| Production deploy path, customer-visible service, regulated data, or shared infrastructure | Level 4 |
| Safety-critical, high-traffic, multi-tenant, compliance-critical, or repeated incident area | Level 5 |

Target levels are not prestige goals. A Level 3 capability can be correct when
the cost of measurement and optimization exceeds the risk.

---

## 5. Roadmap Rules

For each priority cell, produce one next-level action:

| Current | Roadmap action pattern |
| ------- | ---------------------- |
| **1** | Create owner, runbook, checklist, or repeatable script |
| **2** | Convert local practice into a standard template/policy used by the scope |
| **3** | Add automated measurement, gate, SLO, dashboard, or audit trail |
| **4** | Add feedback loop: trend review, alert threshold, variance reduction, post-incident improvement |
| **5** | Preserve cadence; remove obsolete checks and reduce waste |

When the cell concerns CI/CD reliability, apply `ci-cd-reliability-architecture`.
When it concerns earliest defect detection, apply `defect-shift-left`. When
prioritizing across many improvement candidates, apply `system-optimization`.

---

## 6. Anti-Patterns

| Anti-pattern | Correction |
| ------------ | ---------- |
| One global "DevOps maturity" score | Score per X/Y cell |
| Level assigned from aspiration | Require observed evidence |
| Chasing Level 5 everywhere | Set targets by risk/value |
| Automating an undocumented process | Move 1 to 2 to 3 before optimizing |
| Metrics nobody reviews | Level 3, not Level 4/5 |
| Dashboard without action threshold | Measurement theatre |
| Manual approval called governance | Map the control to evidence, owner, and earliest enforceable gate |
| Tool adoption treated as maturity | Score the capability outcome, not the product installed |

---

## 7. Output Contract

Emit assessment results in this shape:

```
Scope:          <product/repo/platform/team/environment/time window>
Axes:           X=<phases included>; Y=<stack components included>; Z=1-5 maturity
Summary:        <2-4 sentences: strongest cells, weakest cells, main constraint>

Matrix:
| Phase | Component | Current Z | Target Z | Gap | Evidence | Confidence | Next action |
| ----- | --------- | --------- | -------- | --- | -------- | ---------- | ----------- |

Priorities:
| Rank | Cell | Why now | Next-level action | Owner signal | Validation |
| ---- | ---- | ------- | ----------------- | ------------ | ---------- |

Gaps:
<Missing evidence, unknown ownership, absent metrics, or cells intentionally excluded>
```

For roadmap-only requests, omit low-priority cells but keep `Scope`, `Axes`,
and `Gaps` so the recommendation does not detach from the assessment basis.

---

## 8. See Also

- **`ci-cd-reliability-architecture`** - pipeline safety and deployment reliability patterns.
- **`defect-shift-left`** - earliest-stage placement for checks and gates.
- **`system-optimization`** - bottleneck and waste analysis after the matrix exposes gaps.
- **`continuous-improvement`** - promotion of recurring findings into skills, checks, or templates.
