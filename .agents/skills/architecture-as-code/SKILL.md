---
name: architecture-as-code
description: >-
    Stack-agnostic pattern for declaring and enforcing component boundaries via
    per-module config files merged into a single ruleset and lint-enforced.
    Every module lives in a directory and MAY ship an architecture config
    declaring its components and forbidden dependency edges. Files merge
    recursively: rules from higher levels accumulate. A small assembler
    discovers them and emits a single config for the stack's import-graph
    linter. TRIGGER when: designing or auditing a dependency-rule enforcement
    mechanism, deciding what a per-module file should and shouldn't say,
    placing a new rule, debugging a forbidden edge, or extending the assembler.
    SKIP for routine edits inside a governed module. Defines the pattern; for
    a concrete implementation see `architecture-as-code-javascript` (ESLint +
    `eslint-plugin-boundaries`) or `architecture-as-code-python` (import-linter
    + Grimp). See `architecture-guidelines` for first principles and
    `geometric-architecture` for the spatial rationale this enforces.
---

# Architecture-as-Code (Pattern)

> **Scope.** Stack-agnostic pattern: file format, discovery, assembly, and
> rule-placement discipline that turn a directory tree into an enforced
> dependency graph. Implementation is delegated to a per-stack linter (e.g.
> `eslint-plugin-boundaries` for JS, `import-linter` for Python). Does NOT
> prescribe what the graph should look like — that's `architecture-guidelines`
> and `geometric-architecture`. Does NOT govern code style — that's your
> project's coding-style convention.

> **Core Directives**
>
> 1. **Module = directory** (or a single-file unit for a facade). Files belong
>    to a module by living under its path / dotted path.
> 2. **One optional config file per module** — declaratively lists this
>    module's components and its outbound rules. Repo root has one too, same
>    structure.
> 3. **A module knows itself, not its context.** Its own file governs
>    internals (sub-tiers, layering) and outbound dependencies ("what I
>    import") — never inbound ("who imports me") or its place in the wider
>    system, which it does not and should not know. Mechanically: only
>    `<own-prefix>-*`, specific `<own-prefix>-x` names, and the anonymous `*`
>    may appear; any other module name is a violation.
> 4. **Composition lives on the level that does the composing.** Constraints
>    between a module and its peers (afferent — "who may import me" — and
>    cross-module sibling-isolation) live higher up. Constraints among a
>    module's own sub-tiers (internal layering, sub-tier sibling-isolation)
>    live in its own file. Higher-level rules accumulate.
> 5. **Every module with rules ends with a catch-all bucket.** Files matching
>    no component are invisible to the linter and silently bypass forbidden
>    edges. A `<dir>/**` (or whole-package) entry MUST be last in
>    `components`.
> 6. **Recursion via discovery.** Assembler walks the tree; deeper files are
>    processed first.

---

## 1. File schema

Each architecture config declares two optional top-level arrays:

```
components: [ ... ]   # one entry per module
forbidden:  [ ... ]   # one entry per dependency edge
```

Concrete encoding (`.mjs`, `.toml`, `.yaml`, …) is stack-specific. Schema is
not. Most modules don't need their own file — they're declared once in the
`components` list higher up in the tree.

> [!NOTE] `<own-prefix>` is the shared prefix of a module's component names
> — e.g. `core-` for `core-facade`, `core-tier1`, `core-other`.
> Single-component modules just use the bare name.

## 2. Components — modules declared as patterns

| Field     | Required | Purpose                                                      |
| --------- | -------- | ------------------------------------------------------------ |
| `name`    | yes      | Module id referenced from `forbidden` edges.                 |
| `pattern` | yes      | Selector for the module's files (stack-specific syntax).     |
| `mode` / `single` | no | Marks a single-file or single-module unit (e.g. a facade). |
| `capture` | no       | Path-segment captures for parametric rules.                  |

Order matters within a file: narrowest first (file-mode → sub-directories →
catch-all). Across files: deeper-first (so a module's own file overrides its
ancestor's catch-all).

## 3. Forbidden — dependency edges

```
{ from: <spec>, to: <spec>, except?: [...], except_to?: [...], why: '...' }
```

| `from` / `to` accepts | Meaning                                            |
| --------------------- | -------------------------------------------------- |
| `"service"`           | Single module name.                                |
| `["app", "service"]`  | Multiple module names.                             |
| `"*"`                 | Every registered module.                           |
| `"core-*"`            | Prefix wildcard — every module starting with `core-`. |
| `{ captured = ... }`  | Parametric (uses captures from a `capture`-enabled component). |

`except` subtracts from a wildcard `from`; `except_to` from a wildcard `to`.
Strings in either may be prefix wildcards. `why` is the violation message
emitted to developers.

### Canonical examples (encoding-neutral)

```
# Afferent — higher level. Only the orchestrator may import the facade.
{ from: '*', except: ['orchestrator', 'core-*'], to: 'core-facade',
  why: 'Only the orchestrator may import the core facade.' }

# Efferent — own file. Self-contained.
{ from: 'core-*', to: '*', except_to: ['core-*'],
  why: 'Core purity: no imports outside the core module.' }

# Internal layering — own file. Sub-tier names share the prefix.
{ from: 'core-tier3', to: 'core-tier1',
  why: 'Tier 3 must go through tier 2; direct tier-1 access is forbidden.' }

# Parametric — higher level. Sibling sub-domains may not import each other.
{ from: { type: 'domain-handler', captured: { domain: '*' } },
  to:   { type: 'domain-handler', captured: { domain: '!{from.captured.domain}' } },
  why:  'Cross-domain import: extract shared helpers to a sibling shared/ module.' }
```

## 4. Where each rule lives

| Rule type                       | Lives in                  |
| ------------------------------- | ------------------------- |
| Afferent ("who may import me?") | Higher level (composer).  |
| Efferent ("what may I import?") | Own file.                 |
| Cross-module sibling-isolation  | Higher level (composer).  |
| Internal layering               | Own file.                 |
| Sub-tier sibling-isolation      | Own file.                 |

Higher-level rules accumulate. Place each rule where the composition it
expresses lives — sub-tier sibling-isolation in the module's own file (it
composes its sub-tiers); encapsulation between the module and its peers
higher up (where the module is composed with peers).

> [!IMPORTANT] A module's own file MUST reference only its own-prefix names
> (`<own-prefix>-*` or `<own-prefix>-x`) and `*`. Naming any other module is
> a violation — that knowledge belongs higher up.

---

## 5. The assembler

A small script invoked at lint time (CI / pre-commit / editor). Concept is
identical across stacks; encoding is not.

```
# 1. Discover — recursive walk, skipping the configured ignore-list
#    (vendor / build / cache / virtualenv dirs).
files = walk(REPO_ROOT, name = "<config-filename>")
files.sort(by_depth, descending = True)   # deeper-first

# 2. Concat
components = []
forbidden  = []
for f in files:
    data = parse(f)
    components.extend(data.components)
    forbidden.extend(data.forbidden)

# 3. Expand wildcards against the live registry.
#    Turn a spec ('foo' | 'foo-*' | '*' | list | parametric) into
#    a concrete list of component names, with `except` subtracted.
names = [c.name for c in components]
def expand(spec, except_):
    if spec is parametric: return spec     # passthrough
    types = resolve_to_names(spec, names)  # handles *, prefix-*, lists
    if except_: types = types - resolve_to_names(except_, names)
    return types

# 4. Emit the stack's native lint config from `components` + expanded `forbidden`.

# 5. Invoke the stack's lint tool against the emitted config.
```

The discovery + merge + wildcard-expansion pipeline is the same everywhere.
Steps 4 and 5 are the only stack-specific parts.

> [!NOTE] The generated lint config is a **build artifact** — git-ignored,
> regenerated on every run. The source of truth is the per-module
> architecture files.

---

## 6. Timing — rules first for new modules

When introducing a new module on a stack that supports this pattern, write
its architecture file (plus any afferent rules in the parent) **before**
its implementation code. Catching the first wrong import on day 1 is the
point; retrofitted rules either rubber-stamp accidents or trigger
unbounded refactors. The PR that adds the module contains the rules first,
the implementation second.

**Spike escape-hatch.** Code explicitly marked as a spike or throwaway
prototype may skip rules. The spike must be deleted or rewritten
rules-first before merging to main — a spike that crosses the merge
boundary ungoverned becomes the next round of "we'll add the rules later"
code that never gets the gate.

---

## 7. Anti-patterns + pre-merge audit

| Anti-pattern                                  | Fix                                                        |
| --------------------------------------------- | ---------------------------------------------------------- |
| A module's own file names another module.     | Move higher, or rewrite with `<own-prefix>-*` + `*`.       |
| Hardcoded list of "all other modules".        | Use `'*'` + `except` / `except_to`.                        |
| Renaming a module without updating consumers. | Use prefix wildcards (`<prefix>-*`) so renames stay local. |
| Module has rules but no catch-all bucket.     | Add the whole-module entry as the last `components` row.   |
| Dynamic / unresolved imports evade rules.     | Make imports static and resolvable, or document the loophole and ban the dynamic style where possible. |

Before merge:

- [ ] No other-module name appears in any module's own architecture file.
- [ ] `components` ordered narrowest-first; constrained modules end with a
      catch-all.
- [ ] Lint violation count matches baseline (or new violations reflect
      intentional changes).

> [!NOTE] The "no other-module name" check is mechanical — a small AST/TOML
> walk over each architecture file could enforce it as a meta-lint. Until
> then, the manual checklist is the gate.

---

## 8. Output Contract

When designing or auditing rules, emit a coder-facing decision record:

```
Scope:          <repo / package / module path>
Stack:          JavaScript | Python | Other
Decision:       Add config | Update config | Reject rule | Defer | Blocked
Config files:   <eslint.architecture.mjs / architecture.toml / generated config>
Components:     <component names or patterns added/changed>
Forbidden edges:<from -> to rules added/changed>
Verification:   <lint command / meta-lint / Not run + reason>
Next action:    <specific edit, rule, test, or owner question>
```

## 9. Implementations

This skill defines the pattern. Concrete implementations live in
sibling skills:

| Stack      | Config file               | Lint tool                              | Skill |
| ---------- | ------------------------- | -------------------------------------- | ----- |
| JavaScript | `eslint.architecture.mjs` | ESLint + `eslint-plugin-boundaries`    | `architecture-as-code-javascript` |
| Python     | `architecture.toml`       | `import-linter` (over Grimp)           | `architecture-as-code-python`     |

Adapting to a new stack: pick an import-graph linter that supports forbidden
edges between named module sets, then write a small assembler that emits its
native config. Everything in §§ 1–6 transfers; only step 4 of §5 (emit) and
step 5 (invoke) are stack-specific.

## 10. See also

- **`architecture-guidelines`** — first-principles rules this pattern enforces.
- **`geometric-architecture`** — the spatial rationale (cells, faces, locality) this enforces.
- **`defect-shift-left`** — §6.2 (ADR → executable architectural rule) names this pattern.
