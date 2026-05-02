---
name: architecture-as-code-python
description: 
    Pluggable mechanism for declaring and enforcing component boundaries
    via TOML files in the source tree of a Python project. Every package
    lives in a directory with `__init__.py` (or a single `.py` module)
    and MAY ship an `architecture.toml` declaring its components and
    rules. Files merge recursively: rules from higher levels accumulate.
    A small assembler discovers them, generates an `import-linter`
    config, and invokes `lint-imports`. Use when: adding a package,
    splitting one, expressing a new dependency rule, debugging a
    forbidden edge, or extending the assembler. SKIP for routine edits
    inside a governed package. See `architecture-guidelines` for first
    principles, `geometric-architecture` for spatial rationale,
    `import-linter-fix-protocol` for daily workflow.
---

# Architecture-as-Code-Python

> **Scope.** Describes the file format, discovery, and assembly that
> turn the package tree into an enforced dependency graph. Runs as
> `import-linter` (over a Grimp-built import graph) — no
> `import-linter`, no enforcement. Operates on Python source (`.py`,
> `.pyi`, package `__init__.py`). Does NOT prescribe what the graph
> should look like — that's `architecture-guidelines` and
> `geometric-architecture`. Does NOT govern code style — that's
> `coding-standard`.

> **TL;DR / Core Directives**
>
> 1. **Package = directory** (with `__init__.py`), or a single `.py`
>    module. A module belongs to a component because its dotted path
>    matches a `pattern`. Patterns are dotted module paths;
>    **descendants are included automatically** (import-linter default).
> 2. **One optional file per package** — `architecture.toml`. Plain
>    TOML; no Python code, no imports. The repo root has one too — same
>    structure.
> 3. **A package knows itself, not its context.** Its own file governs
>    internals (sub-tiers, layering) and outbound dependencies ("what I
>    import") — never inbound ones ("who imports me") or its place in
>    the wider system, which it does not and should not know.
>    Mechanically: only `<own-prefix>-*`, specific `<own-prefix>-x`
>    names, and the anonymous `*` may appear; any other component name
>    is a violation.
> 4. **Composition lives on the level that does the composing.**
>    Constraints between a package and the system (afferent — "who may
>    import me" — and cross-package sibling-isolation) live higher up.
>    Constraints among a package's own sub-tiers (internal layering,
>    sub-tier sibling-isolation) live in its own file. Efferent rules
>    ("what may I import") are self-knowledge — own file. Higher-level
>    rules accumulate.
> 5. **Every package with rules ends with a catch-all bucket.** The
>    anonymous `*` wildcard expands to **registered** components only;
>    code under unregistered paths isn't covered. Add a `<pkg>` entry
>    that captures the whole package as the last `[[components]]` row.
> 6. **Recursion via discovery.** The assembler walks the tree; deeper
>    files are discovered first.

---

## 1. File schema

Each `architecture.toml` declares two optional top-level arrays:

```toml
[[components]]
# one entry per component

[[forbidden]]
# one entry per dependency edge
```

Most packages don't need their own file — they're declared once in the
`[[components]]` list higher up in the tree.

> [!NOTE]
> `<own-prefix>` is the shared prefix of a package's component names —
> e.g. `core-` for `core-facade`, `core-tier1`, `core-other`.
> Single-component packages (e.g. `service`) just use the bare name.

## 2. Components — packages declared as module patterns

| Field        | Required | Purpose                                                              |
| ------------ | -------- | -------------------------------------------------------------------- |
| `name`       | yes      | Component id referenced from `[[forbidden]]` edges.                  |
| `pattern`    | yes      | Module path, e.g. `mypkg.core.tier1`. The package and all submodules are matched. |
| `single`     | no       | `true` to match **only** the listed module, not its descendants. Emits contracts with `as_packages = false`. |
| `capture`    | no       | Path-segment captures, e.g. `["domain"]`, for parametric rules. Used by the assembler, not import-linter. |

Component patterns may overlap (e.g. `mypkg.core` and `mypkg.core.tier1`
both match files under `mypkg/core/tier1/`). That's fine —
import-linter checks each contract independently against the import
graph; there's no first-match-wins resolution.

```toml
# A package's own architecture.toml. Each entry maps to a Python module path.
[[components]]
name = "core-facade"
pattern = "mypkg.core.api"           # public sub-package = the facade

[[components]]
name = "core-tier1"
pattern = "mypkg.core.tier1"

# ...narrower buckets

[[components]]
name = "core-other"
pattern = "mypkg.core"               # catch-all (whole package), last
```

> [!NOTE]
> **Facade pattern in Python.** Python's idiomatic facade is a
> sub-package (e.g. `mypkg.core.api`) exposing public API via
> `__init__.py` and `__all__`. The "single file as facade" pattern from
> the JS skill maps awkwardly here; prefer a public sub-package plus
> forbidden edges that ban imports to the internal sub-packages.

## 3. Forbidden — dependency edges

```toml
[[forbidden]]
from = "..."         # spec
to   = "..."         # spec
except    = ["..."]  # optional
except_to = ["..."]  # optional
why  = "..."         # message
```

| `from` / `to` accepts | Meaning                                                  |
| --------------------- | -------------------------------------------------------- |
| `"service"`           | Single component name.                                   |
| `["app", "service"]`  | Multiple component names.                                |
| `"*"`                 | Every registered component.                              |
| `"core-*"`            | Prefix wildcard — every component starting with `core-`. |
| `{ captured = ... }`  | Parametric (uses captures from a `capture`-enabled component). |

`except` subtracts from a wildcard `from`; `except_to` from a wildcard
`to`. Strings in either may be prefix wildcards. `why` is the violation
message.

The assembler emits `forbidden` contracts for these edges. For two
common shapes, it can use more specific contract types (cleaner
output):

- **Sibling-isolation across N components** → emits one `independence`
  contract listing the N module patterns.
- **Strict tier ordering** (e.g. tier1 < tier2 < tier3, where higher
  tiers may import lower) → can be expressed as a `layers` contract.
  This is optional; explicit `[[forbidden]]` edges between specific
  tiers also work.

### Examples

```toml
# Afferent — higher level. Only the orchestrator may import the facade.
[[forbidden]]
from = "*"
except = ["orchestrator", "core-*"]
to = "core-facade"
why = "Only the orchestrator may import the core facade."

# Efferent — own file. Self-contained.
[[forbidden]]
from = "core-*"
to = "*"
except_to = ["core-*"]
why = "Core purity: no imports outside the core package."

# Internal layering — own file. Sub-tier names share the prefix.
[[forbidden]]
from = "core-tier3"
to = "core-tier1"
why = "Tier 3 must go through tier 2; direct tier-1 access is forbidden."

# Parametric — higher level. Sibling sub-domains may not import each other.
# (Assembler emits an `independence` contract over all matched domains.)
[[forbidden]]
from = { type = "domain-handler", captured = { domain = "*" } }
to   = { type = "domain-handler", captured = { domain = "!{from.captured.domain}" } }
why  = "Cross-domain import: extract shared helpers to a sibling shared/ package."
```

`!{from.captured.domain}` is the assembler's "not equal to the captured
value" syntax — fires when the two `domain` captures differ.

## 4. Where each rule lives

| Rule type                              | Lives in                  |
| -------------------------------------- | ------------------------- |
| Afferent ("who may import me?")        | Higher level (composer).  |
| Efferent ("what may I import?")        | Own file.                 |
| Cross-package sibling-isolation        | Higher level (composer).  |
| Internal layering                      | Own file.                 |
| Sub-tier sibling-isolation             | Own file.                 |

Higher-level rules accumulate. Place each rule where the composition
it expresses lives — sub-tier sibling-isolation in the package's own
file (it composes its sub-tiers); encapsulation between the package
and the system higher up (where the package is composed with peers).

> [!IMPORTANT]
> A package's own file MUST reference only its own-prefix names
> (`<own-prefix>-*` or `<own-prefix>-x`) and `*`. Naming any other
> component is a violation — that knowledge belongs higher up.

---

## 5. The assembler

A small Python script invoked by pre-commit and CI. Discovers all
`architecture.toml` files, merges them, generates a `.importlinter`
config in INI form, and invokes `lint-imports`.

**Why generate `.importlinter` rather than mutate `pyproject.toml`?**
The generated file is a build artifact (gitignored alongside
`.import_linter_cache/`); the source of truth is the per-package
`architecture.toml`s. import-linter natively reads `.importlinter`
ahead of `pyproject.toml`.

```python
# tools/arch_lint.py
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT_PACKAGE = "mypkg"          # set this for your project
GENERATED_CONFIG = Path(".importlinter")

# 1. Discover — recursive walk, skipping the configured ignore-list
#    (.venv, dist, build, .tox, __pycache__, .import_linter_cache).
arch_files = sorted(
    Path(".").rglob("architecture.toml"),
    key=lambda p: -len(p.parts),  # deeper-first
)

# 2. Concat
components, forbidden = [], []
for f in arch_files:
    data = tomllib.loads(f.read_text(encoding="utf-8"))
    components.extend(data.get("components", []))
    forbidden.extend(data.get("forbidden", []))

# 3. Expand wildcards against the live registry.
#    Turn a spec ('foo' | 'foo-*' | '*' | list[str] | parametric dict)
#    into a list of component names, with `except` subtracted.
names = [c["name"] for c in components]

def expand(spec, except_=None):
    if isinstance(spec, dict):
        return spec  # parametric — handled separately
    items = spec if isinstance(spec, list) else [spec]
    def resolve(lst):
        out = []
        for t in lst:
            if t == "*":
                out.extend(names)
            elif t.endswith("*"):
                p = t[:-1]
                out.extend(n for n in names if n.startswith(p))
            else:
                out.append(t)
        return out
    types = resolve(items)
    if except_:
        sub = set(resolve(except_))
        types = [t for t in types if t not in sub]
    return types

# 4. Emit import-linter contracts (INI format).
component_pattern = {c["name"]: c["pattern"] for c in components}
component_single  = {c["name"]: c.get("single", False) for c in components}

ini = ["[importlinter]", f"root_package = {ROOT_PACKAGE}", ""]
for i, edge in enumerate(forbidden):
    src = expand(edge["from"], edge.get("except"))
    dst = expand(edge["to"],   edge.get("except_to"))
    if not src or not dst:
        continue   # nothing to forbid after exceptions

    src_modules = [component_pattern[n] for n in src]
    dst_modules = [component_pattern[n] for n in dst]
    as_packages = not any(component_single[n] for n in src + dst)

    ini.append(f"[importlinter:contract:{i}]")
    ini.append(f"name = {edge['why'][:80]}")
    ini.append("type = forbidden")
    ini.append("source_modules =")
    ini.extend(f"    {m}" for m in src_modules)
    ini.append("forbidden_modules =")
    ini.extend(f"    {m}" for m in dst_modules)
    if not as_packages:
        ini.append("as_packages = False")
    ini.append("")

GENERATED_CONFIG.write_text("\n".join(ini), encoding="utf-8")

# 5. Invoke lint-imports
result = subprocess.run(
    ["lint-imports", "--config", str(GENERATED_CONFIG)],
    check=False,
)
sys.exit(result.returncode)
```

**Install & run:**

```bash
pip install import-linter      # pulls in grimp; tomli on Python <3.11
python tools/arch_lint.py      # discover + assemble + lint
```

**Pre-commit hook:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: arch-lint
        name: "Architecture lint"
        entry: "python tools/arch_lint.py"
        language: system
        pass_filenames: false
```

`language: system` is required — `lint-imports` must run inside the
project's virtualenv to import the analyzed packages.

**Gitignore:**

```
.importlinter            # generated by tools/arch_lint.py
.import_linter_cache/    # import-linter's own cache
```

### Known gotchas

> [!NOTE]
> **Dynamic imports bypass enforcement.** import-linter reads static
> `import` and `from ... import` statements via Grimp. Imports through
> `importlib.import_module(...)`, `__import__`, or string-based
> dispatch don't appear in the graph. If a package uses dynamic imports
> for plugin loading, mark the entry-point as a single-module component
> (`single = true`) so its rules are explicit, and consider banning the
> dynamic style elsewhere.

> [!NOTE]
> **import-linter `*` is single-segment.** In `forbidden_modules` and
> similar fields, `mypkg.*` matches `mypkg.foo` but **not**
> `mypkg.foo.bar`. The skill's prefix wildcards (`core-*`) operate on
> *component names* and are expanded by the assembler before contracts
> are emitted, so they don't hit this limit. But if you write raw
> module patterns yourself, mind the difference.

> [!NOTE]
> **Cache staleness during refactors.** `.import_linter_cache/` speeds
> up subsequent runs but can mislead during heavy refactors. Delete it
> if results don't match what your import statements actually say.

> [!NOTE]
> **Root package must be importable.** import-linter imports the root
> package to walk it. Make sure `pip install -e .` (or equivalent)
> has been run in the active venv before invoking the assembler.

---

## 6. Recipes

| To do                              | Where                                                                                   |
| ---------------------------------- | --------------------------------------------------------------------------------------- |
| Add a new package                  | One `[[components]]` entry where the package is composed (usually root).                |
| Add a dependency rule              | One `[[forbidden]]` entry higher than the components it constrains.                     |
| Package with internal layering     | Create the package's own `architecture.toml`; declare sub-modules; layer with `<own-prefix>-*` or specific `<own-prefix>-x` names. |
| Sibling-isolation                  | At the composer's level: `capture` on the parent component, parametric `from`/`to`. Assembler emits an `independence` contract.    |
| Strict tier ordering               | Same level: layers can be expressed as one `[[forbidden]]` per blocked direction, or by switching the emitted contract type to `layers` (advanced). |

## 7. Anti-patterns + pre-merge audit

| Anti-pattern                                              | Fix                                                              |
| --------------------------------------------------------- | ---------------------------------------------------------------- |
| A package's own file names another component.             | Move higher, or rewrite with `<own-prefix>-*` + `*`.             |
| Hardcoded list of "all other components".                 | Use `"*"` + `except` / `except_to`.                              |
| Renaming a component without updating consumers.          | Use prefix wildcards (`<prefix>-*`) so renames stay local.       |
| Package has rules but no catch-all bucket.                | Add a `<pkg>` (whole-package) entry as the last `[[components]]`. |
| Dynamic imports used to evade forbidden edges.            | Refactor to static imports, or accept the loophole and document it. |
| Mixing module-segment `*` with component-name `core-*`.   | Component-name wildcards are the assembler's; raw `*` in import-linter patterns is single-segment only. Don't mix in one rule. |

Before merge:

- [ ] No other-component name appears in any package's own
      `architecture.toml`.
- [ ] `[[components]]` lists the whole-package catch-all entry for any
      package being constrained.
- [ ] `python tools/arch_lint.py` violation count matches baseline (or
      new violations reflect intentional changes).

> [!NOTE]
> The "no other-component name" check is mechanical — a small TOML
> walk over each `architecture.toml` could enforce it as a meta-lint.
> Until then, the manual checklist is the gate.
