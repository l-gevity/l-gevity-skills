# Measuring "Simpler": The Four Axes of Complexity

Two engineers review the same refactoring proposal. One says it simplifies
the codebase — "it removes all that duplication." The other says it
complicates it — "it adds an abstraction layer." They are both right, both
sincere, and the discussion goes nowhere, because *simple* is doing two
different jobs in one conversation.

The way out is to stop treating complexity as a feeling and start treating
it as a **measurement** — one that anyone can take, before and after a
proposed change, and compare. This document explains the model: complexity
as a vector with four independent axes, and restructuring decisions as
per-axis before/after comparisons instead of intuition contests.

![Structural Simplification](structural_simplification.svg)

## The four axes

Take any structure made of parts and relationships — a codebase, a
deployment, a data model, a workflow, even an org chart. Its complexity has
four independent components:

| Axis | Question it answers | How to measure |
| ---- | ------------------- | -------------- |
| **Diversity** (D) | How many *kinds* of things are there? | Count the distinct patterns, shapes, and concepts a reader must learn |
| **Coupling** (K) | How *connected* is it? | Count the relationships — imports, calls, references — and their density |
| **Depth** (P) | How *long are the chains*? | Find the longest path from any entry point to any endpoint |
| **Quantity** (n) | How many *parts* are there? | Count them |

Each axis taxes the reader differently. Diversity taxes *learning*: a
codebase with twelve ways to fetch data must be learned twelve times.
Coupling taxes *change*: every edge is a path along which a modification
here becomes a surprise there. Depth taxes *tracing*: a five-hop chain
means five files open before you find where anything actually happens.
Quantity taxes *navigation*: more parts, more places to look.

The crucial rule: **score each axis separately, and never collapse them
into one number.** A single "complexity score" would let a large
improvement on one axis launder a serious regression on another — and it's
precisely the *shape* of the trade that a decision needs to see.

## Nothing is free: every operation trades axes

With the vector in hand, the two reviewers' argument dissolves into
something tractable, because almost every restructuring move improves some
axes *at the cost of* others:

**Extracting an abstraction** over three duplicated implementations:
diversity drops (three variant shapes become one pattern) and coupling
drops (N scattered dependencies collapse onto one) — but depth rises (every
reader now traverses an extra level) and quantity rises (the abstraction is
a new part). Whether that trade wins depends on the numbers: with three or
more genuine instances, usually yes; done speculatively for one, every
axis worsens at once — the measurable meaning of "premature abstraction."

**Adding a facade** in front of a messy subsystem: the interface *looks*
simpler, but the four-step chain behind it still exists — with the facade
now in front, chains are one hop *longer*. A facade **hides depth; it does
not reduce it**, and hidden complexity still bills you: measure the actual
structure, not the visible one.

**Flattening** — removing a middle layer that merely forwards calls: depth
and quantity drop; the check is whether the removed layer secretly earned
its keep (enforcing a boundary, hiding a volatile dependency), because its
callers now couple directly to what it concealed.

**Merging two parts**: quantity and diversity drop, but the coupling that
ran *between* them doesn't vanish — it moves inside, invisible to any
dependency graph. Merging two tightly-entangled parts is honest bookkeeping;
merging two unrelated ones creates the many-jobs module that is worse than
either original.

The pattern generalizes: *"is this simpler?"* is the wrong question. The
right one is *"which axes improve, which worsen, and is the trade worth
it here?"* — answerable, in writing, with counts.

## Two structural faults that outrank the arithmetic

Two findings aren't trade-offs at all — they're vetoes.

**Cycles.** In any structure that's supposed to flow one way — imports,
layering, ownership — a cycle (A depends on B depends on C depends on A)
isn't "high coupling"; it's a property violation. The three parts can no
longer be understood, tested, or replaced separately; they've fused into
one unit wearing three names. A restructuring that introduces a cycle is
rejected regardless of how nicely its other axes score. (Structures that
legitimately contain loops — state machines, retry logic, feedback systems
— are fine; there, the discipline is naming the loop's semantics and bounds
explicitly rather than pretending it isn't there.)

**False unification.** Merging lookalikes — two config keys, two roles, two
statuses collapsed into one — is safe only if every *other* part of the
system that references them treats all the merged members identically. If
some access rule bans one but allows the other, the merged item would need
to be half-banned: the difference you erased was load-bearing. Before
claiming a diversity win from any merge, enumerate the places that
reference the things being merged and check they're uniform.

## The decision protocol

The model becomes practice as a short written exercise — minutes, not days
— for any proposed restructuring:

1. **Model both states.** Sketch the parts and relationships before and
   after; record the four counts for each. The four *deltas* are the
   proposal's real content.
2. **Check for cycles** in the after-state. A cycle in a must-be-acyclic
   projection ends the evaluation.
3. **Answer four forcing questions in writing**, one line each — they
   surface exactly the self-deceptions refactoring proposals run on:
   - *What unique pattern does this introduce that nothing else uses?* And
     what's the second concrete instance? (No second instance → it's
     speculation.)
   - *Which previously-independent parts does this connect?*
   - *How long is the chain a typical change now traverses?* (More than
     three hops: the depth is itself the problem.)
   - *If we deleted the new part, what would its dependents do?* (If the
     answer is "use the thing it wraps, directly" — it's a pass-through
     that earns nothing.)
4. **Check the non-structural gates.** A structurally cleaner design that
   breaks a security, compliance, performance, or migration requirement is
   not an improvement — structure never outranks required behavior.
5. **Classify.** Every axis improves or holds → proceed. Mixed → weigh the
   specific trade, knowing there are legitimate asymmetric cases (below).
   No axis improves → reject; whatever the change is, it isn't a
   simplification.

## When losing on an axis is still winning

Three recurring cases where accepting a local worsening is correct — each
with a condition attached:

- **Conformance.** One module doing things its own way, among ten uniform
  siblings, inflates diversity out of proportion to its size — every
  reader must learn the standard pattern *plus* the exception. Rewriting
  the snowflake to match, even if slightly clumsier locally, deletes a
  concept from the codebase's vocabulary. *Condition:* the standard
  pattern must genuinely fit — a real domain difference deserves a name,
  not forced uniformity.
- **Deletion.** A special case costs more than its own code: it forces
  conditional paths, extra tests, and exceptions in every part that
  touches it. Removing a marginal feature improves all four axes at once —
  the only move that does. *Condition:* someone has verified the feature's
  worth is actually negative, and removal respects migration and
  compatibility promises.
- **Chosen atomicity.** Making a multi-step operation all-or-nothing
  demands coordination — coupling and depth rise, unavoidably. Accepting
  eventual consistency keeps the structure loose but requires documented
  tolerance of partial states. Either answer can be right; the fault is
  *not deciding* and letting the structure inherit an accident.

## The habit

The model compresses into a discipline of one sentence: **before accepting
any "simplification," write down the four deltas.** Kinds of parts,
connections, longest chain, count — before and after. The exercise takes
minutes and it converts refactoring debates from adjective exchanges into
comparisons of numbers. Most proposals survive it. The ones that don't were
the ones that would have quietly cost you for years — and the reviewer who
asks "what does this do to chain depth?" contributes more than the one who
says "looks cleaner."

---

*Related concepts:
[architecture guidelines](READ-architecture-guidelines.md) supplies the
design principles (Rule of Three, separation of concerns) that the axes
quantify; [worth evaluation](READ-functionality-complexity-tradeoff.md)
consumes these measurements as the cost side of its ledger;
[morphogenetic architecture](READ-morphogenetic-architecture.md) decides
where boundaries belong before this model measures the move. The full
operational reference — measurement recipes, operation catalogues, the
trade-off matrix, and the decision record — lives in
[SKILL.md](../.claude/skills/structural-simplification/SKILL.md).*
