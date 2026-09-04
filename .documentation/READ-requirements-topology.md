# Requirements Are a Graph, Not a List

Sprint planning, Tuesday. The team picks ticket #34, "approval
notifications." Wednesday, someone discovers notifications need the
approval workflow — #29, not started. The workflow needs role definitions
— #12, "in discussion." By Thursday, #34 is back in the backlog wearing a
`blocked` label, and two days are gone.

The dependencies were real all along. The *backlog format* hid them: a
flat, ordered list can express "this is above that" and nothing else,
while the actual structure of any non-trivial requirement set is a web —
this needs that, this constrains that, these two secretly contradict each
other. This document explains requirements topology: treating requirements
as a typed dependency graph, making that structure explicit and
mechanically checkable instead of discovering it mid-sprint.

## Nodes: one requirement, one obligation

A graph is only as good as its nodes, and the entry condition is
**atomicity**: each node states exactly one outcome or obligation.
Compound requirements — "users can upload documents and administrators
can review them" — must split before any edges are drawn, for a concrete
reason: the two halves have different actors, different dependencies, and
different completion evidence, and a single node forces every one of those
statements to be about the *pair*. You can't truthfully say what a
compound node depends on.

Each node keeps a **stable, readable identity** — a slug like
`report-approval` rather than `R-047` — that survives every re-numbering,
re-grouping, and document reshuffle, because everything downstream (edges,
build order, tests, code annotations) will refer to it. When a requirement
genuinely splits or merges, the lineage is recorded — old name, new names,
why — so no reference anywhere silently dangles.

One more separation keeps the vocabulary honest: a node's *structural
role* (is it a foundation others build on? a constraint that limits
others? a workflow step?) is independent of its *subject matter*
(security, data, integration). A security requirement can be a foundation;
a data requirement can be a constraint. Conflating the two axes produces
categories that fight each other.

## Edges: name the relationship, don't just draw the line

The heart of the model. "Related to" is useless; a typed edge says *how*
two requirements relate, and each type carries different consequences:

| Edge | Meaning | What it implies |
| ---- | ------- | --------------- |
| **depends on** | A cannot be satisfied unless B exists | Build order — the load-bearing type |
| **enables** | A makes B easier or possible, not mandatory | Sequencing preference, not a blocker |
| **constrains** | A limits the valid ways to satisfy B | B's implementers must read A first |
| **verifies** | A proves or checks B | Evidence planning |
| **produces** | A creates output B consumes | Data flow between capabilities |
| **duplicates** | A and B likely overlap | A consolidation decision is pending |
| **conflicts with** | A and B cannot both hold | A human decision is *required* — the graph won't pick |
| **refines** | A is a more specific form of B | Abstraction levels stay linked |

Notice the last three don't describe the domain so much as *flag pending
decisions*. That's deliberate: a duplicate or conflict recorded as an edge
is a decision made visible and assignable; the same duplicate left in
prose is a surprise scheduled for integration week.

Two rules of hygiene. **Every edge carries evidence** — the source
sentence, the data-flow fact, or an explicit "inferred, because…" marker;
an edge someone once drew and no one can justify is exactly as dangerous
as a dependency no one noticed. And **direction is explicit** — "A depends
on B" and "B depends on A" schedule the work in opposite orders, so
ambiguity here isn't stylistic.

## What the graph gives you for free

Once the structure is explicit, questions that were meeting-length become
mechanical:

**Build order is computed, not authored.** Topologically sorting the
depends-on edges yields an order in which nothing is started before its
prerequisites — for free, and *only* from real edges. Document order,
ticket number, and priority rank are all illusions of order; priority says
what matters most, dependency says what's *possible* first, and confusing
them is how the most important ticket ends up blocked.

**Structural defects become findable.** Each has a mechanical signature
and a distinct meaning:

- **Cycles** — A needs B needs C needs A. Nothing in the loop can be
  finished first; usually a compound requirement hiding inside the nodes
  or a mislabeled edge type. Either way, a modeling error to fix, not a
  fact to schedule around.
- **Orphans** — a node with no connections. Either genuinely independent
  (fine, and now *stated*), or its dependencies were never mapped
  (dangerous, and now visible).
- **Duplicates and conflicts** — surfaced as pending decisions with names
  attached, per above.
- **Missing verification** — a requirement that nothing checks: unprovable
  as written.
- **Stale references** — edges pointing at renamed or split nodes; the
  graph rots exactly like code does, and the same discipline (validation
  on every change) keeps it alive.

**Natural groupings emerge.** Clusters that share data ownership, decision
owners, lifecycle, and test surface are candidates for being planned and
owned together. The restraint that keeps this honest: promote something to
a "shared foundation" only when *multiple* real clusters depend on it
today — a foundation with one consumer is a speculative abstraction in
requirements clothing.

## Two lines the graph must not cross

**The graph is a derived view, not a second source of truth.** The
grounded requirements — actors, wording, completion conditions — remain
canonical; topology adds structure *around* meaning and never edits
meaning to make the picture tidier. Normalizing a statement into atomic
form is fine; rewriting a contractual obligation because the diagram would
look cleaner is falsification. Same discipline as generated code: generate
views (registers, diagrams, orderings) from the one canonical model, mark
them read-only, and check them for drift — the moment a hand edit lands in
a derived view, there are two truths, and they will diverge.

**A requirements edge is not a software edge.** "Notifications depend on
approval workflow" says nothing about services, APIs, events, or
deployment units — it constrains the order of *understanding and
delivery*, not the shape of the *system*. Requirements structure is one
input to architecture; treating the requirements graph as a system diagram
skips the entire discipline of designing boundaries, and produces
architectures that mirror the org's paperwork instead of the domain.

## Replacements retire their predecessors

A quieter way the graph rots: a decision changes a requirement, and the
change lands as an *addition*. The new criterion goes in; the old one
stays, because the mechanism it describes is still running and nobody
wants to delete a line that still means something. Do that a few times
and one obligation carries two contradictory rules at once, the coverage
matrix reports both as green, and the next reader — human or agent —
resumes from whichever one they happen to read first.

The rule: a decision retires what it replaces *in the same change*.
Accepting a replacement marks its predecessor superseded, right there,
not in a follow-up. When the removal genuinely can't land yet — the old
mechanism still runs and tests still exercise it — the old record is
marked **lapsing**, with the condition that ends it written down: "until
the role check replaces the allow-list," not "until later." A lapsing
record is a retirement with an expiry attached; an unmarked predecessor
is two truths with none. Two active records for one obligation is
therefore a blocking finding in the graph checks, the same class as a
cycle, not a tidy-up for someday. And the retirement lives in the
lineage fields, where validation can see it — a replacement announced
only in prose is a replacement the tooling will never notice.

## The habit

The concept compresses to a reflex for whenever requirements are being
written, groomed, or planned: for each one, ask *what must exist before
this can be satisfied — and is that written down as an edge, with
evidence, or is it in someone's head?* The head is where #34's blockers
were on Tuesday. Every relationship moved from prose and memory into a
typed, evidenced edge is one integration-week surprise converted into a
planning-time fact — and the graph checks (cycles, orphans, conflicts,
verification gaps) become something you can run before committing a
sprint to it, rather than a lesson the sprint teaches you.

---

*Topology is the middle stage of a requirements discipline:
[grounding](READ-requirements-grounding.md) validates the nodes before
they enter the graph, and
[implementation readiness](READ-implementation-readiness.md) consumes the
graph to decide what is actually buildable. The full operational reference
— record and edge schemas, graph checks, repository gates, and output
modes — lives in
[SKILL.md](../.claude/skills/requirements-topology/SKILL.md).*
