---
name: concurrency-control
description: >-
    Decides how each shared persisted record serializes its writes so that
    concurrent saves, retries, and replays cannot lose an update. Use when
    several users, tabs, workers, or instances write one record, document,
    blob, or row; when a save reads, modifies, then writes; when a request can
    be retried or replayed; when one worker must own a job; or on lost updates,
    stale versions, ETag or If-Match, leases, fencing tokens, idempotency keys,
    or races. Do not use for schema change or test technique; hand those to
    evolutionary-database-design and test-strategy.
---

# Concurrency Control

> **Core Directives**
>
> 1. **Declare a write model per record.** Every shared persisted record names
>    one model from §1 before code writes to it. No model is a defect.
> 2. **The store enforces the model.** A check made between the read and the
>    write is a race; the condition travels with the write.
> 3. **A conflict is an answer.** A rejected write returns a result the caller
>    can act on. Never retry it unchanged or overwrite to make it pass.
> 4. **Prove the interleaving.** A test of one writer proves nothing about two.

## 1. Write Models

| Model | Use when | The write carries | On conflict |
|:--|:--|:--|:--|
| **Version check** | Writers edit one record independently | The version it read: ETag in `If-Match`, row version | Reload and reapply, or return 409/412 |
| **Single writer** | One process owns a job, partition, or schedule | A lease and a fencing token that rises with each lease | The old holder stops and writes nothing |
| **Idempotency key** | One request can arrive twice | A caller-chosen key, unique in the store, kept with the result | Return the stored result |
| **Commutative merge** | Updates combine in any order and no limit spans them: unbounded counters, sets, appends | An operation, not a value | None; a bounded counter needs a conditional operation |
| **Ordered start-up** | A computation reads state that loads asynchronously | A readiness signal it waits for | None: nothing runs on a partial read |

Last-writer-wins is not a model: it is a lost update with a timestamp.
Mechanisms per store, lease and token handling, key retention, and test recipes
are in [references/write-models.md](references/write-models.md).

## 2. Forcing Questions

For each record a change writes:

1. _"Who else can write it, a retry included?"_ "Nobody" must survive a
   scale-out.
2. _"Between the read this write depends on and the write, what stops another
   write?"_ Application code is a race.
3. _"What does the caller see when its write loses?"_
4. _"After a crash between two writes, which repeats, and is that safe?"_

## 3. Verification and Boundary

The oracle is the losing schedule: two writers from one version, a lost lease,
a replay, a save before load. `test-strategy` chooses fidelity, and
conditional writes need the real store or its emulator; `defect-shift-left`
places the unguarded-write check.

`architecture-guidelines` §7 owns in-memory and multi-tab state;
`evolutionary-database-design` owns moving write ownership between schema
versions; `infrastructure-fit` owns whether a store offers conditional writes.

## 4. Output Contract

Emit one record per shared record the change writes:

```
Subject:      <record, document, table, blob, queue, or job>
Writers:      <every writer, retries and replays included>
Write model:  Version check | Single writer | Idempotency key | Commutative merge | Ordered start-up | None (NOT-SHARED only)
Enforced by:  <If-Match, row version, unique key, fencing token, atomic operator>
On conflict:  <what the caller sees>
Decision:     DECLARED | UNGUARDED | NOT-SHARED
Verification: <interleaving test or lint rule, or Not run + reason>
Next action:  <one edit, test, or lint rule>
```

`UNGUARDED` names a writer with no model and blocks the change; `NOT-SHARED`
states why only one writer can exist and is the only decision `None` allows.
