---
name: evolutionary-database-design
description: >-
    Designs and audits compatible, staged, reversible changes to persisted or
    serialized data shape: database schemas, event and message schemas, API
    payloads, and file formats. Use when a change adds, renames, moves,
    narrows, reinterprets, or removes a stored or serialized element, changes
    a key or identity, transfers write ownership, or needs a backfill; when
    deciding whether old and new code versions can coexist against one schema
    during rollout and rollback; when planning an expand/contract transition,
    its reversal steps, and the evidence that permits the contract step; or
    when auditing never-contracted expansions, semantic drift, unowned data,
    and migrations without a reversal path. Do not use for component
    placement, requirement meaning, test technique, pipeline stage placement,
    gating, or evidence state; hand those to morphogenetic-architecture,
    requirements-grounding, test-strategy, defect-shift-left,
    ci-cd-reliability-architecture, and requirements-traceability.
---

# Evolutionary Database Design

Change persisted and serialized data shape in small, compatible, reversible
steps so that every code version that can be live at once — current, rolling
out, and rollback target — reads and writes the same store without a
coordinated cutover. Judge a change by which versions and readers it breaks,
not by whether the migration ran green in a development database.

"Schema" here means any persisted or serialized shape with independent readers
and writers: tables and columns, documents, event and message payloads, API
request and response bodies, exported files, and stored configuration. The
same compatibility model applies to all of them.

## Core Directives

1. **Every change is a refactoring, not an edit.** A data-shape change is one
   unit: the schema change, the data migration, and the access-code change.
   Never ship one without the others.
2. **Compatible with every live version.** Version skew is the normal state
   during a rollout, not an edge case. The shape must be readable and
   writable by every version that can coexist, including the rollback target.
3. **Expand before contract.** Add the new shape, move writers, backfill, move
   readers, prove the old shape has no reader, then remove it. The contract
   step is the only irreversible step; it is gated on evidence, never on the
   calendar.
4. **A reversal step per stage.** Each stage names how it is undone and what
   data that would lose. A stage with no reversal step is a contract step and
   carries the contract step's evidence bar.
5. **Meaning changes are new elements.** Changing what an existing element
   means — unit, encoding, time zone, currency, nullability semantics — under
   the same name is invisible to every compatibility check. Introduce a new
   element or version; never reinterpret in place.
6. **Data outlives code.** Historical records carry the semantics of the code
   that wrote them. Retention, backup, audit, privacy, and compliance
   obligations bind the data across the transition; a migration cannot
   destroy what an obligation requires kept.
7. **Absence of an import is not absence of a reader.** Reports, exports,
   analytics, backups, other repositories, and ad-hoc queries read a shape
   without importing anything. Unknown readers, unmeasured volume, and unowned
   data are findings, not assumptions.

## Boundary

Use this skill when an admitted slice changes a persisted or serialized shape,
or retrospectively when an existing store, contract, migration history, or
data incident provides a bounded subject. In Design mode, use two passes when
architecture can still change the target shape, its write owner, or the
deployment topology that determines which versions coexist:

1. **Compatibility pass — after readiness, before A.** Inventory the current
   shape, its readers and writers, the coexistence window, and the
   obligations that bind the data; classify the change and the compatibility
   mode it requires. This constrains the design and supplies the data facts
   that `morphogenetic-architecture` grades reversibility from.
2. **Transition pass — after final A/L/C and E when applicable, before H.**
   Consume the accepted target shape, ownership, and topology; fix the staged
   path, the migration units per stage, the backfill strategy, the contract
   trigger, the reversal step per stage, and the data contract.

Use a **Combined pass** only for Audit mode against a stable store, or when
the target shape, ownership, and topology are already accepted and will not
change.

Consume:

- the readiness package's data ownership and lifecycle, domain-model seeds,
  contract candidates, and cross-cutting constraints;
- current declared schemas, contracts, serializers, and migration history;
- deployment topology and rollout strategy: which versions coexist, and what
  the rollback target is;
- the `morphogenetic-architecture` reversibility grade when a boundary moves;
- data volume, write rate, lock behavior, and retention windows;
- historical migration incidents, escaped defects, and production signals.

If requirement meaning, data ownership, or the completion conditions of the
slice are unclear, return to `requirements-grounding` or
`implementation-readiness`. Existing schemas and access code are evidence of
readers and writers, not proof of their absence and not product intent.

This skill owns:

- the change classification and required compatibility mode;
- the transition design: staged path, reversal step per stage, contract
  trigger;
- the migration units: schema change, data migration, and access-code change
  per stage, and the backfill strategy;
- the data contract between a shape's writer and its consumers;
- the compatibility obligations handed to verification, placement, pipeline,
  and traceability skills.

This skill does not own:

- component placement, write-ownership assignment across boundaries, or the
  reversibility grade of a boundary move;
- requirement meaning, readiness, or the worth of the functionality the data
  serves;
- the structural complexity deltas of the data model;
- test technique, scope, or fidelity; the earliest pipeline stage for a
  check; pipeline preflight, gating, rollout, or rollback execution; or
  implemented-versus-verified evidence state;
- the choice of migration tooling, online-DDL tool, or schema registry;
- specialist privacy, security, or domain data policy.

Use this Alchemy hand-off when both passes apply:

```text
Implementation Readiness
→ Evolutionary Database Design — Compatibility pass: current shape, readers
  and writers, coexistence window, obligations, change class, mode
→ A → L/C → E, as justified: target shape, ownership, reversibility grade
→ Evolutionary Database Design — Transition pass: staged path, migration
  units, backfill, contract trigger, reversal per stage, data contract
→ Test Strategy — Portfolio pass: compatibility and migration evidence
→ Defect Shift-Left: earliest capable stage for each check
→ CI/CD Reliability: dry-run, reversibility gate, deploy order, rollback
→ Requirements Traceability: migration anchors and executed evidence
```

When `test-strategy` also applies, the Transition pass precedes its Portfolio
pass so the migration units are inside the evidence scope. Do not restart the
Compatibility pass after architecture unless the architecture changes which
elements change, who reads or writes them, or which versions coexist. If
accepted architecture changes after the Transition pass, rerun only the
affected stages before handing them to H.

`evolutionary-database-design` is a task-matched Alchemy companion. It is not
a new A.L.C.H.E.M.Y. letter, qualification stage, or gate.

## Workflow

### 1. Qualify the subject

Select a mode:

- **Design** — derive the transition for an admitted or clearly bounded
  change.
- **Audit** — assess an existing store, contract, or migration history
  against current readers, obligations, and incidents.

In Design mode, also select the design pass defined under Boundary:
Compatibility, Transition, or Combined.

Define the subject as the set of elements a slice changes, one store or
contract, or a bounded migration history. Do not plan for "the whole
database" when no change or incident bounds the work.

### 2. Inventory the shape and its parties

For each element that changes, record:

```text
Element:            <store.table.column | topic.field | contract.path | file.field>
Current shape:      <type, nullability, constraints, encoding, semantics>
Writer:             <owning component, or unowned>
Readers:            <components, reports, exports, analytics, backups, other repos>
Coexisting versions:<server versions live at once during rollout, plus rollback target>
Coexisting clients: <cached browser bundles, installed apps, pinned SDKs, or none — and how long each survives>
Volume / rate:      <rows or events, write rate, lock behavior, or unmeasured>
Obligations:        <retention, backup, audit, privacy, compliance, or none>
Reader evidence:    <access logs, query metrics, contract registry, grep, or none>
```

Use the widest evidence available for readers: query logs, access metrics,
contract or schema registries, consumer lists, and export inventories. A
grep across one repository is a lower bound. An element with an unknown
writer or an unbounded reader set yields `DEFER` for that element.

The coexistence window does not end where the deployment ends. Code the
deployment cannot reach still runs: a browser bundle already fetched, a mobile
app not yet updated, a pinned SDK in a partner's build. Each is a live version
of the reader for as long as its own lifetime, which is set by cache policy,
release cadence, or nothing at all. A window bounded only by the rollout
duration is a window measured from the server's point of view. When a client
lifetime is undeclared or unmeasured, the window is unbounded and the element
yields `DEFER`.

### 3. Classify the change

Classify each element by what it does to an existing reader or writer:

| Class | Example | Old code reads new data | New code reads old data | Default path |
| --- | --- | --- | --- | --- |
| Additive | New optional element, new table or topic, defaulted column | Yes, if tolerant reader | Yes | Single step |
| Widening | Relaxed constraint, longer type, new enum value | Breaks on the new value | Yes | Staged: readers first |
| Narrowing | Added constraint, not-null, shorter type, removed enum value | Yes | Breaks on old data | Staged: clean data first |
| Rename or move | Column rename, table split or merge, field relocated | No | No | Expand/contract |
| Semantic | Same name, new unit, encoding, time zone, currency, or meaning | Silently wrong | Silently wrong | New element or version; never in place |
| Destructive | Drop, delete, truncate, purge | Breaks | n/a | Contract step only |
| Ownership transfer | Write authority moves to another component or service | Depends | Depends | Staged with `morphogenetic-architecture` |
| Identity | Primary key, identifier format, or uniqueness change | No | No | Treat as semantic plus rename |

Then state the compatibility mode the coexistence window requires:

- **backward** — new code reads data written by old code;
- **forward** — old code reads data written by new code;
- **full** — both, the default whenever a rollout and its rollback can
  overlap;
- **full-transitive** — full across every version in the window, required
  when more than two versions coexist or historical data is never rewritten.

A weaker mode is acceptable only when a named owner accepts a coordinated
cutover or downtime, the record says so, and the acceptance **names the
consumers it covers**. "No external consumers" covers the parties it
enumerates and no others; an unnamed cached bundle, installed app, or pinned
SDK is not covered by it. An acceptance whose scope is not written down is
re-examined against the current `Coexisting clients` list, not inherited.

### 4. Design the transition

A change whose class and mode are satisfied by every coexisting version in one
step is `COMPATIBLE`. Every other change is staged. The staged path is:

```text
Expand          add the new shape; nullable or defaulted; nothing reads it yet
                reversal: drop the new shape
Migrate writers write both shapes, or write new and read old
                reversal: stop writing the new shape
Backfill        batched, idempotent, resumable, throttled, verified by count
                or checksum; run out of band from the deploy
                reversal: ignore the new shape
Migrate readers read the new shape, fall back to the old
                reversal: read the old shape again
Verify          evidence that no reader depends on the old shape
                reversal: none needed; nothing has changed yet
Contract        remove the old shape; snapshot or backup taken first
                reversal: restore from the snapshot — data written since is lost
```

Rules:

- Each stage is independently deployable and compatible with the previous
  stage's code.
- Expand and contract never ship in the same deployable.
- The contract trigger is evidence — access logs, query metrics, a closed
  deprecation window with consumer confirmation — not a date.
- Collapse stages only when the coexistence window proves them unnecessary,
  and record the proof.

Report the reversibility input for `morphogenetic-architecture`: every stage
before contract is a **reversible data change**; the contract step, or any
stage without a reversal step, is an **irreversible data migration**. That
skill grades the boundary; this skill supplies the staged path whose reversal
step its Low-reversibility bar requires.

### 5. Design the migration units

In a Transition or Combined pass, define one unit per stage:

```text
Stage:            <expand | migrate writers | backfill | migrate readers | verify | contract>
Schema change:    <DDL, contract diff, serializer change>
Data migration:   <backfill or transform, batch size, checkpoint, throttle, verification>
Access code:      <writer and reader change shipped with it>
Reversal step:    <how it is undone and what is lost>
Deploy order:     <what must be live before this unit>
Evidence:         <what proves this stage is complete>
```

Rules:

- Ship each unit's schema change, data migration, and access code together,
  in the same change as the code that depends on them.
- Make every migration idempotent and re-runnable; a partial run followed by
  a retry converges.
- Production rollback is the previous stage's code against the expanded
  shape. A down-migration is a development convenience, not a rollback path.
- Run a large backfill out of band from the deploy, in batches with a
  checkpoint, throttled against production load, and verified by counts,
  checksums, or dual-read comparison before readers move.
- Prefer online, non-locking schema operations; treat a full-table rewrite or
  a long lock as a capacity risk to be measured, not assumed.
- When a stage transfers write ownership, coordinate its deploy order with
  the accepted `morphogenetic-architecture` decision; dual-write across an
  ownership boundary is a transition, not an end state.
- Temporary scaffolding — dual writes, fallbacks, flags, migration code — is
  removed at contract. Migration code that has provably run on every record
  is a phantom requirement; hand it to `functionality-complexity-tradeoff`.

### 6. Emit the data contract

For every shape with a writer and at least one consumer outside the writer's
boundary, record:

```text
Shape:              <store, topic, contract, or file>
Owner:              <writing component>
Consumers:          <named readers, or unknown>
Compatibility mode: <backward | forward | full | full-transitive>
Versioning:         <additive only | versioned element | versioned contract>
Deprecation:        <window, notice channel, and the evidence that closes it>
```

A contract that names no consumer is a phantom. Where a schema registry or
contract-test framework can enforce the mode, encode it there and route the
tooling choice to `bring-down` rather than restating the rule in prose.

### 7. Hand off the checks

- Send compatibility obligations to `test-strategy`: every coexisting version
  reads and writes the shape; migration and backfill are idempotent; the
  oracle runs against real store semantics and production-shaped data, not an
  empty development database.
- Send each check to `defect-shift-left` for placement: schema-as-code at the
  design stage, migration lint and schema diff at static analysis, contract
  compatibility at integration, dry-run and reversibility at pre-deploy,
  version-skew at canary.
- Send deploy order, pre-deploy dry-run, reversibility gate, contract-step
  gating, snapshot requirement, and rollback artifact to
  `ci-cd-reliability-architecture`.
- Send the schema or migration identifier and its compatibility test to
  `requirements-traceability` as the data anchor.
- Send obsolete scaffolding to `functionality-complexity-tradeoff` and
  tooling substitution to `bring-down`.
- Send privacy, security, or domain data policy to the applicable companion
  skill without weakening it.

### 8. Audit the store

In Audit mode:

1. Map each element to its writer, readers, obligations, and last change.
2. Find never-contracted expansions: parallel columns, `_old` and `_new`
   pairs, forever-nullable additions, dual writes with no closing evidence.
3. Find semantic drift: an element whose meaning changed in place, and the
   historical records that still carry the earlier meaning.
4. Find unowned elements, unknown readers, and unversioned external shapes.
5. Find migrations without a reversal step, non-idempotent backfills, and
   contract steps that ran on a date rather than on evidence.
6. Treat every migration incident as evidence that the transition design
   missed a reader, a version, a volume, or an obligation.

A never-contracted expansion is not neutral: it doubles the write path,
splits the reader population, and leaves the reversal step of the original
change undefined. Either close it with evidence or record it as accepted
residual risk with an owner.

## Decision Rules

| Condition | Decision |
| --- | --- |
| Every coexisting version reads and writes the shape unchanged; no transition needed | `COMPATIBLE` |
| A staged path exists; every stage is independently deployable and reversible until a contract step whose evidence trigger, snapshot, and obligation clearance are named | `STAGED` |
| No compatible or staged path satisfies the obligations, or a contract step lacks its evidence trigger, snapshot, or obligation clearance | `BREAKING` |
| A writer, reader set, coexistence window, ownership, volume, or obligation is unknown | `DEFER` |

A Compatibility pass is provisional by design: its `COMPATIBLE` or `STAGED`
is a class, not a release-ready plan. Reserve the final decision for a
Transition or Combined pass against accepted architecture.

Do not emit `COMPATIBLE` from a green migration on an empty or synthetic
database, a passing down-migration, or the absence of imports.

## Output Contract

Emit one row per changed element:

| Element | Change class | Writer / readers | Coexisting versions | Compatibility mode | Transition stage | Reversal step | Evidence | Residual blind spot |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Then emit:

```text
Subject:              <store, contract, shape, slice, or migration history>
Mode:                 Design | Audit
Design pass:          Compatibility | Transition | Combined
Decision:             COMPATIBLE | STAGED | BREAKING | DEFER
Change class:         <additive | widening | narrowing | rename/move | semantic | destructive | ownership transfer | identity>
Compatibility mode:   <backward | forward | full | full-transitive | weaker, accepted by owner>
Coexistence window:   <server versions live at once, including the rollback target>
Coexisting clients:   <cached bundles, installed apps, pinned SDKs and their lifetimes, or none>
Reversibility input:  <reversible data change | irreversible data migration | unknown>
Staged path:          <stages in order, or single step>
Contract trigger:     <evidence that closes the old shape, or not yet defined>
Migration units:      <per-stage units, or not yet fixed>
Data contract:        <owner, consumers, mode, deprecation, or none needed>
Obligations:          <retention, backup, audit, privacy, compliance, or none>
Handoffs:             <test-strategy, shift-left, CI/CD, traceability, M, bring-down, companions>
Residual risk:        <accepted, blocked, deferred, unknown, or none identified>
Next action:          <one concrete stage, evidence, or owner question>
Verification:         <dry-run, dual-read comparison, counts, commands, or Not run + reason>
```

## Guardrails

- Do not infer absence of readers from absence of imports.
- Do not reinterpret an existing element in place.
- Do not ship expand and contract in one deployable.
- Do not schedule the contract step by date.
- Do not use a down-migration as the production rollback path.
- Do not run a large backfill inside the deploy step.
- Do not treat a green migration on an empty or synthetic database as
  compatibility evidence.
- Do not leave an expansion open without an owner and a closing condition.
- Do not claim an ownership boundary listed under Boundary; hand it off.
