---
name: architecture-as-code-javascript
description: >-
    JavaScript / TypeScript implementation of the `architecture-as-code`
    pattern. Per-module `eslint.architecture.mjs` files merged into a single
    ESLint flat-config and enforced via `eslint-plugin-boundaries`. TRIGGER
    when: implementing or extending architecture-as-code in a JS/TS repo,
    debugging an `eslint-plugin-boundaries` rule, or adapting the assembler.
    SKIP for routine edits inside a governed module. Reads in conjunction with
    `architecture-as-code` (the pattern, source of truth for schema, rule
    placement, anti-patterns, and audit checklist) — this skill defines only
    the JS-specific encoding, assembler code, and gotchas.
---

# Architecture-as-Code — JavaScript Implementation

> **Prerequisite.** Read [`architecture-as-code`](../architecture-as-code/)
> first. The schema (§1), components (§2), forbidden edges (§3), rule
> placement (§4), assembler concept (§5), and anti-patterns / audit (§6) are
> defined there and apply identically here. This file documents only what is
> JavaScript-specific.

## 1. File format

- Filename: `eslint.architecture.mjs`. Use `.mjs` only; `.js` trips
  source-discovery walkers and ESLint's own config-loader.
- ES module with `export default { components: [...], forbidden: [...] }`.
- Pattern syntax: filesystem globs (`<dir>/**`).
- Repo-root `package.json` must include `"type": "module"`.

```js
// eslint.architecture.mjs — example for a module with internal layering
export default {
    components: [
        { name: 'core-facade', pattern: 'packages/core/index.js', mode: 'file' },
        { name: 'core-tier1',  pattern: 'packages/core/tier1/**' },
        { name: 'core-tier3',  pattern: 'packages/core/tier3/**' },
        { name: 'core-other',  pattern: 'packages/core/**' },        // catch-all, last
    ],
    forbidden: [
        // Efferent — self-knowledge, lives in own file.
        { from: 'core-*', to: '*', except_to: ['core-*'],
          why: 'Core purity: no imports outside the core directory.' },
        // Internal layering — own-prefix only.
        { from: 'core-tier3', to: 'core-tier1',
          why: 'Tier 3 must go through tier 2.' },
    ],
};
```

Boundaries-plugin's parametric "not equal" syntax for cross-domain isolation
is `!{{from.captured.domain}}` (double braces).

## 2. Assembler

Runs once at lint startup in `eslint.config.js` (flat-config supports
top-level `await`).

```js
// 1. Discover — recursive readdirSync, skipping ignore-list
//    (node_modules, dist, _site-*, and similar build/output dirs).
const files = findFilesByName(REPO_ROOT, 'eslint.architecture.mjs');
files.sort((a, b) => b.split(sep).length - a.split(sep).length); // deeper-first

// 2. Concat
const archs = await Promise.all(files.map(f => import(pathToFileURL(f).href)));
const COMPONENTS  = archs.flatMap(m => m.default.components ?? []);
const allForbidden = archs.flatMap(m => m.default.forbidden ?? []);

// 3. Expand wildcards against the live registry.
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

// 4. Emit boundaries-plugin config.
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

## 3. Output Contract

When applying this implementation, emit:

```
Scope:          <repo / package / module path>
Decision:       Add eslint.architecture.mjs | Update assembler | Update ESLint config | Blocked
Generated config:<path, if any>
Rules changed:  <boundaries/dependencies or no-restricted-imports entries>
Verification:   <eslint command / assembler command / Not run + reason>
Next action:    <specific file edit, dependency install, or unresolved question>
```

## 4. JavaScript-specific gotchas

> [!NOTE] **Unresolved imports bypass enforcement.** `eslint-plugin-boundaries`
> only enforces rules on imports it can resolve to a file path. Host-served
> absolute paths (e.g. SWA's `/js/...`) aren't resolved by default and pass
> silently. Fix: install `eslint-import-resolver-alias` and add it under
> `settings['import/resolver']` so `/js → packages/.../js` resolves.

> [!NOTE] **Unmatched files bypass enforcement.** Files matching no component
> are invisible to the plugin. End every constrained module's `components`
> with a `<dir>/**` catch-all (pattern directive #5).

> [!NOTE] **Facade-as-file pattern.** JavaScript idiomatically exposes a
> facade as a single index/entry file. Use `mode: 'file'` plus an exact-path
> `pattern` (no glob) so the facade is matched alone.

> [!NOTE] **`.js` config breaks discovery.** Many source-discovery walkers
> (the assembler's own, plus some lint plugins) treat `.js` as analyzable
> source. Naming the architecture file `.js` triggers self-reference and
> mis-classification. `.mjs` is required.
