# Architecture-as-Code — Python

> **Prerequisite.** Read
> [`architecture-as-code`](./READ-architecture-as-code.md) first — it
> defines the universal pattern (schema, rule placement, anti-patterns,
> "why this works"). This primer documents the Python implementation:
> per-package `architecture.toml` files merged into an `import-linter`
> config and enforced by `lint-imports`.

## How to use

1. **Decide your architecture.** Identify packages, sub-tiers, and allowed
   dependency edges. (Pattern primer covers the universals.)
2. **Drop an `architecture.toml` next to each package that needs rules.**
   Most packages don't need their own file — they're declared once higher
   up.
3. **Prompt the AI.** Describe the architecture; the skill generates the
   matching TOML files.

   > *"Set up architecture-as-code-python: `mypkg.core` is a package with
   > internal tiers `tier1 < tier2 < tier3`; only `mypkg.orchestrator` may
   > import the core facade `mypkg.core.api`."*

4. **Run the assembler.** Violations print their `why`.

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

## Python-specific notes

- **Facade is a sub-package, not a single file.** Python's idiomatic facade
  exposes public API via `__init__.py` + `__all__`. The JS "single file as
  facade" pattern maps awkwardly; prefer a public sub-package
  (`mypkg.core.api`) plus forbidden edges banning imports to the internal
  sub-packages.
- **Pattern syntax is dotted module paths**, not filesystem globs.
  Descendants are matched automatically; `single = true` matches only the
  exact module.
- **Specialized contracts.** For sibling-isolation the assembler emits an
  `independence` contract; for strict tier ordering, an optional `layers`
  contract.
- **Generated `.importlinter` is a build artifact.** Git-ignored alongside
  `.import_linter_cache/`. Source of truth is the per-package
  `architecture.toml`s.

## Known gotchas

- **Dynamic imports bypass enforcement.** `importlib.import_module(...)`
  and `__import__` don't appear in the static graph. Mark plugin
  entry-points as `single = true` and ban dynamic imports elsewhere.
- **Root package must be importable.** `pip install -e .` (or equivalent)
  needs to have run in the active venv before the assembler walks the
  graph.
- **Cache staleness during refactors.** Delete `.import_linter_cache/` if
  results stop matching what your `import` statements actually say.
- **`mypkg.*` is single-segment** in raw import-linter patterns. The
  pattern's `core-*` (multi-match) is the assembler's domain; don't mix
  the two in a single rule.

## Next steps

- See [SKILL.md](../.claude/skills/architecture-as-code-python/SKILL.md)
  for the full assembler code, advanced features (captures, parametric
  rules), and Python-specific gotchas.
- For the universal pattern, see
  [READ-architecture-as-code](./READ-architecture-as-code.md).
- For first principles on what goes inside a package, see
  [`architecture-guidelines`](../.claude/skills/architecture-guidelines/).
