# Boundary Enforcement in JavaScript: What the Linter Can See

Suppose your team has decided that production code may never import test
helpers, and that only the orchestrator may touch the core module's
internals. In a JavaScript or TypeScript repo, those decisions can be
enforced — automatically, on every commit, in the editor as you type. This
document explains how that enforcement actually works in the JS ecosystem,
and — just as important — the specific ways it can silently *not* work.

It assumes you've read the
[architecture-as-code concept](READ-architecture-as-code.md): rules live in
small per-module files, an assembler merges them, a linter enforces the
merged result. Here we cover the JavaScript half: what the tooling really
does under the hood.

## The mechanism: ESLint sees the import graph

ESLint normally checks code one file at a time — style, syntax, suspicious
patterns. But every `import` statement names a path, and a resolver can
turn that path into a concrete file. That's enough to reconstruct the
**import graph**: which file depends on which. Boundary plugins (the
established one is `eslint-plugin-boundaries`) build on exactly this:

1. **Classification.** Glob patterns map files to named components:
   everything under `packages/core/tier1/**` is `core-tier1`;
   `packages/core/index.js` alone is the `core-facade`.
2. **Rules over pairs.** Each rule forbids edges between components:
   *`core-*` may import nothing outside `core-*`*; *nobody but the
   orchestrator may import `core-facade`*. Every rule carries a message
   explaining *why* — that message is what a developer sees at the moment
   they type the forbidden import, which makes it the architecture's most
   effective documentation.
3. **Evaluation per import.** For every import in every file, the plugin
   resolves the target, classifies both ends, and checks the pair against
   the rules. A match on a forbidden edge is a lint error, in the editor
   and in CI.

The per-module rule files (`eslint.architecture.mjs` — one per governed
directory, declaring only that module's own components and outbound rules)
are merged by a small assembler script at lint startup into one ESLint
flat-config. The merged config is a throwaway build artifact; the
per-module files are the source of truth, versioned next to the code they
govern.

## The four ways enforcement silently fails

Here's the part worth internalizing even if you never touch the config,
because all four failures produce the same dangerous symptom: **a green
lint run that isn't checking what you think it checks.**

**1. Unresolved imports are invisible.** The plugin can only judge an
import it can resolve to a file. An import path the resolver doesn't
understand — a host-served absolute path like `/js/app.js`, an exotic
alias, a bundler-specific scheme — resolves to nothing, gets classified as
nothing, and passes every rule *silently*. The fix is configuring the
resolver (e.g. an alias resolver mapping `/js` to its real directory) so
every real dependency is visible. The test: if you can't jump-to-definition
through an import, the linter probably can't follow it either.

**2. Unmatched files are invisible.** A file that matches no component
pattern doesn't exist as far as the rules are concerned — imports from it
and to it are unjudged. This is why every governed module's component list
must end with a catch-all pattern (`packages/core/**`, last, after the
narrower patterns): it sweeps every file into *some* component, so nothing
sits outside the law. Patterns are matched in order, narrowest first —
the facade's exact file path before tier directories before the catch-all
— so each file lands in its most specific classification.

Two caveats on that catch-all, both learned expensively. It belongs *inside*
a module, where the parts sit at one depth. At the repository root the same
`**` matches at the shallowest folder and steals files from the specific
components below it, whatever its position in the list — so the root's loose
files get declared individually, as exact file paths. And a catch-all only
makes a file *classified*; to make an unclassified file *fail*, switch on the
plugin's unknown-file rule. That rule is also the only one that can flag a
file with no imports at all — a dependency rule needs an edge to judge, and
such a file has none.

**3. Unlinted files are invisible — and this one hides in the config.** The
others are gaps in what the plugin can *see*; this is a gap in where it is
*pointed*. The boundaries rule lives in a flat-config block with a `files`
glob, and that glob is a second gate, independent of every component pattern:
a file outside it is never handed to the rule. A scope that started as
`packages/**` and grew into a hand-kept list of directories will eventually
miss a new one, and the lint output won't change by a character — the count
stays at zero because the rule was never asked. Point the block at the whole
tree and keep real exclusions in the config's shared ignore list, where they
are one visible list rather than an omission.

**4. Computed dynamic imports are invisible.** `import('./' + name)` can't
be resolved statically — the target is decided at runtime, so the boundary
plugin can't see the edge at all. One computed import can smuggle any
dependency past every rule. The countermeasure is a companion lint rule
that forbids non-literal dynamic import paths outright:
`import('./known-module.js')` is fine; variables, concatenation, and
template strings in an import are themselves the lint error. This isn't
pedantry — it's closing the one door the whole enforcement scheme can't
watch.

The principle behind the first and fourth: **static enforcement
governs only the statically analyzable.** Every convenience that makes imports
more "dynamic" trades away the ability to check them. The principle behind
the second and third is harsher: **the tool's silence is not a result.** A
count of zero means the same thing whether the boundary held or was never
examined, so coverage has to be proven with a positive signal, never inferred
from a green check.

## Ecosystem idioms worth knowing

- **Facade as a single file.** JavaScript's natural public-API idiom is an
  index/entry file. Declaring it as a single-file component (exact path,
  `mode: 'file'`, no glob) lets rules like "outsiders may import the
  facade and nothing else in the module" match precisely.
- **Test/production separation.** Declare test files
  (`src/**/*.test.ts`, `test/**`) as their own components *before* the
  production catch-all, then forbid the production component from
  importing them. One direction only: tests may import production code;
  production importing test code is the bug.
- **`.mjs` for the rule files.** The architecture files are ES modules the
  assembler `import()`s at startup. Naming them `.js` gets them
  misclassified as application source by discovery walkers and by ESLint
  itself; the `.mjs` extension keeps them out of their own jurisdiction.
- **Warnings during migration, errors after.** A newly-introduced rule on
  an old codebase surfaces existing violations. Run it at `warn` while
  the backlog clears, then promote to `error` — an error nobody can merge
  past is the end state; a permanent warning is theatre.

## The habit

When working in a repo governed this way, two reflexes serve you. When the
linter blocks an import, read the `why` message before reaching for a
workaround — the rule is a design decision talking to you, and the correct
responses are "route through the public interface" or "challenge the rule
in review", never "find a path the resolver can't see." And when you *add*
a module, add its architecture file in the same change — a component the
rules don't know is not exempt so much as invisible, which is worse.

---

*The stack-agnostic pattern — file schema, rule placement, assembler
design, audit checklist — is defined in the
[architecture-as-code concept](READ-architecture-as-code.md); the Python
counterpart is
[architecture-as-code-python](READ-architecture-as-code-python.md). The
full operational reference — assembler code, recipes, and gotchas — lives
in
[SKILL.md](../.claude/skills/architecture-as-code-javascript/SKILL.md).*
