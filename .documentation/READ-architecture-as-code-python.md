# Boundary Enforcement in Python: Contracts over the Import Graph

Python will happily let any module import any other module. `from
mypkg.core.internals import _do_things` works from anywhere — the
underscore is a social convention, not a wall. So when a team decides
"domain code must not import infrastructure" or "the billing package's
internals are off-limits," the language itself offers nothing to hold the
line.

The ecosystem does: a static analyzer builds the package's real import
graph, and a contract checker fails the build when the graph violates
declared rules. This document explains how that works in Python — the
mechanism, the idioms, and the specific blind spots worth knowing.

It assumes the
[architecture-as-code concept](READ-architecture-as-code.md): rules live in
small per-package files, an assembler merges them, a checker enforces the
merged result. Here we cover the Python half.

## The mechanism: a graph, then contracts

The tooling has two layers. First, a graph builder (**Grimp**) imports your
root package and walks every module's `import` and `from ... import`
statements, producing the complete static import graph — every edge from
every module to every module it names. Second, a contract checker
(**import-linter**) evaluates declared rules against that graph and exits
non-zero on violation, which is what makes it a pre-commit hook and CI
gate.

Rules address modules by their dotted paths, and a path matches the package
*and everything under it* by default — `mypkg.core.tier1` covers the whole
subtree, which is usually what a boundary means. Three contract shapes
cover nearly everything:

- **Forbidden** — the workhorse: modules in set A may not import modules in
  set B. "Core purity: `mypkg.core` imports nothing outside itself."
- **Independence** — N sibling packages may not import each other at all.
  One contract replaces N×(N−1) forbidden edges — the natural shape for
  "feature modules stay isolated."
- **Layers** — a strict ordering: `api` above `domain` above `storage`;
  higher may import lower, never the reverse. The whole layered
  architecture in one declaration.

In the architecture-as-code arrangement, each governed package carries a
plain-TOML `architecture.toml` naming its own components and outbound
rules; an assembler script discovers them all, expands the wildcards, and
generates the import-linter config as a git-ignored build artifact. The
per-package files are the versioned source of truth — the generated config
is never edited by hand.

## The facade idiom: a public sub-package

Every language grows its own shape for "this is the public API; the rest is
internal." Python's is the sub-package: `mypkg.core.api` exposes the
public surface through its `__init__.py` (with `__all__` naming the
official exports), while `mypkg.core.tier1`, `mypkg.core.engine`, and the
rest are implementation. The contracts then make the convention real:
outsiders may import `mypkg.core.api` and are *forbidden* from importing
the internal sub-packages directly. The underscore prefix asks nicely;
the contract refuses the merge. This is the single most valuable rule pair
in most Python codebases, because it's the difference between "we can
refactor core's internals freely" being true and being folklore.

## The blind spots

Static enforcement governs only what static analysis can see, and Python
has well-known ways of importing that it can't:

**Dynamic imports.** `importlib.import_module(name)`, `__import__`, and
string-based plugin dispatch never appear in the graph — the module name
is computed at runtime. One dynamic import can carry any dependency past
every contract, invisibly. The pragmatic posture: confine dynamic loading
to one explicitly-declared entry-point module whose rules are written with
that in mind, and keep the style banned everywhere else. A plugin system
gets one well-lit door, not a building with no walls.

**The environment matters.** The graph builder *imports your package to
analyze it* — so the checker runs inside the project's virtualenv, with
the package installed (`pip install -e .`). Run it outside that
environment and it fails — or worse, analyzes a stale installed copy
rather than your working tree. The related trap is the analyzer's cache:
excellent for speed, misleading mid-refactor. When violations don't match
what the import statements plainly say, delete the cache before doubting
your eyes.

**Wildcard semantics.** In raw import-linter patterns, `mypkg.*` matches
one level only — `mypkg.foo` but *not* `mypkg.foo.bar`. Meanwhile the
assembler's component-name wildcards (`core-*`) expand across component
names before contracts are generated, with no such limit. Two wildcard
systems, different rules; mixing them in one rule produces contracts that
check less than they appear to. When a contract seems to pass suspiciously
easily, this is the first thing to check.

## Living with it

Day to day, the contract checker is a quiet teammate: it runs in
pre-commit and CI, says nothing while the graph is clean, and blocks the
one commit that would have welded billing to the inside of inventory. When
it does block you, the violation message carries the rule's *why* — the
design decision you just bumped into. The correct responses are the same
as in any governed codebase: route through the public sub-package, or
challenge the rule in review. The response that defeats the whole
mechanism is the workaround import — dynamic loading, a re-export shim —
that satisfies the letter of the contract while smuggling the dependency
anyway. The graph the checker sees should *be* the architecture, not a
sanitized version of it.

And when you create a new package: its `architecture.toml` goes in the
same change, before the implementation grows dependencies nobody chose.

---

*The stack-agnostic pattern — file schema, rule placement, assembler
design, audit checklist — is defined in the
[architecture-as-code concept](READ-architecture-as-code.md); the
JavaScript counterpart is
[architecture-as-code-javascript](READ-architecture-as-code-javascript.md).
The full operational reference — assembler code, contract types, and
gotchas — lives in
[SKILL.md](../.claude/skills/architecture-as-code-python/SKILL.md).*
