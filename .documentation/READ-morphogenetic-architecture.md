# Architecture as a Living Structure

Every team has the diagram: boxes, arrows, clean layers, drawn eighteen
months ago. And every team has the codebase, which has since grown opinions
of its own. Two modules that the diagram says are strangers change together
in every third commit. A "shared utilities" box has quietly become the most
depended-upon component in the system. An import cycle connects three
services the diagram shows as a tidy one-way chain.

The usual responses are denial (update nothing), or surrender (declare the
diagram dead and navigate by folklore). There is a third option: treat the
declared architecture as a **hypothesis** and the system's observed behavior
as **evidence** — and evolve the structure deliberately, the way living
forms grow: not from a fixed blueprint, but from simple local rules
responding to measured pressure. That's the idea this document explains,
and the reason for the name: *morphogenesis* is how organisms develop
shape.

![Morphogenetic Architecture](morphogenetic_architecture.svg)

## The skeleton: every component gets an address

Structure starts with a declaration. Every component gets a position along
three independent coordinates:

- **Domain** — which part of the business it serves: `billing`,
  `identity`, `commerce/payments`. Domains nest, and each is a boundary of
  *meaning*: inside it, words like "account" have one definition.
- **Abstraction tier** — its scale of responsibility: an *orchestrator*
  composes a workflow from capabilities; a *capability* does one
  meaningful job; a *primitive* is a small reliable building block. Tiers
  give a direction of service: primitives serve capabilities serve
  orchestrators — a primitive that starts directing its callers has
  inverted the hierarchy.
- **Layer** — its distance from the outside world: consumer-facing code,
  application/domain logic, infrastructure. Crossing more than one layer
  in a single step (a UI component reaching straight into the database) is
  a *layer skip* — legitimate only through a named adapter that owns the
  transition.

The coordinates are deliberately independent: "payments / capability /
domain-layer" says what a thing is, what scale it works at, and how far
from the edge it sits — and a component whose address you *cannot* state is
itself a finding, usually the first symptom of a module doing several jobs.

Around the address go local rules: each component exposes one **inbound
interface** (the contract callers use — everything else is private),
declares its **outbound** dependencies, and talks to a small, *named* set
of neighbors. Cross-domain access goes through the target domain's public
contract, never around it. Local rules are the whole trick — no one
component needs the global picture, yet a coherent global shape emerges
from every component keeping its own neighborhood honest. That is how
organisms manage it, too.

Those local rules are worth stating as one check rather than three habits,
because together they are **decidable**. Given every component's address and
the import graph, you can compute whether an edge is legal: layer and
abstraction tier are ordered, so "more than one step without a named adapter"
means something precise; domain is not ordered, so the only question there is
whether the edge goes through the target's public contract. Two whole-graph
clauses finish it — the static graph is acyclic, and an external SDK is
touched only inside its adapter.

That decidability is the point. It needs no telemetry, no history, and no
judgement, so it runs on day one of a greenfield system and it belongs in the
build rather than in a review comment. Resist the temptation to read more into
the coordinates than that: they are an address, not a space. `commerce/
payments` is not *nearer* to `commerce/shipping` than to `identity`; domains
are the same or they are different, and any distance you think you see between
them is a semantic judgement wearing a costume.

Legality is necessary, never sufficient. A legal edge can still be a bad one
for reasons only evidence exposes — which is the rest of the method.

## Many graphs, not one

The most common source of architectural confusion is talking about "the
dependency graph" as if there were one. There are at least five, and they
answer different questions:

| Graph | Edge means | Question it answers |
| ----- | ---------- | ------------------- |
| **Static** | A imports B | What can be built, tested, understood alone? |
| **Runtime** | A calls B in production | Where do latency and load actually flow? |
| **Change** | A and B change in the same commits | What is *really* coupled, whatever the imports say? |
| **Data** | A and B share a schema or store | Who else breaks when this table changes? |
| **Failure** | When B dies, A dies | Where does an incident spread? |

Two disciplines follow. First, **different graphs, different laws**: the
static graph must be a one-way, cycle-free hierarchy — a static cycle is a
hard fault, always. The runtime graph may legitimately contain loops
(retries, feedback, event flows), provided each is *declared*: named, given
a termination bound, an owner, and monitoring. Never let an acceptable
runtime loop excuse a forbidden import cycle — they live in different
graphs.

Second, **indirection can hide edges but not remove them**: routing a call
through an event bus, a registry, or a callback makes the arrow invisible
to import analysis while the coupling remains fully real at runtime.
Undeclared edges are the ones that hurt, precisely because nobody is
watching them.

## Pressure: when the map and the territory disagree

Now the interesting part. Overlay the observed graphs on the declared
skeleton and look for **boundary pressure** — evidence repeatedly straining
against a declared line:

- Two components in *different* declared domains that change together
  constantly, share data, and fail together — the boundary between them
  may be drawn through the middle of one real thing.
- One component whose edges fan out to several unrelated clusters, with
  several independent reasons to change — a god component, two or three
  real things wearing one name.
- A declared boundary that *no* evidence ever crosses — possibly a false
  boundary, ceremony separating things that belong together.

Pressure is information, not instruction. A single noisy signal — one
co-change burst from a cross-cutting rename, one traffic spike — is a
prompt to look, nothing more. The standard for actually moving a boundary
is deliberately conjunctive: **a domain-meaning reason and independent
observed evidence, agreeing on the same change.** Evidence without meaning
over-fits history; meaning without evidence is opinion with a diagram.

And the required weight of evidence scales with **reversibility**. Renaming
a module one team owns, with no published contract? Cheap to undo — decide
on light evidence. Splitting a service with external consumers, a
versioned API, and a data migration? Expensive to undo — demand multiple
independent lines of evidence, a staged path, and an explicit reversal
step. Grading a change's undo-cost *before* arguing about it is the
discipline; when in doubt, take the smallest reversible step first —
introduce the boundary and its contract, live with it, and move things
behind it only once it holds.

One escape valve keeps the discipline from becoming paralysis: when the
evidence simply doesn't exist yet — a young system with no history, a
boundary nobody instrumented — and the change is cheap to reverse, decide
*on probation*: make the move, but attach an expiry, the instrumentation
that will produce the missing evidence, and a named way back. Probation
covers absent evidence only; measured evidence that contradicts the change
always blocks it, and evidence sitting unfetched in version control doesn't
count as absent — probation is for evidence that cannot exist yet, not
evidence nobody ran the command for. The alternative — deferring everything
until telemetry appears — just moves the decision to whoever feels least
bound by the process.

## Evolution: the smallest sufficient change

When declared structure and observed evidence disagree, the resolution is
one move from a small vocabulary — deliberately small, so that every
structural decision is *nameable* and *recorded*:

| Move | When |
| ---- | ---- |
| **Keep** | Declaration and evidence agree — record that, too; it's what makes the next audit cheap |
| **Place** | A new component gets its address, interface, and neighbor set — the everyday case |
| **Move** | A component's evidence says it lives in the wrong domain, tier, or layer |
| **Split** | Independent change/failure clusters share one component |
| **Merge** | A boundary separates one purpose without buying any decoupling |
| **Introduce a boundary** | Cross-domain access needs one explicit contract instead of ad-hoc reaches |
| **Declare a runtime cycle** | A real feedback loop exists; give it bounds, an owner, observability |
| **Defer** | Evidence is missing or contradictory — say so, and name what's needed |

Prefer the smallest move that relieves the pressure, and prefer one
explicit boundary over a scatter of peer-to-peer exceptions. *Defer* is a
first-class outcome, not a failure: moving a boundary on insufficient
evidence is how systems get restructured annually, in a different wrong
direction each time. And before any restructuring move is accepted, it
faces the same test as any refactor — measure the before-and-after
complexity rather than trusting the story; a move that worsens every axis
while chasing a tidy narrative is still a bad move.

One more discipline before an expensive move: force a *second candidate*
— one genuinely different alternative, with its rejection condition named
in advance. Where it comes from is free: a graph algorithm's proposed cut,
a biological analogy, a colleague's competing decomposition. Analogies in
particular generate candidates, not verdicts — a structure is never right
because it resembles a tree or a honeycomb; if an analogy can't be tested
against something, it's decoration. Baseline and challenger then face the
same evidence, which is the cheapest known cure for falling in love with
your first idea.

## Homeostasis: making the shape self-maintaining

A structural decision that lives only in a diagram will drift again —
that's how the wall diagram got eighteen months stale in the first place.
The end of every evolution is therefore enforcement: encode each decided
static constraint ("domain code may not import infrastructure"; "only the
orchestrator may call this facade") as an automated import-graph check that
fails the build. New rules start as warnings until existing violations
clear, then become errors. Constraints that automation can't see — runtime
patterns, data ownership, failure isolation — get monitoring and review
checklists instead, explicitly, so nobody believes the linter covers what
it doesn't. A living structure needs an immune system, or every boundary
decision is a suggestion with an expiry date.

Enforcement guards the lines you drew; two more habits guard the drawing
itself. First, every restructuring ships with a **prediction** — the split
was made because these clusters change independently, so cluster-local
change should stay high; when the window closes, measure it. A confirmed
prediction retires the debate; a miss triggers the named way back — and a
rule that predicts wrongly across several decisions is itself the bug.
Second, make drift detection *standing* rather than heroic: the static
rules fail the build, and a scheduled declared-vs-observed comparison
watches what the linter can't see — new cross-boundary runtime edges,
co-change outliers, expired probations — so re-examination is triggered by
the system, not by whoever happens to remember the diagram exists. (A
freshly decided boundary rule still starts life as a warning; the standing
comparison carries it until it is promoted to a build-failing error.)

Probation only works if something remembers it. Every probationary decision
goes into a register — subject, expiry, the instrumentation that will settle
it, the way back, and an owner — and that register is what the scheduled
check reads. Skip it and you have not granted a probation, you have granted
an exemption; expiry dates nobody holds are the most reliably broken promise
in engineering.

## The habit

The mindset compresses to this: an architecture is a claim, and the system
continuously files evidence for and against it. Declare positions and
allowed directions explicitly — you can't detect drift from an undeclared
design. Keep the five graphs distinct, and be suspicious of invisible
edges. When evidence strains a boundary, require meaning *and* measurement
before moving it, with proof proportional to the cost of being wrong. Make
the smallest change that relieves the pressure, then encode it so it
holds. And re-examine whenever the ground shifts by an order of magnitude
— team count, traffic, data, components — because a shape that fit the old
scale is under no obligation to fit the new one.

---

*Related concepts:
[architecture guidelines](READ-architecture-guidelines.md) governs what
happens *inside* a component — this concept governs where components sit
and how boundaries between them evolve;
[structural simplification](READ-structural-simplification.md) provides the
four-axis measurement every restructuring move must pass; and
[architecture-as-code](READ-architecture-as-code.md) is the enforcement
mechanism that keeps decided boundaries from drifting. The full operational
reference — analysis modes, evidence fields, finding taxonomy, and the
decision record — lives in
[SKILL.md](../.claude/skills/morphogenetic-architecture/SKILL.md).*
