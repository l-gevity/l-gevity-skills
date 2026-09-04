# Grounding: The Problem Behind the Ticket

The ticket says: *"Add a CSV export button to the reports page."* It gets
estimated, built, tested, shipped. Three months later, telemetry shows
eleven clicks — nine of them from the team demoing it. Meanwhile the
person who asked is still doing, by hand, the thing they actually needed:
getting monthly figures into their finance tool, which speaks a format the
export never produced.

Nothing in the delivery failed. The failure happened before the ticket was
written: a *solution* was recorded and the *problem* never was — so
everyone downstream faithfully built the wrong thing. This document
explains grounding: the discipline of tracing every requirement back to a
real problem, a real actor, and honest evidence, before any of the
machinery of building gets to run.

## Requirements describe problems, not features

A grounded requirement starts from a problem statement that is deliberately
**solution-free**: it names an *actor* (who experiences this — a specific
role, not "users"), a *situation* (when it arises), an *outcome* (what must
become possible), and an *obstacle* (why it isn't possible today). Notice
what's absent: no button, no screen, no service, no format. "The finance
lead, at month-end close, must get report figures into the accounting
system without manual re-entry; today that takes four error-prone hours."

Why this shape matters practically, not just philosophically: it keeps the
solution space open (an API, a scheduled sync, or a different report layout
might all solve it — the CSV button happened to solve none of it), and it
makes the requirement *checkable* — you can go ask the finance lead whether
that's really their situation. "Add an export button" can't be wrong; that
is exactly what's wrong with it.

Two boundary statements complete the frame: **done-when** (what observable
state ends the problem) and **not-problem** (what this explicitly does not
cover). The second one looks like bureaucracy and is actually the scope
argument you'd otherwise have during the sprint, held early and cheaply
instead.

## Not all "requirements" carry the same weight

Every requirement rests on some basis, and the four kinds justify very
different confidence:

| Basis | It rests on | Honest attitude |
| ----- | ----------- | --------------- |
| **Authoritative** | A law, contract, standard, or binding decision | Verify the source really says this, applies here, and is current |
| **Interpreted** | Someone's reading of an ambiguous source | Record the reading *and the rejected alternatives*; revisitable |
| **Evidenced** | Observed behavior, measurements, user research | Weigh strength, reach, recency; prefer small commitments |
| **Hypothesized** | Someone's belief that a need exists | Test before building anything expensive on it |

The failure mode this taxonomy prevents is *basis laundering*: a guess gets
written in requirement grammar ("the system shall…"), survives two
meetings, and hardens into fact. Six months later nobody can distinguish
"legal made us" from "someone in a workshop thought so" — yet one of those
is negotiable and the other isn't. Keeping the basis attached keeps the
negotiability visible. A related trap: **priority is not certainty**.
"Must-have" says how much it matters *if real*; it is not evidence that it
is real. A must-have resting on a hypothesis is a risk to surface, not an
urgency to obey.

How much validation a requirement deserves before you act on it follows a
simple rule: **cost of being wrong × difficulty of reversal.** A reversible
UI tweak on a hypothesis? Ship it and watch. An irreversible schema
commitment on an interpreted clause? Validate the reading first.

## Three questions that must not blur

The single most clarifying distinction in this discipline is between three
questions that casual language mashes together:

1. **Is the problem real?** — settled by grounding: actors, sources,
   evidence.
2. **Is the capability complete?** — settled by *complete-when*
   conditions: two to four observable checks a reviewer can verify
   ("finance-compatible file downloads containing the displayed figures").
   Observable, but not implementation-prescribing.
3. **Did it have the hoped-for impact?** — settled only by measurement
   *after* real use: did month-end close actually get faster?

Confusing 2 and 3 causes damage in both directions. Put impact into
completion criteria ("done when close time drops 50%") and the team can't
finish — impact isn't in their control and isn't observable at ship time.
Treat completion as impact ("we shipped it, so it worked") and the export
button's eleven clicks count as success. The clean arrangement: completion
criteria stay observable and shippable, while the expected impact becomes
an explicit, separate **outcome hypothesis** — *we believe finance leads
will use this, cutting close time by half; measured by X against baseline
Y within window Z* — with the humility of the word "hypothesis" and its
own follow-up date. And one honest asymmetry: obligations don't need
hypotheses. A legal retention requirement doesn't wait for an experiment
proving users "engage with" retention.

## Reading requirements out of code

Often there is no requirements document — there's a codebase, and someone
asking "what is this supposed to do?" Requirements can be *recovered* from
code, but under one governing principle:

> **Code is evidence of what the system does — never proof of what it
> should do.**

The inspected version demonstrably exhibits its behaviors; whether each
behavior is intended, a defect nobody caught, a dead experiment, or a
workaround that outlived its reason — the code cannot say. So recovery
reads layers of evidence with different weights: *stated intent* (docs,
decision records — may be stale), *executable contracts* (tests, schemas —
strong on behavior, silent on why, and a test can faithfully preserve a
bug), *enforced behavior* (validation, permissions — actively imposed, but
possibly legacy), and *inference from names and structure* (weakest; keep
confidence low without corroboration).

Everything recovered this way is **provisional** until a human who owns
the domain confirms it — the deliverable is candidate requirements *plus a
confirmation queue*, not a retroactive specification. The discipline this
enforces: writing "the system must reject uploads over 10MB" because a
config file says `10485760` is transcription, not requirements work. The
requirement question is whether anyone *wants* that limit — and the code
has no opinion.

## Honesty as a formal property

The thread through all of it: a grounding artifact is valuable in
proportion to how visibly it carries its own uncertainty. Every requirement
states its basis, source, and confidence. Every consequential choice gets a
decision log entry — what was decided, on what, by whom, and what would
reopen it. Each entry also names what the decision supersedes: an earlier
decision left standing beside its replacement is not history, it is a
second answer the next reader may pick. Interpretations are marked as
interpretations; unverifiable sources make their requirements provisional;
open questions are listed as open rather than smoothed into confident
prose.

This inverts a common instinct — that requirement documents should look
authoritative. A document that *looks* certain and isn't will be trusted
exactly until it's expensive. The best one tells you precisely how far to
trust each line: *these three are contractual, verified against the signed
version; these five are our reading of an ambiguous clause, alternatives
noted; these two are hypotheses with experiments attached.* That document
you can build on — because when something turns out wrong, you know
immediately which kind of wrong it is and which decision to reopen.

---

*Grounding is the first stage of a requirements discipline: it feeds
[requirements topology](READ-requirements-topology.md), which structures
grounded requirements into a dependency graph, and
[worth evaluation](READ-functionality-complexity-tradeoff.md), which
decides whether a grounded capability justifies its cost. The full
operational reference — modes, recovery protocol, record shapes, and the
validation gate — lives in
[SKILL.md](../.claude/skills/requirements-grounding/SKILL.md).*
