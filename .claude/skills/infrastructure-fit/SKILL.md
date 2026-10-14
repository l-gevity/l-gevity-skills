---
name: infrastructure-fit
description: >-
    Chooses a system's infrastructure foundation from a requirements-derived
    fit profile, and re-checks at any later point whether the foundation in
    use still fits. Use when choosing or inheriting a datastore, identity
    provider, compute or hosting model, region, or tenancy model; when a
    template or starter ships infrastructure defaults; when a requirement,
    scale estimate, or compliance obligation changes; when workarounds against
    a platform accumulate; before the first real data enters an environment;
    or for a periodic fit review. Do not use for build-or-buy of one
    capability, vendor advisories or end-of-life dates, migration staging, or
    pipeline design; hand those to bring-down, dependency-lifecycle,
    evolutionary-database-design, and ci-cd-reliability-architecture.
---

# Infrastructure Fit

The foundation a system runs on is chosen once and paid for on every feature
after it.

> **Purpose**: Every hard-to-reverse infrastructure choice traces to a
> requirement, carries a tripwire someone evaluates, and is checked again when
> the requirements move.

> **Core Directives**
>
> 1. **Profile before platform.** Choose no foundation before the domain
>    sketch and the fit profile exist. A template default is a decision nobody
>    made.
> 2. **Rigor follows reversibility.** A one-way door gets a record with its
>    forcing requirement, tripwires, and reversal cost. A two-way door takes
>    the default and no record.
> 3. **Boring, portable, few.** Start from the fewest components that meet the
>    profile. A platform-specific feature names the requirement that forces it,
>    or it goes.
> 4. **Skeleton before features.** Run every hard non-functional path end to
>    end on the chosen foundation before the first feature lands.
> 5. **A tripwire nobody evaluates is a comment.** It names a signal, a
>    threshold, an owner, and the place it is checked.
> 6. **Forward costs only.** Sunk investment is never an argument for keeping a
>    foundation, and reversal cost rises with every row of real data.

## Boundary

`infrastructure-fit` is a task-matched Alchemy companion, not a qualification
stage, gate, or acronym letter. Select mode runs when a foundation is first
chosen, inherited, or extended: after readiness has fixed what the increment
must do, before Architecture places subsystems on it. Review mode runs in a
single pass whenever a §6 trigger fires.

This skill decides *which foundation fits the requirements, and whether it
still does*.

- `requirements-grounding` owns the quality-characteristic sweep that fills the
  profile. A blank dimension goes back there.
- `bring-down` owns whether one capability is bespoke or external, and the
  survey that selects a service. When its answer becomes a one-way door, this
  skill's profile and record apply before adoption.
- `dependency-lifecycle` owns vendor-side triggers on a platform already owned:
  advisories, pricing or license changes, end-of-life dates. Return here only
  when that event changes fit.
- `architecture-guidelines` and `morphogenetic-architecture` own where
  subsystems sit on the foundation, and whether a control may rely on the
  platform beneath it.
- `structural-simplification` measures what adding or removing a component
  does to diversity and count.
- `evolutionary-database-design` stages a store migration once `MIGRATE` is
  decided.
- `test-strategy` owns when a fake may stand in for the real foundation.
- `zero-copy-requirements` names the artifact that holds the decision record.
- `ci-cd-reliability-architecture` owns deploy, rollback, and promotion.

Apply a project profile for provider names, environments, infrastructure-as-code
paths, and cost envelopes. Keep none of those here.

## 1. Modes

| Mode | Enter when | Returns |
| --- | --- | --- |
| **Select** | New project; template or starter adopted; a new foundation component proposed | One record per one-way door, plus skeleton results |
| **Review** | A §6 trigger fires; periodic review; before the first real data | One record per component, plus the profile diff |

Review rebuilds the profile from current sources. The snapshot in an old record
is what is being checked, never the input.

## 2. Fit Profile

Build the profile from requirements, decisions, and measurements, never from
the infrastructure already in place.

| Dimension | Capture | Decides |
| --- | --- | --- |
| **Domain shape** | 5–10 core entities, their relations, and invariants that span entities: uniqueness, referential integrity, multi-entity transactions | Data model paradigm |
| **Access patterns** | The 3–5 hardest queries and reports, including aggregate, cross-tenant, and ad-hoc reporting | Store, indexing, read model |
| **Scale** | Expected tenants, users, data volume, and request rate, plus a stated ceiling | Single node or distributed |
| **Isolation and residency** | Tenancy model, isolation proof, data region, subprocessors | Region, tenancy, provider |
| **Data lifecycle** | Retention, erasure, legal hold, backup, restore point and time objectives | Store features, backup model |
| **Identity** | Who signs in, federation, administrative roles, account lifecycle | Identity provider, user store |
| **Workload shape** | Request/response, long jobs, batch imports, schedules, events | Compute model, async |
| **Operability** | Team size, on-call capacity, skills, local and pipeline parity | Managed or self-run, component count |
| **Cost** | Envelope at expected scale and at zero load | Pricing model |
| **Lock-in tolerance** | What it costs the product to be unable to leave a vendor | Portable or proprietary |

A blank dimension is a coverage gap. Every choice that depends on it is
`PROVISIONAL` until the gap closes.

## 3. Doors and Defaults

| Door | Typical choices | Rigor |
| --- | --- | --- |
| **One-way** | Data model paradigm and store; identity provider and user store; compute and hosting model; cloud and region; tenancy model; persisted event backbone | Full record (§4) |
| **Two-way** | Pipeline provider, lint and format tooling, UI framework, logging library, add-ons behind a standard protocol | Take the default; no record |

Start from the default. Deviate only when the profile shows the named reason.

| Concern | Default | Deviate only when the profile shows |
| --- | --- | --- |
| Store | One relational database | Scale beyond one node, data schemaless by nature, multi-region writes, or a specialized access shape: graph, time series, search, blobs |
| Compute | One deployable application | Idle-heavy load where scale-to-zero pays and cold starts are acceptable, or a measured need to scale parts independently |
| Identity | A standards-based identity provider; the application owns authorization | Federation, partner, or customer-identity needs the default cannot meet |
| Async | None; then a job table in the existing store | Throughput or fan-out that table measurably cannot carry |
| Region | One region that satisfies residency | Latency or availability that one region cannot meet |

## 4. Select Protocol

1. **Strip inherited defaults.** List every foundation choice the template,
   starter, or previous project ships. Each is `INHERITED` until steps 2–4
   pass it. A template carries tooling, never product decisions.
2. **Build the profile** (§2) and classify each choice by door (§3).
3. **Compare candidates** on the three hardest access patterns and the §5
   skeleton paths. When ratings are close or unknown, spike each candidate for
   at most a day.
4. **Record the decision** where `zero-copy-requirements` puts decisions:
   forcing requirement, the profile snapshot relied on, rejected alternatives,
   tripwires (§6), owner, review date, and reversal cost.
5. **Put the one-way door behind an owned port**, so domain code never imports
   the vendor SDK. A port lowers migration cost; it does not make a wrong
   paradigm right. A fake behind the port accepts any query shape and hides a
   paradigm mismatch, so the port's contract tests also run against the real
   foundation.

## 5. Walking Skeleton

Before the first feature, run each path end to end on the chosen foundation, in
an environment shaped like production:

- [ ] The full stack runs locally, or through a documented substitute, and in the pipeline.
- [ ] Sign-in end to end, including one authorization check.
- [ ] Deploy and rollback.
- [ ] Backup and a restore drill.
- [ ] Erasure of one data subject across every store and the identity provider.
- [ ] A tenant isolation probe: a cross-tenant read is refused.
- [ ] The hardest query or report from the profile.

A path that cannot be made to run is a fit finding, not a backlog item.

## 6. Tripwires and Review Triggers

A tripwire names a signal, a threshold, an owner, and where it is evaluated: a
pipeline check, a release gate, or the periodic review. "Deferred until X"
without those four is a comment.

| Signal in code, history, or operations | Indicates |
| --- | --- |
| Hand-written uniqueness or referential checks, conflict retries, manual joins, denormalized copies kept in sync, readers for old document shapes | A relational domain on a non-relational store |
| Platform behavior learned from an incident or a probe: hidden middleware, silent no-ops, local runtime limits | Platform glue costs more than it saves |
| Manual per-environment steps, settings lost on reprovision, one registration per environment per service | Too many components, or incomplete infrastructure-as-code |
| The stack cannot run locally; fakes pass where production fails | A parity gap |
| Cost per tenant or idle cost outside the envelope | Wrong sizing or pricing model |
| A large share of commits or issues spent on one component instead of features | Platform tax; count it, never estimate it |

Review when:

- a requirement, scale estimate, or compliance obligation moves a profile dimension;
- a tripwire fires;
- the first real data is about to enter an environment, because reversal is cheapest before it;
- a period passes: at least quarterly, or before each major release;
- `dependency-lifecycle` finds that a vendor event changes fit.

## 7. Review Protocol

1. **Inventory from the source of truth.** Read the infrastructure-as-code and
   runtime configuration, not documents about them. A component without a
   record is `INHERITED`.
2. **Rebuild the profile** and diff it against each record's snapshot.
3. **Harvest evidence.** Search code and history for §6 signals. Count commits
   and issues per component with a script.
4. **Return one verdict per component.**

   | Verdict | Condition |
   | --- | --- |
   | `CHOOSE` | Select only: the option the profile favors, recorded with its tripwires |
   | `KEEP` | The profile change stays within the envelope and no tripwire fired |
   | `ADJUST` | Same component; different tier, configuration, or usage, or removal of an unused part |
   | `WATCH` | A tripwire is approaching; set the new threshold and date |
   | `MIGRATE` | The profile now favors another option, and the forward cost of staying exceeds the migration cost over the planning horizon |
   | `DEFER` | A required dimension or measurement is missing; name it |

5. **Justify `MIGRATE` with forward costs only**: workaround effort, incidents,
   and blocked requirements against the migration cost. Sunk investment is
   never an argument.
6. **Update each record**: new snapshot, new tripwires, next review date.

## 8. Output Contract

Emit one record per component:

```text
Mode:            Select | Review (<trigger>)
Component:       <foundation component>
Door:            ONE-WAY | TWO-WAY
Status:          DECIDED | PROVISIONAL | INHERITED
Forcing need:    <requirement that forces this choice, or none found>
Profile:         <dimensions relied on; GAP where blank; old -> new in Review>
Evidence:        <counted signals, measurements, skeleton results; NOT VERIFIED where none>
Verdict:         CHOOSE | KEEP | ADJUST | WATCH | MIGRATE | DEFER
Tripwires:       <signal, threshold, owner, where evaluated>
Reversal cost:   <estimate, and what raises it>
Handoff:         <skill that owns the next decision, or none>
Next action:     <one concrete action>
```

## 9. See Also

- **`requirements-grounding`** - the quality-characteristic sweep that fills the profile.
- **`bring-down`** - whether one capability should be bespoke or external, and which service.
- **`dependency-lifecycle`** - vendor-side triggers on a platform already owned.
- **`evolutionary-database-design`** - staging a store migration.
- **`structural-simplification`** - component count and diversity deltas.
- **`zero-copy-requirements`** - where the decision record lives.
