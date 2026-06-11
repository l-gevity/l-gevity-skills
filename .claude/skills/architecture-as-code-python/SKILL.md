---
name: architecture-as-code-python
description: >-
    Python implementation of the `architecture-as-code` pattern. Per-package
    `architecture.toml` files merged into a single `import-linter` config and
    enforced via `lint-imports` (over a Grimp-built import graph). TRIGGER
    when: implementing or extending architecture-as-code in a Python repo,
    debugging an `import-linter` contract, or adapting the assembler. SKIP
    for routine edits inside a governed package. Reads in conjunction with
    `architecture-as-code` (the pattern, source of truth for schema, rule
    placement, anti-patterns, and audit checklist) — this skill defines only
    the Python-specific encoding, assembler code, and gotchas.
---

# Architecture-as-Code — Python Implementation

> **Prerequisite.** Read [`architecture-as-code`](../architecture-as-code/)
> first. The schema (§1), components (§2), forbidden edges (§3), rule
> placement (§4), assembler concept (§5), and anti-patterns / audit (§6) are
> defined there and apply identically here. This file documents only what is
> Python-specific.

## 1. File format

- Filename: `architecture.toml`. Plain TOML — no Python code, no imports.
- TOML arrays-of-tables: `[[components]]`, `[[forbidden]]`.
- Pattern syntax: dotted module paths (`mypkg.core.tier1`). The package and
  all submodules match by default; set `single = true` to match only the
  exact module.
- Component patterns may overlap (e.g. `mypkg.core` and `mypkg.core.tier1`
  both match files under `mypkg/core/tier1/`). That's fine — import-linter
  checks each contract independently; there's no first-match-wins.

```toml
# architecture.toml — example for a package with internal layering
[[components]]
name = "core-facade"
pattern = "mypkg.core.api"           # public sub-package = the facade

[[components]]
name = "core-tier1"
pattern = "mypkg.core.tier1"

[[components]]
name = "core-tier3"
pattern = "mypkg.core.tier3"

[[components]]
name = "core-other"
pattern = "mypkg.core"               # whole-package catch-all, last

[[forbidden]]
# Efferent — self-knowledge, lives in own file.
from = "core-*"
to = "*"
except_to = ["core-*"]
why = "Core purity: no imports outside the core package."

[[forbidden]]
# Internal layering.
from = "core-tier3"
to = "core-tier1"
why = "Tier 3 must go through tier 2."
```

Parametric "not equal" syntax for cross-domain isolation:
`!{from.captured.domain}` (single braces).

> [!NOTE] **Facade pattern in Python.** Python's idiomatic facade is a
> sub-package (e.g. `mypkg.core.api`) exposing public API via `__init__.py`
> and `__all__`. The "single file as facade" pattern from the JS skill maps
> awkwardly here; prefer a public sub-package plus forbidden edges that ban
> imports to the internal sub-packages.

## 2. Specialized contract types

The assembler emits `forbidden` contracts by default. For two common shapes
import-linter offers more specific contract types that produce cleaner
violations:

- **Sibling-isolation across N components** → one `independence` contract
  listing the N module patterns.
- **Strict tier ordering** (e.g. `tier1 < tier2 < tier3`, where higher tiers
  may import lower) → a `layers` contract. Optional — explicit `[[forbidden]]`
  edges between specific tiers also work.

## 3. Assembler

A small Python script invoked by pre-commit and CI. Discovers all
`architecture.toml` files, merges them, generates a `.importlinter` config in
INI form, and invokes `lint-imports`.

**Why generate `.importlinter` rather than mutate `pyproject.toml`?**
The generated file is a build artifact (gitignored alongside
`.import_linter_cache/`); the source of truth is the per-package
`architecture.toml`s. import-linter natively reads `.importlinter` ahead of
`pyproject.toml`.

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

## 4. Output Contract

When applying this implementation, emit:

```
Scope:          <repo / package / module path>
Decision:       Add architecture.toml | Update assembler | Update import-linter config | Blocked
Generated config:<path, if any>
Contracts changed:<forbidden / layers / independence contracts>
Verification:   <lint-imports command / assembler command / Not run + reason>
Next action:    <specific file edit, package install, cache clear, or unresolved question>
```

## 5. Python-specific gotchas

> [!NOTE] **Dynamic imports bypass enforcement.** import-linter reads static
> `import` and `from ... import` statements via Grimp. Imports through
> `importlib.import_module(...)`, `__import__`, or string-based dispatch
> don't appear in the graph. If a package uses dynamic imports for plugin
> loading, mark the entry-point as a single-module component
> (`single = true`) so its rules are explicit, and consider banning the
> dynamic style elsewhere.

> [!NOTE] **import-linter `*` is single-segment.** In `forbidden_modules` and
> similar fields, `mypkg.*` matches `mypkg.foo` but **not** `mypkg.foo.bar`.
> The pattern's prefix wildcards (`core-*`) operate on *component names* and
> are expanded by the assembler before contracts are emitted, so they don't
> hit this limit. But if you write raw module patterns yourself, mind the
> difference.

> [!NOTE] **Cache staleness during refactors.** `.import_linter_cache/`
> speeds up subsequent runs but can mislead during heavy refactors. Delete
> it if results don't match what your import statements actually say.

> [!NOTE] **Root package must be importable.** import-linter imports the
> root package to walk it. Make sure `pip install -e .` (or equivalent) has
> been run in the active venv before invoking the assembler.

> [!NOTE] **Mixing pattern-level and component-level wildcards.** A single
> rule that uses both `mypkg.*` (single-segment, import-linter native) and
> `core-*` (multi-match, assembler-expanded) will surprise you. Component-
> name wildcards are the assembler's domain; raw `*` in import-linter
> patterns is single-segment only. Don't mix in one rule.
