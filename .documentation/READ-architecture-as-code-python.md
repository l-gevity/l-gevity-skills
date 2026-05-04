# Architecture-as-Code (Python)

A build step that enforces your architectural rules in Python. You declare which packages may import from which via per-package `architecture.toml` files; an assembler turns them into `import-linter` contracts and the build fails on violations.

## Why use this

- **Architectural violations are caught at lint time**, not weeks later in review or production.
- **Rules live next to the code they govern.** Each package ships its own `architecture.toml`; rules accumulate from the root down.
- **A package knows itself, not its context.** Internal layering and outbound imports live in the package; "who may import me" lives one level up — the composition lives where the composing happens.
- **Refactors stay local.** Prefix wildcards (`core-*`) mean renames don't ripple through every consumer's rule file.
- **Drift becomes impossible.** The check runs in pre-commit and CI; new edges fail the build with a plain-English `why`.

## Fundamental principles

Python's import system offers no resistance to bad connections — any module can import any other with a single line. Architecture-as-code makes the dependency graph an enforced artifact instead of a wiki page nobody reads.

- **Package = directory** (with `__init__.py`) or a single `.py` module. Components are dotted module paths; descendants are matched automatically.
- **One optional file per package** — plain TOML, no Python code, no imports.
- **Self-knowledge stays local.** A package's own file may name only its `<own-prefix>-*` components and the anonymous `*`. Naming any other component is itself a violation.
- **Composition lives at the composer.** Cross-package rules ("orchestrator may import the facade", "siblings stay isolated") live one level up, where the parts are composed.
- **Recursion via discovery.** The assembler walks the tree, merges files, and emits one `.importlinter` config — a build artifact, not a checked-in source.

## How to use

1. **Decide your architecture.** Identify packages, sub-tiers, and the allowed dependency edges.
2. **Drop an `architecture.toml` next to each package that needs rules.** Most packages don't need their own file — they're declared once higher up.
3. **Prompt the AI.** Describe the architecture; the skill generates the matching TOML files.

   > *"Set up architecture-as-code-python: `mypkg.core` is a package with internal tiers `tier1 < tier2 < tier3`; only `mypkg.orchestrator` may import the core facade `mypkg.core.api`."*

4. **Run the assembler.** Violations print their `why`. Fix and commit.

   ```bash
   pip install import-linter
   python tools/arch_lint.py
   ```

## Minimal example

```toml
# mypkg/core/architecture.toml — package's own file
[[components]]
name = "core-facade"
pattern = "mypkg.core.api"

[[components]]
name = "core-tier1"
pattern = "mypkg.core.tier1"

[[components]]
name = "core-other"
pattern = "mypkg.core"            # whole-package catch-all, last

[[forbidden]]
from = "core-tier3"
to   = "core-tier1"
why  = "Tier 3 must go through tier 2; direct tier-1 access is forbidden."
```

```toml
# mypkg/architecture.toml — composer level
[[forbidden]]
from   = "*"
except = ["orchestrator", "core-*"]
to     = "core-facade"
why    = "Only the orchestrator may import the core facade."
```

## Where each rule lives

| Rule type                              | Lives in                  |
|----------------------------------------|---------------------------|
| Afferent ("who may import me?")        | Higher level (composer).  |
| Efferent ("what may I import?")        | Own file.                 |
| Cross-package sibling-isolation        | Higher level (composer).  |
| Internal layering                      | Own file.                 |
| Sub-tier sibling-isolation             | Own file.                 |

## Known gotchas

- **Dynamic imports bypass enforcement.** `importlib.import_module(...)` and `__import__` don't appear in the static graph. Mark plugin entry-points as `single = true` and ban dynamic imports elsewhere.
- **Root package must be importable.** `pip install -e .` (or equivalent) needs to have run in the active venv before the assembler walks the graph.
- **Cache staleness during refactors.** Delete `.import_linter_cache/` if results stop matching what your `import` statements actually say.

## When to skip

Tiny packages, scratch scripts, throwaway tooling. Otherwise the cost is one TOML file plus a pre-commit hook, and it pays off the first time someone tries to import your storage layer from a UI handler.

## Next steps

- See [SKILL.md](./SKILL.md) for the full reference (file schema, parametric rules, assembler internals, anti-patterns, pre-merge audit).
- For first principles on what goes inside a package, see [`architecture-guidelines`](../architecture-guidelines/).
- For the spatial rationale behind layered/sibling rules, see [`geometric-architecture`](../geometric-architecture/).
- For the JavaScript/TypeScript counterpart, see [`architecture-as-code-javascript`](../architecture-as-code-javascript/).
