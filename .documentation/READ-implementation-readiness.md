# Ready Means Something

The ticket was marked "ready for development." By lunch on day one, the
developer has three questions nobody can answer: which roles may approve a
report (a policy decision, still open), where customer data for the flow
actually lives (two systems claim it), and what "done" means (the
acceptance criteria say "works correctly"). The sprint absorbs the delay.
The retro notes "requirements could be clearer." Next sprint, same story.

"Ready" was a feeling — the ticket *looked* finished. This document
explains implementation readiness as something better: a **falsifiable
decision** with explicit criteria, made before work starts, that either
holds up or names exactly what's missing and who owns it.

## Readiness is a gate, not a vibe

The question the gate answers is narrow: *can a developer make responsible
decisions about this work, today, without inventing answers to questions
that belong to someone else?* That yields a concrete checklist. Work is
**ready** when:

- it traces to stable, identified requirements — not a paraphrase in a
  ticket that has quietly drifted from the source;
- its **completion conditions are usable** — observable checks a reviewer
  could verify, not "works correctly";
- it has a clear owner and actor — someone can answer questions, and it's
  known who the capability serves;
- every **prerequisite either exists or has a named minimal contract** —
  more on this below;
- **data ownership and lifecycle are identified** — which system is
  authoritative for the records this touches, and what happens to them;
- the relevant cross-cutting constraints (security, privacy, compliance,
  accessibility, operations) are *identified* — not solved, but known
  to apply, because retrofitted constraints are the expensive kind;
- **no unresolved decision remains that would change the required
  outcome.**

Each item is checkable, which is the point: "ready" becomes a claim that
can be *wrong*, and when it's wrong, the gap has a name and an owner
instead of surfacing as a stalled developer on day one.

## The distinction that does the most work

Not all open questions block. The gate turns on *what kind* of uncertainty
remains:

- **Product and policy uncertainty blocks.** "Which roles may approve?"
  changes the required *outcome*. A developer who proceeds must guess, and
  a guess about policy embedded in shipped code is a decision made by
  default, by the wrong person, at the worst time to change it.
- **Architecture uncertainty does not block — it becomes a recorded
  decision.** "Queue or synchronous call?" doesn't change what must be
  true for the actor; it changes how. Capture it as a decision record with
  its options and forces, and let building proceed — engineering decisions
  are engineering's to make, on engineering's schedule.

Teams that don't make this distinction fail in one of two directions:
blocking everything until a mythical fully-specified state (nothing
starts), or blocking nothing (everything starts, and the day-one
questions ambush every ticket). The gate blocks precisely the questions
whose answers change what "correct" means, and only those.

There's a middle verdict, and it's honest rather than lax: **partly
ready** — a bounded piece can proceed behind an explicit, *reversible*
assumption. The external API's contract isn't final? Build behind an
adapter that isolates the assumption, with the assumption written down and
a trigger for revisiting. The discipline is the boundedness: a named
assumption with a seam around it, not general optimism.

## Prerequisites: exists, contracted, or blocking

The most common readiness lie is the prerequisite everyone assumes someone
else has handled. The gate forces each one into one of three states: it
**exists** (verified, not assumed); it has a **minimal contract** (the
depending team can build against a small named agreement — the endpoint's
shape, the event's fields — even though the thing itself isn't finished);
or it is **missing**, in which case the dependent work is not ready, and
saying so *now* costs a conversation while discovering it mid-sprint costs
a sprint. A minimal contract is the legitimate middle: it converts "we'll
integrate later and hope" into "we agreed on this seam, and either side
can proceed."

## Prepare the build without designing it

Readiness sits between requirements and architecture, and its output is a
*preparation* package — with a strict rule about how far it may go:
**derive only what the requirements actually support; preserve every open
decision as an open decision.** The package typically contains capability
groupings, an implementation order (computed from real dependencies),
contract *candidates*, domain-model *seeds* — and the word choices are the
concept: a candidate is a place where a contract will be needed, not the
contract; a seed is a term the requirements themselves use, not a schema.
Uncertainty converted into confident-looking design is the subtle failure
here — a guessed payload in a readiness package reads as a decision, and
downstream everyone builds on it.

Two more lines the package must not cross. A dependency edge between
requirements implies *sequence*, never *system shape* — "notifications
depend on approval" doesn't mean a NotificationService calls an
ApprovalService; boundaries are architecture's job. And the package never
restates acceptance criteria in its own words — the canonical completion
conditions are referenced, because a paraphrase is a fork, and forks
drift.

## Start with the smallest coherent slice

Of everything that's ready, what gets built first? The principle: the
**smallest vertical slice that demonstrates the core outcome end to end**
— one actor, one workflow, real boundaries crossed, thin at every layer,
rather than a complete horizontal layer of everything.

The reasoning is about *when risk surfaces*. Horizontal layers feel
productive and defer every integration truth to the end, where surprises
are most expensive. A vertical slice drags the riskiest unknowns — does
the data flow, does the contract hold, is the outcome what the actor
needed — into week one, while everything is still cheap to change. The
slice also gives the readiness decision its first real test: nothing
exposes a phantom "ready" faster than attempting a thin end-to-end path
through it.

Two refinements decide the order among slices. First, the *riskiest
assumption* goes first: not the most valuable feature, but the belief that,
if wrong, invalidates the most of the plan — and it gets the cheapest vehicle
that can prove it wrong. A proof of concept kills one feasibility assumption
and is thrown away; a prototype tests what stakeholders actually want and
never ships; a minimum viable product is the smallest thing that lets real
use test the outcome hypothesis, and doubles as the first full rehearsal of
the delivery path.

Second, a slice is *parallel-ready* — safe to hand to several people or
agents at once — only when it is isolated enough to need little context,
small enough to merge on its own, unassigned to anyone in particular, and
independent of the other slices in its group. These are the conditions under
which work coordinates through the shared artifact instead of through
meetings; a group that fails one of them is a sequence wearing a parallel
costume.

## Ready ≠ built ≠ verified

Last, a bookkeeping rule that prevents a whole family of status lies:
readiness, implementation, and verification are **independent facts**.
"Ready" permits work to start — it asserts nothing about code existing.
"Implemented" says code exists — it asserts nothing about proof. "Verified"
says executed evidence passed. Any report that collapses these ("it's
ready" sliding into "it's basically done") is manufacturing status out of
category confusion. The gate's honesty on day zero — including its
willingness to say **not ready** with a named gap, which is a *cheap*
outcome, not a failure — is what keeps status honest at every later stage.

---

*Readiness is the third stage of a requirements discipline:
[grounding](READ-requirements-grounding.md) establishes that problems are
real, [topology](READ-requirements-topology.md) structures the dependency
graph readiness consumes, and
[traceability](READ-requirements-traceability.md) takes over once admitted
work enters implementation — tracking whether the evidence obligations
readiness defined are actually fulfilled. The full operational reference —
gate criteria, derived-artifact shapes, and the decision record — lives in
[SKILL.md](../.claude/skills/implementation-readiness/SKILL.md).*
