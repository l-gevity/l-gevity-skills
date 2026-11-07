---
name: gate-lifecycle
description: >-
    Keeps every gate (lint rule, CI check, hook, budget, debt baseline) proven,
    measured, and explicitly changed for as long as it exists. Use when a gate is
    added over existing violations, narrowed, suspended, trialed, or removed; when
    a baseline or exception list churns; when a gate passed while a known-bad input
    existed; or when a gate fails because it cannot evaluate rather than because of
    a violation. Do not use to place a check at a stage, decide how a gate blocks,
    or design the oracle it asserts; hand those to defect-shift-left,
    ci-cd-reliability-architecture, and test-strategy.
---

# Gate Lifecycle

A gate that stopped checking reports the same green as one that found nothing.
Here a **gate** is any automated check that can stop a change, not one of
Alchemy's lettered gates.

> **Purpose**: Every gate is proven, measured, and loosened only with a criterion,
> an owner, and an expiry.

> **Core Directives**
>
> 1. **A gate is proven by a failure, not a pass.** Green from a gate never seen
>    red is a claim about the gate, not evidence about the code.
> 2. **Effective scope is measured, never assumed.** A gate checks what its
>    resolved configuration and aggregation reach, not what it declares.
> 3. **A debt baseline only shrinks on its own.** Automation may remove entries;
>    growth is named in the change that makes it.
> 4. **Indeterminate is not failed.** A gate that could not evaluate said nothing
>    about the code: not a pass, not a violation, not a reason to remove it.
> 5. **Every suspension expires.** Something other than memory enforces its
>    criterion, owner, and expiry.
> 6. **Retirement needs a criterion met.** A gate leaves because what it checks
>    is gone or covered, never because it is inconvenient.
> 7. **The gate's own tooling obeys the gate's rules.** A script that regenerates
>    a baseline or aggregates results carries its own negative control and cannot
>    loosen the gate as a side effect.

## Boundary

`gate-lifecycle` is a task-matched Alchemy companion, not a qualification stage,
gate, or acronym letter. It runs in a single pass when a §2 trigger fires: after
H places a check, beside CI/CD's gate behavior, or later on its own. It decides
*whether a gate still does what it claims*, not where it runs, how it blocks, or
what oracle it asserts.

- `defect-shift-left` owns the stage. A check its §6.4 made blocking comes here
  for `PROVE`; its "remove as theatre" branch takes its criterion from §6.
  `RESTORE` never changes stage.
- `ci-cd-reliability-architecture` owns blocking and the Gate Evidence Contract.
  Its `Policy: baseline` is a debt list under §5; its `Result: not-applicable` is
  a `TRIAL` or `RETIRE` with this skill's guard. Whether a trial gate warns or
  blocks nothing stays there.
- `test-strategy` owns the oracle and per-test quarantine, whose fields a `TRIAL`
  reuses. The aggregator enforcing that oracle needs a negative control here.
- `architecture-as-code`, its stack skills, and `continuous-improvement` own a
  new rule; this skill takes over when §2 fires.
- `functionality-complexity-tradeoff` owns whether an obligation stands: `RETIRE`
  cites its verdict rather than reaching one.

A routine baseline shrink, a new rule nothing violates, a test added to a proven
gate without changing its scope, and a pure placement or blocking question do not
open this skill.

## 1. Gate Population

A project profile names where gates live and how they run. A sweep enumerates from
there; a check found elsewhere is unmanaged, which is a finding. The earliest
enforceable form is a registry whose entries each name a negative-control command
run in CI, so a gate added without proof fails.

## 2. Triggers

Most of these fire with no edit to the gate.

| Trigger | Signal | Opens |
| --- | --- | --- |
| **born** | Promoted to blocking, or added over existing violations | §3; §5 when violations exist |
| **narrowed** | A block, glob, ignore, filter, or skip changed its reach, or it passed while a known-bad input existed | §4 |
| **churn** | A baseline or budget moves on most commits, or grew with no named decision | §5 |
| **suspended** | Dropped, downgraded, or shortened "until" something, or that date passed | §6 |
| **indeterminate** | It could not evaluate: identity, environment, tooling, an unreachable dependency | §6 |
| **orphaned** | What it checks is gone, or its obligation lapsed | §6 |

## 3. Proof

`PROVEN` names a negative control and the last commit or run where it turned the
gate red. Without that record a gate is `UNPROVEN`, however long its green
history. The control is a committed known-bad input (rules, schemas), a self-test
feeding the runner a synthetic failing report (aggregators, budgets), or a
mutation of a tree copy (whole-tree gates).

- Run it through the gate as configured: a rule tested in isolation passes while
  the assembled configuration shadows it.
- Assert the declared message, rule, or exit code. A crash is also red, and a
  broken rule can hide behind the block that shadows it.
- A one-off probe proves the gate once. Where configuration can change under it,
  keep the control in CI.

## 4. Scope

Declared scope is what a gate says it governs; effective scope is what it reaches
once configuration resolves and results aggregate. Measure each way a gate shrinks:

- **Shadow.** A later or broader block replaces a narrower rule's options, with no
  error. Compare declared against resolved configuration; every rule fires on its
  control.
- **Narrow.** A glob, ignore, path filter, or skip marker drops files, or a new
  directory falls outside. Every rule governs at least one file; the governed set
  equals the source set.
- **Aggregate.** A summary counts skipped, retried, flaky, or not-run as passed.
  Feed the aggregator a report holding each state; it must fail. Aggregation
  semantics are scope.

An undeclared shrink is `RESTORE`. A deliberate narrowing updates the declaration
in the same change and says why.

## 5. Ratchet

A baseline admits known violations so a gate can block new ones. It is a debt
list, and one that moves both ways hides growth. Read
[references/ratchet.md](references/ratchet.md) for the reconcile algorithm and the
dated expiry step.

- Shrinking needs no decision. Growth is refused unless the change names the
  entry; a blanket update flag is regeneration under another name.
- A red run never writes the baseline. Regenerating from the current tree turns
  the gate into a recording of whatever exists.
- A stale entry is removed or fails the gate. Kept, it is headroom for the next
  regression.
- A budget raise is growth.

## 6. Decisions

Choose one decision per gate. A decision that cannot satisfy its guard is not that
decision.

| Decision | Admission test | Guard |
| --- | --- | --- |
| **KEEP** | Proven, in scope, baseline absent or only shrinking | None |
| **PROVE** | `UNPROVEN` | The control runs in CI, or its last red is recorded |
| **RESTORE** | An undeclared scope delta | The control that would have caught the shrink |
| **RATCHET** | A baseline or budget can grow without a named decision | Unnamed growth refused; the list has an owner |
| **TRIAL** | Its cost is measured and its value in doubt, or an evaluation outage outlasts what delivery can absorb | A measurable criterion, an owner, and an expiry a dated step enforces |
| **REINSTATE** | A trial failed its criterion or expired undecided, or the gate was removed for erroring | It blocks again and its control goes red |
| **RETIRE** | What it checks is gone, a proven same-scope gate catches it earlier, or M retired the obligation | Names that evidence; control and configuration go in the same change |

Past expiry the default is `REINSTATE`. A renewal is a new `TRIAL` citing data
measured in the window that ended; a moved date is not a decision.

`INDETERMINATE` is a status, not a decision. The gate keeps blocking under a
distinct exit code or label, so nobody reads it as a defect or a pass. Repair
evaluation; the rest of the record sets the decision. A gate that needs
target-environment state goes back to `defect-shift-left` for 8a. Being unable to evaluate is never a reason to
`RETIRE`; neither is never having fired, which is `UNPROVEN`, not useless.

## 7. Output Contract

```text
Gate:         <rule / check / hook / budget / baseline, and where it runs>
Stage:        <defect-shift-left stage, or unplaced>
Trigger:      born | narrowed | churn | suspended | indeterminate | orphaned
Proof:        PROVEN <negative control, last red commit or run> | UNPROVEN
Scope:        declared <…> / effective <…> / delta <none | what is no longer checked>
Baseline:     <none | count, trend, last accepted growth and the change that named it>
Status:       BLOCKING | TRIAL | INDETERMINATE | RETIRED
Decision:     PROVE | RESTORE | RATCHET | TRIAL | REINSTATE | RETIRE | KEEP
Guard:        <criterion, owner, expiry that ends this decision, or none>
Handoff:      <skill that owns the next decision, or none>
Next action:  <one concrete action>
Verification: <command, red run, or Not run + reason>
```

In a sweep, emit one table row per gate with these fields, then the `UNPROVEN`
count.

## 8. See Also

- **`defect-shift-left`** - the stage a check belongs at.
- **`ci-cd-reliability-architecture`** - how a gate blocks and what it records.
- **`architecture-as-code`** - rule recipes and the file-scope audit.
