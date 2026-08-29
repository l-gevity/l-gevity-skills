# Architecture-as-Code: Rules the Build Can Refuse

The team agrees, in a well-attended meeting, that domain logic must not
import infrastructure code. It goes in the architecture decision record.
Everyone nods.

Four months later, a grep finds eleven violations. Nobody rebelled — the
rule was simply invisible at the moment it mattered: 4:45pm, a deadline, an
autocompleted import that worked. Each violation made the next one look
normal. The decision record was never wrong; it was just *unenforced*, and
an unenforced architectural rule is a suggestion with a half-life.

This document explains architecture-as-code: the idea that a system's
dependency rules should live in version-controlled files that a linter
enforces on every commit — so the architecture *is* checked, the way types
and tests are, rather than remembered.

![Architecture as Code](architecture_as_code.svg)

## The enforceable slice of architecture

Not everything called "architecture" can be automated. What *can* be —
completely, cheaply, deterministically — is the **import graph**: which
modules are allowed to depend on which. That slice is worth automating
because most architectural erosion is exactly this: dependency arrows
appearing where the design says none should exist. Layer skips, domain
logic reaching into infrastructure, two sibling features quietly importing
each other's internals — every one of them is just an edge in the import
graph, and machines are excellent at checking edges.

The recipe has three ingredients:

1. **Name the components.** Declare that files under `billing/` are the
   `billing` module, that `core/facade.ts` is the `core-facade`, and so
   on — patterns mapping the directory tree onto named parts.
2. **Declare the forbidden edges.** `domain` may not import
   `infrastructure`. Nobody but the `orchestrator` may import
   `core-facade`. Sibling feature modules may not import each other.
3. **Check every commit.** An import-graph linter (they exist for every
   major ecosystem) evaluates the actual imports against the declared
   rules and fails the build on violation.

The 4:45pm import now fails *in the editor*, seconds after being typed,
with a message explaining the rule — which is why every rule carries a
**why**: the violation message is the architecture teaching itself to
whoever bumps into it, precisely at the moment they're making the mistake.
No meeting, no memory, no code-review vigilance required.

## The design discipline: who is allowed to know what

The naive version of this idea is one giant rules file at the repo root —
and it rots just like any other centralized registry: every module change
edits the same file, the file grows into an unreadable tangle, and after a
while nobody knows which rules still reflect intent. The pattern that
scales rests on a principle worth knowing beyond this context, because
it's the same principle that makes modules themselves work:

> **A module may know itself. It may not know its context.**

Concretely, every module (directory) may carry its own small architecture
file, and that file may declare only two kinds of things:

- **Its internals** — the module's own sub-parts and layering: "my tier-3
  code may not reach directly into my tier-1 code."
- **Its outbound rules** — what *it* imports: "core imports nothing outside
  core."

What a module's own file may *never* declare is anything requiring
knowledge of the wider world: who is allowed to import it, how it relates
to siblings, its place in the system. Those are **composition** concerns,
and they live one level up — in the architecture file of the directory
that composes the modules together. "Only the orchestrator may import the
core facade" is knowledge about how the composer arranged its parts, so
the composer's file says it.

The mechanical tell is memorable: *a module's own architecture file never
contains another module's name.* The moment it does, knowledge is leaking
across a boundary — the same smell as a class hardcoding its callers'
names, appearing one level up.

An assembler script walks the tree, gathers every architecture file, and
merges them into one configuration for the linter. Two conventions do
disproportionate work here. **Wildcards over enumerations**: writing "any
module except the orchestrator" as `* except orchestrator` rather than
listing modules means new modules are governed the moment they're created,
instead of silently ungoverned until someone remembers the list. And a
**catch-all pattern last in every governed module**: any file matching no
declared component is *invisible* to the linter, and invisible files bypass
every rule — the catch-all closes the gap that would otherwise make the
whole system quietly optional. The merged linter config itself is a build
artifact — generated, git-ignored, never hand-edited; the per-module files
are the single source of truth.

## Rules before code

A timing rule with an outsized effect: when creating a new module, write
its architecture file **before** its implementation, in the same change.

The reasoning is about what each ordering produces. Rules-first means the
very first wrong import fails immediately — the boundary is real from day
one, and the module grows inside it. Rules-later means the rules are
written to describe whatever dependencies have already accumulated — and
retrofitted rules face an ugly pair of options: rubber-stamp the accidents
(making the "architecture" a photograph of the mess) or declare war on
them (an unbounded refactor nobody scheduled). Ten minutes of declaration
before the first line of code buys years of a boundary that was never
crossed.

Honest exception: genuine throwaway spikes may skip rules — exploration
shouldn't fight scaffolding. The condition is that spike code never
crosses into the main branch ungoverned; it gets deleted, or rewritten
rules-first. "We'll add the rules later" is how permanent modules end up
permanently ungoverned.

## What this pattern is not

Three boundaries keep the idea honest:

- **It doesn't decide what the architecture should be.** Which boundaries
  exist, which direction dependencies flow — those decisions come from
  design principles and evidence, elsewhere. This pattern is the
  *enforcement layer*: it takes a decided constraint and makes it
  physically checkable. Encoding a bad architecture enforces a bad
  architecture, very reliably.
- **It sees only static imports.** Coupling that flows through runtime
  indirection — event buses, registries, dynamically-computed imports — is
  invisible to import analysis. That's a reason to prefer static, resolvable
  imports where possible, and to know explicitly which couplings the
  linter does *not* see, so nobody mistakes "the architecture lint passes"
  for "the architecture holds."
- **It replaces prose ADRs' enforcement, not their rationale.** The
  decision record still explains *why* the boundary exists; the rule makes
  it *hold*. One is for humans deciding whether to change the rule; the
  other is for the build refusing to let it erode by accident.

## The habit

The concept compresses into a question to ask about any architectural
agreement your team makes: *"what enforces this?"* If the answer is
"review vigilance and the wiki," you have a suggestion, and its half-life
started at the meeting. If a dependency rule can be stated as "X may not
import Y" — and most can — it can be a build failure instead. Declared
where the knowledge belongs, worded with its reason, checked on every
commit: that is an architecture that stays the way it was designed, not
because everyone remembers, but because nothing that violates it can
merge.

---

*Related concepts:
[architecture guidelines](READ-architecture-guidelines.md) and
[morphogenetic architecture](READ-morphogenetic-architecture.md) decide
which boundaries and directions the rules should encode;
[shift-left](READ-defect-shift-left.md) explains why enforcement belongs in
the editor and the build rather than in review — this pattern is its
"decision record → executable rule" move made systematic. Stack-specific
implementations exist for
[JavaScript/TypeScript](READ-architecture-as-code-javascript.md) and
[Python](READ-architecture-as-code-python.md). The full operational
reference — file schema, rule placement, assembler, and audit checklist —
lives in [SKILL.md](../.claude/skills/architecture-as-code/SKILL.md).*
