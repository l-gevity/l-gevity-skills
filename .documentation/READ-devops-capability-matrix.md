# DevOps Capability Matrix

A three-axis DevOps assessment SKILL for mapping delivery capability by
pipeline phase, stack component, and maturity level.

## Why use this

- It replaces vague "DevOps maturity" claims with evidence-backed cells.
- It shows where maturity is uneven across Plan, Build, Test, Deploy, Monitor,
  and Operate.
- It prevents chasing Level 5 everywhere by setting targets from risk and
  value.
- It turns assessment into a one-step roadmap instead of a generic improvement
  wishlist.

## The model

| Axis | Meaning |
| ---- | ------- |
| **X** | CI/CD pipeline phase: Plan, Build, Test, Deploy, Monitor, Operate |
| **Y** | Stack component: infrastructure, databases, app framework, APIs, security, observability, data/ML, developer tooling |
| **Z** | Maturity level from 1 manual/ad hoc to 5 optimized/continuous improvement |

## Maturity levels

| Level | Name | Short test |
| ----- | ---- | ---------- |
| **1** | Manual / ad hoc | Does this rely on individual memory or manual work? |
| **2** | Repeatable / documented | Can another person repeat it from documented steps? |
| **3** | Defined / standardized | Is there a shared standard used across the relevant scope? |
| **4** | Measured / quantified | Are metrics collected and reviewed? |
| **5** | Optimized / continuous improvement | Do measured feedback loops regularly improve the capability? |

## How to use

1. Define the assessment scope: product, repo, platform, teams, environments,
   and time window.
2. Choose relevant X/Y cells. Exclude cells with no owner, risk, or recurring
   work.
3. Gather evidence from workflows, IaC, dashboards, incident records, runbooks,
   test reports, deployment logs, and team practices.
4. Score current maturity, target maturity, confidence, and gap for each cell.
5. Prioritize by gap, risk, frequency, and dependency count.
6. Roadmap only the next maturity step for each priority cell.

Example prompt:

> "Assess DevOps maturity for this repo using `devops-capability-matrix`.
> Focus on Build, Test, Deploy, Monitor across infrastructure, app framework,
> databases, and observability. Give current level, target level, evidence,
> and next action."

## When to combine it

- Use `ci-cd-reliability-architecture` for deploy-path reliability findings.
- Use `defect-shift-left` when a matrix gap is really a missing earlier gate.
- Use `system-optimization` when many gaps exist and the constraint is unclear.
- Use `continuous-improvement` when a recurring gap should become a skill,
  template, check, or build-time rule.

## Next steps

- See [SKILL.md](../.claude/skills/devops-capability-matrix/SKILL.md) for the
  full rubric, assessment protocol, anti-patterns, and output contract.
