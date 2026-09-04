# Alchemy: The Right Questions, in the Right Order, at the Right Size

Two ways to ruin an engineering discipline. The first is having none: every
change, from a typo fix to a new service, gets whatever thought the moment
allows, and the architecture becomes the sum of a thousand unexamined
decisions. The second is having too much: every change, from a typo fix to
a new service, must pass the same heavyweight checklist — so the checklist
gets pencil-whipped within a month, and you're back to the first way with
extra paperwork.

Alchemy is a design for avoiding both: a fixed sequence of design
questions — each one a concept in its own right, with its own explainer in
this collection — plus a dispatcher that decides *how much of the sequence
a given change deserves*. The questions provide the rigor; the dispatcher
provides the proportionality; and the ordering rule makes each question's
answer trustworthy. This document explains all three.

![Design and Refactor](design_and_refactor.svg)

## The questions, and why their order is fixed

Structural work — new modules, cross-boundary refactors, consolidations —
walks a sequence of gates. Each gate is a question, and the sequence is
arranged so that **every question is meaningless until the one before it
has passed**:

1. **Is it worth building at all?** — the
   [worth question](READ-functionality-complexity-tradeoff.md): does the
   problem exist here, and does the value justify the lifetime cost? A
   "no" here makes every following question moot — which is precisely why
   it goes first: the most expensive design work is elegant design of
   something that shouldn't exist.
2. **What is the smallest correct design?** — the
   [first-principles question](READ-architecture-guidelines.md): one
   concern per module, pure core, minimal abstraction.
3. **Where does it belong?** — the
   [placement question](READ-morphogenetic-architecture.md): which domain,
   tier, and layer, with which allowed neighbors — declared structure
   tested against observed evidence.
4. **Is the result actually simpler?** — the
   [measurement question](READ-structural-simplification.md): before/after
   deltas on the four complexity axes, replacing "it feels cleaner."
   Placement and measurement work as a handshake: a proposed restructuring
   isn't accepted on narrative — the move is named, measured, and only
   then confirmed.
5. **What enforces it?** — the
   [enforcement question](READ-architecture-as-code.md): decided
   boundaries become build-failing rules, in the *same change* as the code
   they govern — enforcement bolted on later arrives to find the erosion
   already started.
6. **Where are defects caught?** — the
   [shift-left question](READ-defect-shift-left.md): every error path
   mapped to the earliest stage that can catch it.
7. **Where does the flow bottleneck?** — the
   [optimization question](READ-system-optimization.md), deliberately
   deferred to the *second* iteration: optimizing before a design is
   stable tunes what's about to change, and stabilization beats
   optimization every time they compete.

The macro-structure is the part worth internalizing: **questions 1–4 shape
the design, 5–6 enforce it, 7 tunes it** — and running them out of order
produces recognizable pathologies. Enforcing before shaping locks in
accidents. Optimizing before enforcing tunes a structure that's still
leaking. Designing before asking "worth it?" produces beautiful
unnecessary things.

Upstream of gate 1, the same ordering logic extends into requirements:
before "is it worth building?" can be answered honestly, the problem must
be [grounded](READ-requirements-grounding.md) (real actor, real evidence),
non-trivial requirement sets get a
[dependency structure](READ-requirements-topology.md), and only work that
passes a [readiness check](READ-implementation-readiness.md) may enter
design at all — with
[traceability](READ-requirements-traceability.md) as the follow-through
once building starts, and a
[test-strategy](READ-test-strategy.md) pass on either side of design:
evidence obligations defined before architecture, the concrete test
portfolio finalized after it. These aren't extra gates so much as the same
principle — *don't answer a question whose prerequisite is unanswered* —
applied before the pipeline as well as inside it.

## The dispatcher: process proportional to structural risk

Here's the part that keeps the sequence alive in practice. The full walk
is *earned by the change, not owed by the process*. Before anything else,
a change is classified by one question: **how much structure could this
alter?**

- **Skip** — copy edits, CSS tweaks, routine dependency bumps, an isolated
  bug fix inside one governed boundary. Structural risk: none. Process:
  none. Fix the thing.
- **Direct** — the change poses exactly one clear question. "Should this
  dead code exist?" is the worth question alone. "Could this have been
  caught earlier?" is the shift-left question alone. One question, one
  gate, done.
- **Adaptive** — structure genuinely moves: responsibilities shift,
  boundaries change, a new module appears. Walk the *smallest set of gates
  the change actually implicates*, in order.
- **Full** — the complete traversal, reserved for when someone explicitly
  asks for it, typically a deep audit. Uncertainty is *not* a reason to go
  full: the answer to "not sure how big this is" is the smallest plausible
  route plus honesty about the uncertainty, not maximum ceremony.

The classification happens *before* any deep investigation — from the
request and readily available context — because a dispatcher that must
study everything before deciding what to skip has already not skipped it.

Why the proportionality matters more than it looks: a discipline that
costs too much on small changes doesn't merely waste time — it trains
everyone to route around the discipline, and then the *large* changes
escape too. The skip lane isn't a concession to laziness. It's what makes
the full lane credible.

Two rules keep the dispatcher honest. **Skips are recorded, with a
one-line reason** — "topology skipped: single bounded requirement, no
dependencies" costs ten seconds, and the difference between a *decided*
skip and a *forgotten* question is the entire difference between
proportionality and negligence; a recorded skip can be audited, a
forgotten question can't even be found. And **narrow questions get narrow
answers**: asking the placement question alone doesn't license a full
traversal — scope creep in process is still scope creep.

## Resume; don't relitigate

The third idea, easily overlooked: the gates produce **decision records**
— a worth verdict with its evidence, a placement with its rationale, a
measured delta. When work continues, it *resumes from the latest
trustworthy record* rather than starting over. A record earns that trust
by carrying its own lineage — each decision in it names what it
supersedes, and what it superseded is retired or marked lapsing — because
a record that still holds an old and a new answer side by side is not a
checkpoint but the argument itself, and resuming from it resumes the
argument.

This has two consequences. Decisions don't get relitigated for free — the
worth question, once answered with evidence, stays answered until new
evidence arrives; process that re-asks settled questions teaches people
that its questions don't stay answered, which is another road to
pencil-whipping. And failure has an address: when a gate fails, work
returns *to the specific failed question* — a complexity measurement that
rejects a design returns to the design question, not to square one; a
readiness blocker returns to the decision that's actually missing.
"Start over" is almost never the right granularity, in code or in
process.

Auditing existing code runs the same machinery from the other end: start
by *measuring* the structure as it stands (read-only — where is the
complexity concentrated?), recover the original intent only where it's
genuinely missing or disputed, then re-ask the worth question of what's
found and walk only the gates the remediation itself requires. Old code
gets judged by the same standard as new proposals — a feature that would
be rejected as a proposal today should not survive as code today merely
because it exists.

## The habit

The three ideas compress cleanly. *Fixed questions, fixed order* — worth,
design, placement, measurement, enforcement, detection, flow; each
meaningless until its predecessor passes. *Proportional entry* — the
change's structural risk, not habit or anxiety, decides how many of them
run; most changes deserve none, and that's the feature that keeps the rest
honest. *Resume from decisions* — answers are artifacts; work continues
from the last trustworthy one and returns to the exact question that
failed. Any team can run this with a wiki page and discipline; the value
isn't in tooling, it's in never designing what shouldn't exist, never
enforcing what isn't designed, and never optimizing what isn't stable.

---

*Each gate's underlying concept has its own explainer, linked above; the
[shift-left](READ-defect-shift-left.md) / [push-out](READ-push-out.md) /
[bring-down](READ-bring-down.md) improvement trio runs alongside the
pipeline for detection timing, operational toil, and code altitude. The
full operational reference — command grammar, dispatch rules, gate
handshakes, and the decision-trail format — lives in
[SKILL.md](../.claude/skills/alchemy/SKILL.md).*
