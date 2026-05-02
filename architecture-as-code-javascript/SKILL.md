---
name: architecture-as-code
description: >-
    Pluggable mechanism for declaring and enforcing component boundaries via
    `.mjs` files in the source tree. Every module lives in a directory (or
    single file for a facade) and MAY ship an `eslint.architecture.mjs`
    declaring its components and rules. Files merge recursively: rules from
    higher levels accumulate. ESLint discovers them and builds one rule set. Use
    when: adding a module, splitting one, expressing a new dependency rule,
    debugging a forbidden edge, or extending the assembler. SKIP for routine
    edits inside a governed module. See `architecture-guidelines` for first
    principles, `geometric-architecture` for spatial rationale,
    `eslint-fix-protocol` for daily lint workflow.
---

# Architecture-as-Code

> **Scope.** Describes the file format, discovery, and assembly that turn the
> directory tree into an enforced dependency graph. Runs as ESLint flat-config
> via `eslint-plugin-boundaries` — no ESLint, no enforcement. Does NOT prescribe
> what the graph should look like — that's `architecture-guidelines` and
> `geometric-architecture`. Does NOT govern code style — that's
> `coding-standard`.

> **TL;DR / Core Directives**
>
> 1. **Module = directory** (or a single file with `mode: 'file'`, e.g. a
>    facade). Files belong to a module by living in that path. Patterns are
>    usually `<dir>/**`.
> 2. **One optional file per module** — `eslint.architecture.mjs`. Use `.mjs`
>    only; `.js` trips source-discovery walkers. Repo root has one too, same
>    structure.
> 3. **A module knows itself, not its context.** Its own file governs internals
>    (sub-tiers, layering) and outbound dependencies ("what I import") — never
>    inbound ones ("who imports me") or its place in the wider system, which it
>    does not and should not know. Mechanically: only `<own-prefix>-*`, specific
>    `<own-prefix>-x` names, and the anonymous `*` may appear; any other module
>    name is a violation.
> 4. **Composition lives on the level that does the composing.** Constraints
>    between a module and the system (afferent — "who may import me" — and
>    cross-module sibling-isolation) live higher up. Constraints among a
>    module's own sub-tiers (internal layering, sub-tier sibling-isolation) live
>    in its own file. Efferent rules ("what may I import") are self-knowledge —
>    own file. Higher-level rules accumulate.
> 5. **Every module with rules ends with a catch-all bucket.** Unmatched files
>    silently bypass forbidden edges, so a `<dir>/**` entry MUST appear last in
>    `components`.
> 6. **Recursion via discovery.** Assembler globs the tree; deeper files
>    register first (first-match-wins).

---

## 1. File schema

Each architecture file exports a default object with two optional fields:

```js
export default {
    components: [
        /* one entry per module */
    ],
    forbidden: [
        /* dependency edges */
    ],
};
```

Most modules don't need their own file — they're declared once in the
`components` list higher up in the tree.

> [!NOTE] `<own-prefix>` is the shared prefix of a module's component names —
> e.g. `core-` for `core-facade`, `core-tier1`, `core-other`. Single-component
> modules (e.g. `service`) just use the bare name.

## 2. Components — modules declared as directories

| Field     | Required | Purpose                                                      |
| --------- | -------- | ------------------------------------------------------------ |
| `name`    | yes      | Module id referenced from `forbidden` edges.                 |
| `pattern` | yes      | Glob (or array) selecting the directory; usually `<dir>/**`. |
| `mode`    | no       | `'file'` for single-file modules (e.g. a public facade).     |
| `capture` | no       | Segment captures, e.g. `['domain']`, for parametric rules.   |

Order = first-match-wins. Within a file: narrowest first (file-mode →
sub-directories → catch-all). Across files: deeper-first.

```js
// A module's own file. Each entry maps to a directory (or a single file).
{ name: 'core-facade', pattern: 'packages/<module>/index.js', mode: 'file' },
{ name: 'core-tier1',  pattern: 'packages/<module>/tier1/**' },
// ...narrower buckets
{ name: 'core-other',  pattern: 'packages/<module>/**' },  // catch-all, last
```

## 3. Forbidden — dependency edges

```js
{ from: <spec>, to: <spec>, except?: [...], except_to?: [...], why: '...' }
```

| `from`/`to` accepts  | Meaning                                               |
| -------------------- | ----------------------------------------------------- |
| `'service'`          | Single module name.                                   |
| `['app', 'service']` | Multiple module names.                                |
| `'*'`                | Every registered module.                              |
| `'core-*'`           | Prefix wildcard — every module starting with `core-`. |
| `{ type, captured }` | Parametric (boundaries-plugin native).                |

`except` subtracts from a wildcard `from`; `except_to` from a wildcard `to`.
Strings in either may be prefix wildcards. `why` is the violation message.

### Examples

```js
// Afferent — higher level. Only the orchestrator may import the facade.
{ from: '*', except: ['orchestrator', 'core-*'], to: 'core-facade',
  why: 'Only the orchestrator may import the core facade.' }

// Efferent — own file. Self-contained.
{ from: 'core-*', to: '*', except_to: ['core-*'],
  why: 'Core purity: no imports outside the core directory.' }

// Internal layering — own file. Sub-tier names share the prefix.
{ from: 'core-tier3', to: 'core-tier1',
  why: 'Tier 3 must go through tier 2; direct tier-1 access is forbidden.' }

// Parametric — higher level. Sibling sub-domains may not import each other.
{ from: { type: 'domain-handler', captured: { domain: '*' } },
  to:   { type: 'domain-handler', captured: { domain: '!{{from.captured.domain}}' } },
  why: 'Cross-domain import: extract shared helpers to a sibling shared/ directory.' }
```

`!{{from.captured.domain}}` is boundaries-plugin's native "not equal" syntax —
the rule fires when the two `domain` captures differ.

## 4. Where each rule lives

| Rule type                       | Lives in                 |
| ------------------------------- | ------------------------ |
| Afferent ("who may import me?") | Higher level (composer). |
| Efferent ("what may I import?") | Own file.                |
| Cross-module sibling-isolation  | Higher level (composer). |
| Internal layering               | Own file.                |
| Sub-tier sibling-isolation      | Own file.                |

Higher-level rules accumulate. Place each rule where the composition it
expresses lives — sub-tier sibling-isolation in the module's own file (it
composes its sub-tiers); encapsulation between the module and the system higher
up (where the module is composed with peers).

> [!IMPORTANT] A module's own file MUST reference only its own-prefix names
> (`<own-prefix>-*` or `<own-prefix>-x`) and `*`. Naming any other module is a
> violation — that knowledge belongs higher up.

---

## 5. The assembler

`eslint.config.js` runs once at lint startup (flat-config supports top-level
`await`).

```js
// 1. Discover — recursive readdirSync, skipping the configured ignore-list
//    (node_modules, dist, _site-*, and similar build/output dirs).
const files = findFilesByName(REPO_ROOT, 'eslint.architecture.mjs');
files.sort((a, b) => b.split(sep).length - a.split(sep).length); // deeper-first

// 2. Concat
const archs = await Promise.all(files.map(f => import(pathToFileURL(f).href)));
const COMPONENTS = archs.flatMap(m => m.default.components ?? []);
const allForbidden = archs.flatMap(m => m.default.forbidden ?? []);

// 3. Expand wildcards against the live registry.
//    Turn a spec ('foo' | 'foo-*' | '*' | string[] | parametric obj) into
//    a boundaries-plugin type list, with `except` subtracted.
const names = COMPONENTS.map(c => c.name);
function expand(spec, except) {
    if (spec && typeof spec === 'object' && !Array.isArray(spec)) return spec; // parametric
    const resolve = list =>
        list.flatMap(t =>
            t === '*'
                ? names
                : t.endsWith('*')
                  ? names.filter(n => n.startsWith(t.slice(0, -1)))
                  : [t]
        );
    let types = resolve(Array.isArray(spec) ? spec : [spec]);
    if (except?.length) types = types.filter(t => !resolve(except).includes(t));
    return { type: types.length === 1 ? types[0] : types };
}

// 4. Emit boundaries-plugin config
const elements = COMPONENTS.map(c => ({
    type: c.name,
    pattern: c.pattern,
    ...(c.mode && { mode: c.mode }),
    ...(c.capture && { capture: c.capture }),
}));
const rules = allForbidden.map(e => ({
    from: expand(e.from, e.except),
    disallow: { to: expand(e.to, e.except_to) },
    message: e.why,
}));

export default [
    /* ...language blocks, SDK lockdown, etc... */
    {
        files: ['packages/**/*.{js,ts,mjs}'],
        plugins: { boundaries },
        settings: { 'boundaries/elements': elements },
        rules: {
            'boundaries/dependencies': ['warn', { default: 'allow', rules }],
        },
    },
];
```

**Dependencies:** `eslint-plugin-boundaries`, plus `"type": "module"` in the
repo-root `package.json`.

### Known gotchas

> [!NOTE] **Unresolved imports bypass enforcement.** The plugin only enforces
> rules on imports it can resolve to a file path. Host-served absolute paths
> (e.g. SWA's `/js/...`) aren't resolved by default and pass silently. Fix:
> install `eslint-import-resolver-alias` and add it under
> `settings['import/resolver']` so `/js → packages/.../js` resolves.

> [!NOTE] **Unmatched files bypass enforcement.** Files matching no component
> are invisible to the plugin. End every constrained module's `components` with
> a `<dir>/**` catch-all (directive #5).

---

## 6. Recipes

| To do                         | Where                                                                                                              |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Add a new module              | One row in `components` where the module is composed (usually root).                                               |
| Add a dependency rule         | One row in `forbidden` higher than the modules it constrains.                                                      |
| Module with internal layering | Create the module's own file; declare sub-modules; layer with `<own-prefix>-*` or specific `<own-prefix>-x` names. |
| Sibling-isolation             | At the composer's level: `capture` on the parent, parametric `from`/`to`.                                          |

## 7. Anti-patterns + pre-merge audit

| Anti-pattern                                  | Fix                                                        |
| --------------------------------------------- | ---------------------------------------------------------- |
| A module's own file names another module.     | Move higher, or rewrite with `<own-prefix>-*` + `*`.       |
| Hardcoded list of "all other modules".        | Use `'*'` + `except` / `except_to`.                        |
| Renaming a module without updating consumers. | Use prefix wildcards (`<prefix>-*`) so renames stay local. |
| Module has rules but no catch-all bucket.     | Add `<dir>/**` as the last `components` row.               |

Before merge:

- [ ] No other-module name appears in any module's own architecture file.
- [ ] `components` ordered narrowest-first; constrained modules end with a
      `<dir>/**` catch-all.
- [ ] `npx eslint .` warning count matches baseline (or new warnings reflect
      intentional changes).

> [!NOTE] The "no other-module name" check is mechanical — a small AST walk
> could enforce it as a meta-lint. Until then, the manual checklist is the gate.
