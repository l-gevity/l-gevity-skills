---
name: dependency-lifecycle
description: >-
    Decides what to do about a third-party dependency after it is adopted, for
    the whole time it is owned. Use when an advisory, an abandoned or archived
    upstream, version drift, a license change, or an end-of-life date names a
    dependency; when classifying a version bump as routine or
    contract-changing; when choosing between upgrading, pinning, patching,
    isolating, replacing, vendoring, accepting, or removing; when setting
    upgrade cadence; or when auditing a manifest for unused, unreachable, or
    undecided dependencies. Do not use to decide whether to adopt an external
    capability at all, which pipeline stage a scan runs at, or how a gate
    blocks; hand those to bring-down, defect-shift-left, and
    ci-cd-reliability-architecture.
---

# Dependency Lifecycle

A dependency is code you own but did not write. Adoption transfers the
maintenance, never the responsibility.

> **Purpose**: Every owned dependency has a current decision, and every
> accepted risk has an owner and an expiry.

> **Core Directives**
>
> 1. **Standing still is a change.** A manifest nobody edits still drifts:
>    upstreams move, advisories land, support windows close. Age is a trigger
>    on its own, with no commit to attach it to.
> 2. **A scan produces evidence, not a decision.** A finding is open until a
>    response is chosen and recorded. Suppressing it is a response only when it
>    is recorded as one.
> 3. **Exposure is reachability, not presence.** Grade a finding by whether a
>    call path in this system reaches the affected behavior, not by whether the
>    package resolves in the lockfile.
> 4. **Every acceptance expires.** An accepted risk carries an owner, a reason,
>    and a date or trigger that reopens it. A permanent suppression is an
>    undecided finding wearing a decision's clothes.
> 5. **Routine is a property of the contract, not the version number.** A bump
>    is routine only when nothing this system depends on changed meaning.
> 6. **Cadence beats reaction.** Small continuous upgrades are one decision
>    each; a deferred upgrade compounds into a migration.
> 7. **Exit cost is designed.** The surface imported decides what replacing the
>    dependency later costs. Depth of use is a choice made at adoption and
>    revisited at every trigger.

## Boundary

`dependency-lifecycle` is a task-matched Alchemy companion, not a qualification
stage, gate, or acronym letter. It runs in a single pass, whenever a trigger
names a dependency this system already owns.

This skill decides *what to do about a dependency already in the tree*. It does
not decide whether to depend on something in the first place, where a check
runs, or whether a gate blocks.

- `bring-down` owns adoption: whether a capability should be bespoke or
  external at all, and the selection evidence for choosing one. This skill
  takes over the moment the choice is in the manifest.
- `defect-shift-left` owns which stage the advisory, license, and unused-package
  scans run at. This skill owns the verdict when one of them fires.
- `ci-cd-reliability-architecture` owns whether a finding blocks merge or
  release, and how the artifact carrying the dependency is built and promoted.
- `functionality-complexity-tradeoff` owns whether the functionality the
  dependency serves is still worth keeping. A `REMOVE` response cites its
  verdict rather than reaching one here.
- `architecture-guidelines` and `morphogenetic-architecture` own where an
  adapter around a dependency sits and which subsystems may import it.
- `evolutionary-database-design` owns compatibility when an upgrade changes a
  persisted or serialized shape this system writes or reads.
- `system-optimization` detects outdated tooling and unused packages as waste
  and hands the subject here; this skill returns the decision.

Apply a project profile for ecosystem names, manifest and lockfile paths, scan
commands, advisory sources, and support-window policy. Keep none of those here.

## 1. Ownership Tier

Tier sets how much a decision costs and how often the dependency is reviewed.
Assign it from the surface actually used, not from the package's reputation.

| Tier | Test | Consequence |
| --- | --- | --- |
| **LOAD-BEARING** | Runtime, on a request or data path, and used through a wide or deeply integrated surface | Replacement is a project. Upgrade continuously; never defer twice. |
| **PERIPHERAL** | Runtime, but reached through one narrow owned surface | Replacement is an increment. The adapter is the asset; keep it thin. |
| **BUILD-TIME** | Never present in the shipped artifact | Exposure is the build environment, not the product. Advisory severity is graded against the build, not the user. |
| **TRANSITIVE-ONLY** | No first-party import; arrives through another dependency | The decision belongs to the parent. Pinning it directly creates a constraint nobody owns. |

A dependency whose tier cannot be named has an unknown surface. Establish the
surface first; every response below depends on it.

## 2. Triggers

These open a decision. Four of the five fire without any change to this
repository, which is what makes the set a standing obligation rather than a
review step.

| Trigger | Signal | Opens |
| --- | --- | --- |
| **Advisory** | A published vulnerability affects a resolved version | Reachability grading (§3), then a response |
| **Drift** | The pinned version trails the current release by enough that an upgrade is no longer a single step | A cadence decision (§6) |
| **Abandonment** | No release, no maintainer response, archived repository, or a sole maintainer with no successor | `REPLACE`, `VENDOR`, or a dated re-check |
| **Expiry** | A runtime, engine, platform, or support window reaches a published end-of-life date; a license or governance term changes | A response before the date, not after |
| **Orphaning** | The last first-party import is deleted, or the functionality it served is retired | `REMOVE` |

An `Expiry` trigger has a known date in advance. Meeting it late is a planning
failure, not an incident.

## 3. Reachability Grading

An advisory names a version; it does not name this system's exposure. Grade
before responding, and record the grade — it is the evidence a later `ACCEPT`
stands on.

| Grade | Test |
| --- | --- |
| **REACHED** | A first-party or transitive call path reaches the affected behavior under conditions this system produces |
| **PRESENT-UNREACHED** | The code resolves but no call path reaches it, or reaching it requires input this system cannot receive |
| **BUILD-ONLY** | Affected behavior runs only in the build or test environment and is absent from the shipped artifact |
| **UNKNOWN** | Reachability was not established |

`UNKNOWN` is not a low grade; it is the absence of one. Treat it as `REACHED`
until the analysis is done, and say which it was in the record.

## 4. Response Ladder

Choose exactly one response per trigger. `UPGRADE` is the default; every other
row is a reason not to take it, and carries a guard that ends the exception.

| Response | Admission test | Guard |
| --- | --- | --- |
| **UPGRADE** | A fixed or current version exists and its contract change is absorbable now | None needed. This is the expected answer. |
| **PIN** | A fix exists, but its contract change cannot be absorbed in this iteration | Names the increment that absorbs it and the date that increment is due |
| **PATCH** | No fixed release exists, the change is small enough to carry locally, and upstream is alive | Submitted upstream; the local patch is deleted when the release lands |
| **ISOLATE** | The exposure is one reachable path that can be cut, gated, or moved behind an owned boundary | The cut is enforced by a rule, not by convention; see `architecture-as-code` |
| **REPLACE** | The dependency fails on more than this trigger, and a compatible capability exists | Runs through `bring-down` for the replacement choice; the old dependency's deletion is the completion condition |
| **VENDOR** | Upstream is abandoned, the needed surface is small, and this system can own it outright | Becomes first-party code with an owner, tests, and a budget. Vendoring without that is abandonment with extra steps. |
| **ACCEPT** | `PRESENT-UNREACHED` or `BUILD-ONLY`, or a named compensating control already blocks the path | An owner, the grade it rests on, and a date or trigger that reopens it. Never open-ended. |
| **REMOVE** | Nothing imports it, or the functionality it served failed its worth verdict | The manifest entry and the lockfile record go in the same change |

A response that cannot satisfy its guard is not that response. Fall back to the
row above it.

## 5. Classifying a Version Bump

A bump is contract-preserving only when no contract this system depends on
changed meaning. The version number alone does not establish that.

| Signal | Class |
| --- | --- |
| Lockfile-only resolution inside an unchanged range, with no symbol this system imports affected | Contract-preserving |
| Major version, or any change to a symbol or option this system imports | Contract-changing |
| Changed default behavior, even within an unchanged version range | Contract-changing |
| Raised runtime, engine, or platform floor | Contract-changing |
| Raised a floor that another dependency also constrains | Contract-changing |
| Changed license, governance, or distribution terms | Contract-changing |
| Changed a serialized, persisted, or wire shape this system reads or writes | Contract-changing; hand to `evolutionary-database-design` |

A contract-preserving bump dispatches `SKIP`. A contract-changing bump is a change to an
external contract: it runs the gate it touches and its verification moves with
it. Classify before dispatching, because the classification is the dispatch.

## 6. Cadence and the Standing Sweep

Cadence is a design decision per tier, not a reaction to advisories. Record the
review interval with the tier; the interval is what makes a `Drift` trigger
observable.

A sweep with no named dependency enumerates from the manifest and lockfile
together, then reports one row per dependency plus the unreached remainder:

- Resolved entries with no first-party import are `TRANSITIVE-ONLY` or orphaned.
  Distinguish them; deleting a transitive entry removes a constraint the parent
  still needs.
- Direct entries with no import are `REMOVE` candidates, not removals — a
  plugin, a type-only import, or a runtime-loaded module has no static edge.
  Name how the absence was established.
- A dependency with no current decision is itself the finding. Undecided is a
  state to report, not a gap to fill silently.

## 7. Output Contract

```text
Dependency:      <name and resolved version>
Tier:            LOAD-BEARING | PERIPHERAL | BUILD-TIME | TRANSITIVE-ONLY
Trigger:         advisory | drift | abandonment | expiry | orphaning
Reachability:    REACHED | PRESENT-UNREACHED | BUILD-ONLY | UNKNOWN
Evidence:        <call path, advisory ID, release date, or EOL date>
Bump class:      routine | contract-changing | not applicable
Response:        UPGRADE | PIN | PATCH | ISOLATE | REPLACE | VENDOR | ACCEPT | REMOVE
Guard:           <condition that ends this response, with owner and date>
Handoff:         <skill that owns the next decision, or none>
Next action:     <one concrete action>
```

In a sweep, emit one row per dependency, then the unreached count:

```text
| Dependency | Tier | Trigger | Reachability | Response | Guard |
| ---------- | ---- | ------- | ------------ | -------- | ----- |
```

## 8. See Also

- **`bring-down`** - whether to depend on an external capability at all, and which one.
- **`defect-shift-left`** - the earliest stage that can catch an advisory, a license conflict, or an unused package.
- **`ci-cd-reliability-architecture`** - whether a finding blocks merge or release.
- **`functionality-complexity-tradeoff`** - whether the functionality the dependency serves is still worth keeping.
- **`evolutionary-database-design`** - upgrades that move a persisted or serialized shape.
- **`architecture-as-code`** - enforcing an isolation boundary so it survives the next contributor.
