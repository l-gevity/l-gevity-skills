# Infrastructure Fit: The Decision Nobody Made

A team starts a new product from a starter template. It is a good template:
hosting, a serverless backend, identity, a document database, pipelines, all
wired together and deploying on day one. The team gets to features quickly,
which is the point of a template.

The product turns out to be about employers, employees, roles, assessments,
and reports that join all of them. Three months in, the backend holds a growing
set of hand-written uniqueness checks, retries for write conflicts, joins
assembled in application code, and readers that cope with older document
shapes. One commit in eight touches the store; one issue in three mentions it.
Somebody finally asks why the product runs on a document database, and the
honest answer is that nobody chose it. It was in the template.

This document explains infrastructure fit: the idea that the foundation a
system runs on should be chosen from what the system has to do, and checked
again whenever that changes.

## A template default is a decision nobody made

A template carries two kinds of choices, and they look identical in the
repository. Some are tooling: a linter, a formatter, a pipeline layout.
Getting those wrong costs an afternoon. Others are foundations: the datastore,
the identity provider, the compute model, the region. Getting those wrong costs
a migration.

The trap is that a template makes the second kind feel like the first. Every
choice arrives already working, so none of them gets questioned. They were
reasonable defaults for the template's author, who could not know the product.
The decision about *this* product's foundation was simply never taken. It was
inherited, and inheritance looks exactly like a decision until the workarounds
start.

## Profile before platform

The fix is ordering. Before the foundation is chosen, write down what it has to
carry: a handful of core entities and how they relate, the few hardest queries
and reports, the realistic scale with a ceiling, where data may live and how
tenants are kept apart, how long data is kept and how it is erased and
restored, who signs in, what kinds of work run, how many people will operate
it, what it may cost, and how much it would hurt to be unable to leave a
vendor.

None of this takes long, and most of it is already in the requirements. What
it does is turn "which database?" from a matter of taste into a question with
an answer. A domain whose core is entities, relations, and rules that span them
is relational, and a store that cannot express those rules will have them
written by hand, again and again, in application code. A product for tens of
small customers does not need a store built for global scale; it needs the
cheapest thing that gets transactions and joins right.

A blank in the profile is information too. It means the choice that depends on
it is provisional, and should be labelled that way rather than presented as
settled.

## Not every choice deserves the same rigor

Spending a week deciding on a formatter is waste, and so is spending ten
minutes on the datastore. The useful line is reversibility. A two-way door can
be walked back cheaply, so take the default and move on. A one-way door — the
data model, identity, compute and hosting, region, tenancy — gets a written
record: which requirement forced the choice, what else was considered, what
would make it wrong, and what reversing it would cost.

That record is short. Its value is that it can be checked later by someone who
was not in the room, against requirements that may since have moved.

## The boring default, and the reason to leave it

For most products the defaults are unglamorous: one relational database, one
deployable application, a standards-based identity provider with authorization
kept in the application, no message broker until a job table demonstrably
cannot cope, one region. Each can be left, but only for a reason the profile
shows — data that is genuinely schemaless, load that is mostly idle, a scale
one node cannot carry.

Every platform-specific feature added on top brings behavior that has to be
discovered: middleware that does something no one wrote down, a local runtime
that times out, a deployment mode that silently skips code it was not told
about. Each one may be worth it. The test is whether it can name the
requirement that forced it.

## Prove the hard paths first

The cheapest time to find out that a foundation does not fit is before
anything is built on it. A walking skeleton runs the paths that are hard to
retrofit end to end: running the stack locally and in the pipeline, signing in
with one real authorization check, deploying and rolling back, restoring a
backup, erasing one person from every store, proving one tenant cannot read
another's data, and running the hardest report.

These paths are usually postponed because they are not features. That is
exactly why they surface late, as incidents or audit findings, when the
foundation under them is already load-bearing. A path that cannot be made to
run is not a backlog item. It is evidence about fit.

## A tripwire nobody checks is a comment

"We will revisit this when we grow" is how most foundation decisions are
deferred, and it almost never happens, because nothing is scheduled to make it
happen. A real tripwire has four parts: a signal anyone can observe, a
threshold, an owner, and a place where it is evaluated — a pipeline check, a
release gate, a periodic review. Without those it is a comment.

The best signals are already in the code and the history, and they can be
counted rather than argued about: uniqueness and referential checks written by
hand, retries on write conflicts, joins in application code, readers for old
document shapes, manual steps repeated per environment, and the share of
commits and issues spent on one component instead of on features.

## When the requirements move

Requirements change. Scale estimates firm up, a compliance obligation appears,
a second product shares the backend. A fit review rebuilds the profile from the
requirements as they are now, compares it with what each recorded decision
assumed, and returns one verdict per component: keep it, adjust it, watch it,
migrate away from it, or defer until a missing measurement exists.

Two rules keep that review honest. Only forward costs count: what was already
spent on a foundation is gone whichever way the decision goes, so it cannot be
a reason to keep it. And reversal is cheapest before real data arrives: once
production holds data, a migration needs a rehearsed data move, a window, and
users who must not notice. The review that matters most is therefore the one
just before the first real data, which is also the one most likely to be
skipped because everyone is busy shipping.

## Asking the question

The question infrastructure fit adds is not "is this a good platform?" — almost
every platform is a good platform for something. It is: **can each foundation
we run on name the requirement that put it there, and would we choose it again
from the requirements we have today?**

A foundation that cannot name its requirement was inherited. A decision with no
tripwire was never really open to revision. And a template default that
survives to production unexamined is the most expensive decision nobody made.

---

*Infrastructure fit takes its profile from
[requirements-grounding](READ-requirements-grounding.md), leaves the choice
between building and buying one capability to [bring-down](READ-bring-down.md),
and hands vendor-side events on a platform already owned to
[dependency-lifecycle](READ-dependency-lifecycle.md). A migration it decides is
staged by [evolutionary-database-design](READ-evolutionary-database-design.md).
The full operational reference — the fit profile, doors and defaults, the
walking skeleton, tripwires, review triggers, and the verdict set — lives in
[SKILL.md](../.claude/skills/infrastructure-fit/SKILL.md).*

<!-- skill-revision: 65a8877f43d4 -->
