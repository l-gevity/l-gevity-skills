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
- ES module with `export default { components: [...], forbidden: [...] }`, plus
  an optional `externals: [...]` for npm-package policy (§3). `forbidden`
  relates declared components to each other and cannot name a package.
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

// 4. Emit boundaries-plugin config. Forward every field the component schema
//    defines: an omitted field is unexpressible in every architecture file in
//    the repo, with no error to say so.
const elements = COMPONENTS.map(c => ({
    type: c.name,
    pattern: c.pattern,
    ...(c.mode && { mode: c.mode }),        // REQUIRED — see § 5, matching mode
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
        // The broad glob is the point, not an accident. This `files` entry is
        // the second coverage gate: the element registry cannot fire on a file
        // the rule never runs on. It must equal the linted source set
        // (pattern Directive 7).
        files: ['**/*.{js,jsx,mjs,ts,tsx}'],
        plugins: { boundaries },
        settings: { 'boundaries/elements': elements },
        rules: {
            // File-existence gate. Flags any file matching no element, whether
            // or not it imports anything — this is what catches a new
            // undeclared directory (pattern Directive 8).
            'boundaries/no-unknown-files': 'error',
            'boundaries/dependencies': ['error', { default: 'allow', rules }],
        },
    },
];
```

Both rules are emitted at `error`. The pattern requires the file-existence rule
at error severity alongside the dependency rules, and a dependency rule at
`warn` is a report rather than a boundary: the build stays green while the edge
it forbids ships. If a repository cannot yet pass, narrow the rule's scope
through declared components, never by softening its severity.

Exclusions — build output, vendored code, generated bundles — belong in the flat
config's shared `ignores`, where one list governs every rule and shows up in
review. Never express them by trimming this block's `files`: a narrowed glob
looks identical to a clean repository in the lint output.

**Dependencies:** `eslint-plugin-boundaries`, plus `"type": "module"` in the
repo-root `package.json`.

## 3. JavaScript-specific enforcement recipes

### Confine a provider SDK to its adapter

The `architecture-guidelines` §10 handoff usually arrives as "only the adapter
may talk to the provider". A provider SDK is an **npm package, not an
element**, so `forbidden` cannot express it: that list only relates declared
components to each other. Declare package policy separately.

```js
// eslint.architecture.mjs
export default {
    components: [
        { name: 'email-adapter', pattern: 'api/src/email/**' },
        { name: 'api-other',     pattern: 'api/src/**' },   // catch-all, last
    ],
    forbidden: [ /* element-to-element edges */ ],
    externals: [
        { package: '@azure/communication-email', allow: ['email-adapter'],
          why: 'The provider SDK is confined to its adapter; callers use the port.' },
    ],
};
```

Assembler translation. Policies are evaluated in order and **the last match
wins**, so deny the package everywhere first, then re-allow its owning
elements:

```js
const allExternals = archs.flatMap(m => m.default.externals ?? []);
const externalRules = allExternals.flatMap(x => [
    { from: expand('*'),
      disallow: { to: { module: { origin: 'external', source: x.package } } },
      message: x.why },
    { from: expand(x.allow),
      allow: { to: { module: { origin: 'external', source: x.package } } } },
]);

'boundaries/dependencies': ['error', {
    default: 'allow',
    checkAllOrigins: true,                       // REQUIRED — see below
    rules: [...rules, ...externalRules],
}],
```

Two traps make this silently wrong:

- **Without `checkAllOrigins: true` the policy never fires.** The rule reports
  nothing, the lint is green, and the boundary does not exist. The flag is not
  an optimization.
- **`checkAllOrigins: true` subjects every package to the block's `default`.**
  With `default: 'disallow'` that turns one SDK policy into a repo-wide import
  ban. Keep the blanket `default: 'allow'` and express prohibition as rules, or
  add an explicit allow-all policy first.

Register the rule at `error`. At `warn` this is a report, not a boundary.

**Prove it red first.** Add a throwaway file that imports the package from
outside the adapter, confirm the lint fails on it with the declared message and
line, delete the file, then confirm the adapter and its callers pass. A policy
that has never failed has not been shown to run — the `checkAllOrigins` trap
above produces exactly the same green output as a working rule.

### Require literal dynamic-import paths

A computed `import(expression)` can bypass path resolution and therefore every
component boundary. Apply this rule to every production and test source block:

```js
{
    files: ['**/*.{js,jsx,mjs,ts,tsx}'],
    rules: {
        'no-restricted-syntax': [
            'error',
            {
                selector: 'ImportExpression[source.type!="Literal"]',
                message:
                    'Dynamic import paths must be string literals so dependency boundaries remain enforceable.',
            },
        ],
    },
}
```

This permits `import('./known-module.js')` and rejects variables, concatenation,
and template expressions. Keep the rule in the same flat config as the
boundaries rules so a new source block cannot silently omit it.

### Prevent production imports of test-only code

Declare test code as a narrower component before the production catch-all, then
forbid the production component from importing it:

```js
export default {
    components: [
        { name: 'app-test', pattern: 'src/**/*.test.{js,jsx,ts,tsx}' },
        { name: 'app-test-support', pattern: 'test/**' },
        { name: 'app-prod', pattern: 'src/**' }, // catch-all, last
    ],
    forbidden: [
        {
            from: 'app-prod',
            to: 'app-test*',
            why: 'Production code must not import test-only code.',
        },
    ],
};
```

Tests may still import production components. Adapt the globs to the repository,
but retain the direction: production → test is forbidden.

### Classify repository-root files

Root-level loose files — configs, entry scripts, generators — are the ones most
often left unclassified, and the pattern's catch-all directive does not help
here. A folder-mode `**` at the root matches at the shallowest segment and
claims files that specific elements already own, from any position in the list
(see § 5). Declare the root's files with `mode: 'file'` instead:

```js
// eslint.architecture.mjs (repository root)
export default {
    components: [
        { name: 'repo-tooling-config', pattern: '*.config.js', mode: 'file' },
        { name: 'repo-tooling-entry',  pattern: 'server.js',   mode: 'file' },
        // No '**' catch-all at this level.
    ],
};
```

`boundaries/no-unknown-files` then names each root file still unclassified, so
the list comes from the linter's output rather than from memory.

## 4. Output Contract

When applying this implementation, emit:

```
Scope:          <repo / package / module path>
Decision:       Add eslint.architecture.mjs | Update assembler | Update ESLint config | Blocked
Generated config:<path, if any>
Rules changed:  <boundaries/dependencies element edges, externals package policy, or no-restricted-imports entries>
Verification:   <eslint command / assembler command / red-first proof / Not run + reason>
Next action:    <specific file edit, dependency install, or unresolved question>
```

## 5. JavaScript-specific gotchas

> [!NOTE] **Unresolved imports bypass enforcement.** `eslint-plugin-boundaries`
> only enforces rules on imports it can resolve to a file path. Host-served
> absolute paths (e.g. SWA's `/js/...`) aren't resolved by default and pass
> silently. Fix: install `eslint-import-resolver-alias` and add it under
> `settings['import/resolver']` so `/js → packages/.../js` resolves.

> [!IMPORTANT] **The rule block's `files` glob is a second, independent gate.**
> A correct element registry, correct forbidden edges, and strict severities do
> nothing on a path outside `files`. A narrowed glob —
> `['packages/**/*.{js,ts,mjs}']`, or an allowlist that grew one directory at a
> time — lets an entire new top-level directory into the repository with the
> boundaries lint reporting zero violations, because the rule never ran on it.
> Nothing in the output distinguishes that from a clean run. Keep the scope at
> `['**/*.{js,jsx,mjs,ts,tsx}']`.

> [!IMPORTANT] **`mode` decides what a pattern matches, and the default is
> `folder`.** In folder mode a pattern is tested against a file's path
> *ancestors*, so `**` matches at the shallowest segment and captures files
> that deeper, more specific elements already own — regardless of its position
> in the list. A root-level `{ name: 'repo-unclassified', pattern: '**' }`
> declared last, after several dozen specific elements, still wins, and yields
> a flood of misclassifications rather than the intended safety net. Use
> `mode: 'file'` for anything a shallower pattern would swallow.

> [!NOTE] **`mode` is deprecated in v7 and the suggested replacement does not
> cover this case.** The deprecation warning recommends `partialMatch: false`;
> that does not classify a repository-root file — with a glob or with an exact
> filename, the file stays unknown. `mode: 'file'` is currently the only form
> that works. Accept the warning instead of chasing it.

> [!NOTE] **`boundaries/external` still works and is deprecated in v7.** Unlike
> the `mode` deprecation above, this one has a working replacement: fold
> package policy into `boundaries/dependencies` with `checkAllOrigins: true`
> and the `to.module.origin` / `to.module.source` sub-selector (§3, *Confine a
> provider SDK to its adapter*). Do not run both rules over the same package —
> two verdicts on one edge, and the one that reports depends on rule order.

> [!NOTE] **Unmatched files bypass enforcement — silently.** Files matching no
> element are invisible to `boundaries/dependencies`. End every constrained
> module's `components` with a `<dir>/**` catch-all (pattern Directive 5), and
> set `boundaries/no-unknown-files` to `error` so an unmatched file is reported
> instead of ignored. Dependency rules are not a substitute: a file with no
> imports, or one loaded by a `<script>` tag, has no edge to judge.

> [!NOTE] **Facade-as-file pattern.** JavaScript idiomatically exposes a
> facade as a single index/entry file. Use `mode: 'file'` plus an exact-path
> `pattern` (no glob) so the facade is matched alone.

> [!NOTE] **`.js` config breaks discovery.** Many source-discovery walkers
> (the assembler's own, plus some lint plugins) treat `.js` as analyzable
> source. Naming the architecture file `.js` triggers self-reference and
> mis-classification. `.mjs` is required.
