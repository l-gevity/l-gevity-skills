---
name: observability-design
description: >-
    Decides what a change must emit so a production failure is detected,
    diagnosed, and verified, and keeps the resulting signal set honest as it
    ages. Use when a risk survives verification into production, when choosing
    between a log, a metric, a trace, an event, or a probe, when defining a
    service level indicator or the threshold an alert fires on, when an
    incident showed the failure was invisible or the page was unactionable, or
    when auditing alerts, dashboards, and telemetry for noise, cost, and
    signals nobody consumes. Do not use to design a pre-production check, place
    a check in the pipeline, gate a release, or link outcome evidence to a
    requirement; hand those to test-strategy, defect-shift-left,
    ci-cd-reliability-architecture, and requirements-traceability.
---

# Observability Design

A failure nobody can observe has no severity, no frequency, and no owner. It is
not a small problem; it is an unknown one.

> **Purpose**: Every risk that survives into production has a signal that
> detects it, a signal that explains it, and an actor who acts on it.

> **Core Directives**
>
> 1. **Undetected is undefined.** Absence of alerts is not evidence of health.
>    Until a signal exists, the failure's rate is unmeasured, not zero.
> 2. **The signal ships with the change.** Instrumentation designed after the
>    incident pays the incident's price first, and is written by someone who
>    already knows the answer.
> 3. **Measure at the consumer's boundary.** Process health is not user
>    experience. A worker reporting healthy while its queue drains nowhere is
>    both, and only the consumer's view catches it.
> 4. **Every alert names an actor and a first action.** An alert with neither is
>    a notification, and notifications train people to ignore alerts.
> 5. **Detect on aggregates, diagnose on particulars.** An alert bound to a log
>    message string depends on a contract nobody agreed to keep.
> 6. **A signal with no consumer is cost.** Emission, storage, and retention are
>    paid continuously; attention is paid per alert. Delete what nothing reads.
> 7. **Alert sets only grow.** Without an explicit prune rule, every incident
>    adds signals and none removes them, until the set is uniformly ignored.

## Boundary

`observability-design` is a task-matched Alchemy companion, not a qualification
stage, gate, or acronym letter. It runs in a single pass, after the risks a
change carries are known and before the change is deployed.

This skill designs the *production* signal. It does not choose what to verify
before production, where checks run, or what a signal proves about a
requirement.

- `test-strategy` owns pre-production risk, oracles, and the evidence
  portfolio. Its residual risk — what the portfolio deliberately does not catch
  — is this skill's input. Do not re-derive failure modes here.
- `defect-shift-left` owns the ladder and the rule that later detection is never
  neutral. Production runtime and post-incident are its two most expensive
  ranks; this skill designs what is detectable there, and every signal it adds
  is a candidate for moving earlier next iteration.
- `ci-cd-reliability-architecture` owns deploy-time health probes, promotion,
  and rollback triggers. This skill decides what those probes read; CI/CD
  decides when they run and what they block.
- `requirements-traceability` owns linking outcome evidence to a requirement and
  judging its freshness. Telemetry for *did this achieve the outcome* is its
  concern; telemetry for *is this failing now* is this skill's.
- `push-out` owns moving the response work outward into automation and
  self-service. This skill owns the signal that triggers it.
- `system-optimization` detects missing metrics, silent failures, and unclear
  alerts as waste and hands the subject here; this skill returns the design.
- `zero-copy-requirements` owns where a fact lives. A dashboard assembled from
  signals is a generated report, never an authority.

Apply a project profile for tooling, naming conventions, retention policy,
severity ladders, and on-call routing. Keep none of those here.

## 1. Three Duties

Every signal serves exactly one of these. A signal serving none is waste; a
signal claiming all three usually serves none well.

| Duty | Question | Failing looks like |
| --- | --- | --- |
| **Detect** | Is something wrong right now? | The first report arrives from a user or a downstream team |
| **Diagnose** | Which part, and why? | Detection fires and the next step is reading source code |
| **Verify** | Did the change or the fix do what it claimed? | A deploy is called good because no new complaints arrived |

Detect must be cheap enough to run always. Diagnose may be expensive, sampled,
or enabled on demand, because it runs after detection has already fired.

## 2. Derive Signals From Residual Risk

Do not enumerate what could be measured. Start from the failure modes that
survive verification, and give each one a detection path.

For every residual risk carried into production, record:

- the **failure mode**, in the consumer's terms, not the process's;
- the **signal** that detects it, and the boundary it is measured at;
- the **threshold** and where the threshold's number comes from;
- the **actor** who receives it and their **first action**;
- the **expected time to detect**, against how long the failure is tolerable.

A residual risk with no detection path is not covered by an accepted risk
decision; it is unobserved. Record it as such rather than closing the row. When
expected time to detect exceeds the tolerable window, the signal does not meet
the risk, and either the threshold, the boundary, or the risk decision changes.

## 3. Choose the Signal Type

Choose by the question answered, then pay the cost that type charges.

| Type | Answers | Choose when | Cost driver |
| --- | --- | --- | --- |
| **Metric** | How many, how often, how slow | The question is aggregate and the answer is a number over time | Cardinality: every label value multiplies stored series |
| **Log** | What happened in this one case | The answer needs the specifics of a single occurrence | Volume and retention |
| **Trace** | Where the time or the failure went across boundaries | The path crosses processes, services, or queues | Sampling rate, and the discipline of propagating context |
| **Event** | A discrete, business-meaningful fact occurred | Something downstream must react to it or count it exactly | It is a published contract; changing its shape runs `evolutionary-database-design` |
| **Probe** | Is this answering correctly right now | Availability must be known independently of live traffic | Frequency, and the false-positive rate of the probe itself |

Detect on metrics and probes. Diagnose on traces and logs. An alert that fires
on the text of a log line couples paging to a string that any refactor may
reword without noticing.

## 4. Alert Admission Test

Run before adding any alert. All four must answer; a failure on any one means
the signal is a dashboard panel, not a page.

```text
1. Which named actor receives it?
2. What do they do in the first five minutes?
3. What degrades for a consumer if nobody acts?
4. Where does the threshold come from — an objective, a budget, or a
   contract — rather than a value that looked normal on the day?
```

An alert derived from an objective states the objective it defends. An alert
derived from a value someone eyeballed is a guess with a pager attached, and it
is the first to be ignored.

Alert on symptoms at the consumer boundary. Alert on a cause only when the
cause has its own distinct first action; otherwise it duplicates the symptom
alert and doubles the interruption for one failure.

## 5. The Prune Rule

Signal sets decay in one direction. A set nobody prunes ends as uniform noise,
and its most important alert is the one most reliably ignored.

| Decay | Detector | Action |
| --- | --- | --- |
| Alert fires repeatedly and nothing is done | Ratio of fires to actions taken | Delete it, or re-derive its threshold from the objective it should defend |
| Alert never fires | Time since last fire against its review interval | Prove it can fire, or delete it. An untested alert is not coverage. |
| Two alerts, one failure | Alerts that consistently fire together | Keep the one at the consumer boundary; demote the other to diagnosis |
| Dashboard nobody opens | Access over the review interval | Delete. A dashboard is a generated view, not a record. |
| Telemetry nothing queries | Queries against a series, log stream, or field | Stop emitting it. Retention is charged whether or not it is read. |
| Signal that earned its place after an incident | Its failure mode and the rank it is detected at | Ask whether it can move earlier; see `defect-shift-left` |

Every alert carries the date of its last useful fire and a review interval. An
alert past its interval is reviewed, never renewed by default.

## 6. Output Contract

```text
Subject:           <change, subsystem, or signal set under review>
Residual risk:     <failure mode in consumer terms, from test-strategy>
Duty:              Detect | Diagnose | Verify
Signal:            metric | log | trace | event | probe
Measured at:       <boundary, and why it is the consumer's view>
Threshold:         <value and the objective, budget, or contract it comes from>
Actor:             <who receives it>
First action:      <what they do in the first five minutes>
Time to detect:    <expected> vs <tolerable>
Decision:          ADD | KEEP | RETARGET | DEMOTE | DELETE | UNOBSERVED
Review interval:   <when this signal is re-examined>
Next action:       <one concrete action>
```

`UNOBSERVED` is a reportable outcome. A risk with no affordable signal is
recorded as undetectable, with the consequence stated, not quietly dropped.

## 7. See Also

- **`test-strategy`** - the risks and oracles that decide what remains residual.
- **`defect-shift-left`** - the cost ladder, and moving a production signal earlier.
- **`ci-cd-reliability-architecture`** - health probes, promotion, and rollback triggers.
- **`requirements-traceability`** - outcome measurement linked to a requirement.
- **`push-out`** - moving the response to a signal out of human memory.
- **`system-optimization`** - the waste scan that surfaces missing or unclear signals.
