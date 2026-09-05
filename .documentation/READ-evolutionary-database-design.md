# Data Outlives Code

The migration renamed `customer.region` to `customer.market`, updated every
query, and passed every test. The rolling deploy started at 02:10. By 02:12
half the pods were new and half were old, and the old half was throwing on
a column that no longer existed. The rollback then broke the new pods the
same way. Nothing in the migration was wrong; the assumption under it was —
that there is one version of the code, and the schema only has to agree
with that one.

**Evolutionary database design** is the discipline of changing stored and
serialized data — database schemas, event and message payloads, API bodies,
file formats — in small, compatible, reversible steps, so that every code
version that can be live at once keeps working. Use it whenever a change
adds, renames, moves, narrows, reinterprets, or removes a stored element,
changes a key, moves write ownership, or needs a backfill. It answers
three questions: which versions and readers does this change break, what
staged path makes it safe, and what evidence permits the one irreversible
step. The rest of this document explains why each of those questions has
the answer it has.

## Version skew is the normal state

During every rollout, and every rollback, two versions of the code run
against one schema. So the test of a data change is not "does the new code
work with the new schema?" but: **does every version that can be live at
once — current, rolling out, rollback target — read and write this shape?**
Data engineering names the directions: *backward* (new code reads old
data), *forward* (old code reads new data), *full* (both). A rollout that
can overlap its own rollback needs full. The same rule holds for a column,
a message field, an API body, and a file format.

## Every change is three changes

A database refactoring is one unit with three parts: the schema change, the
data migration for existing records, and the access-code change in
*everything* that reads or writes the shape. That last word is the trap.
Code coupling is visible in an import graph; data coupling is not. A
report, a dashboard, an export, a backup script, and a service in another
repository all read a table without importing anything. **Absence of an
import is not absence of a reader.** A grep is a lower bound; query logs
and consumer registries are the inventory.

## Expand, then contract

A change old and new code cannot both survive is never made in one step:
expand (add the new shape beside the old), migrate writers (write both),
backfill (batched, idempotent, verified), migrate readers (read new, fall
back to old), verify (evidence nothing reads the old shape), contract
(remove it, after a snapshot). Every stage before contract is reversible
by deploying the previous code, and every stage is compatible with the
stage before it — which is what keeps a rollback safe at every point. So
**expand and contract never ship in the same deployable**, and production
rollback is *the previous code against the expanded schema*. A "down
migration" is for resetting a local database; run during a real rollback it
destroys what the new code wrote.

## Contract is the only irreversible step

Contract is gated on **evidence** that nothing reads the old shape — zero
reads in the access logs, a deprecation window closed with consumer
confirmation — never on a date. It takes a snapshot first and checks the
obligations that bind the data: retention, backup, audit, privacy. And it
does happen: every `_old`/`_new` pair and every forever-nullable
"temporary" column is a doubled write path, a split reader population, and
a contract step that was scheduled by hope.

## Meaning changes are new fields

The change no compatibility check can see is keeping a field's name and
type and changing what it *means* — cents to dollars, local time to UTC,
reassigned status codes. Historical records keep the old meaning forever,
the schema looks identical, and every report that mixes the two is
silently wrong. A change of meaning is a new element, contracted through
the same staged path as a rename. Reinterpreting in place is corruption
with a delay.

## Keep the unknowns visible

The end state is not "the migration ran." It is: every changed element has
a known writer, an enumerated reader set, a coexistence window, a
compatibility mode, a reversal step per stage, and a contract trigger that
names its evidence — or an explicit, owned gap. "Readers unknown; access
logging on since September; contract deferred until thirty days of zero
reads" is a professional statement. The same column dropped because a grep
found nothing is an outage waiting for its report to run.

---

*Related concepts: [morphogenetic architecture](READ-morphogenetic-architecture.md)
decides where data ownership sits and grades how reversible a boundary move
is — this concept supplies the staged path that makes it reversible at all;
[test strategy](READ-test-strategy.md) decides what evidence proves every
coexisting version still works; [shift-left](READ-defect-shift-left.md) and
[reliable pipelines](READ-ci-cd-reliability-architecture.md) place and gate
the dry-run, the deploy order, and the rollback. The operational reference —
inventory, change taxonomy, staged path, migration units, data contract, and
decision rules — lives in
[SKILL.md](../.claude/skills/evolutionary-database-design/SKILL.md).*
