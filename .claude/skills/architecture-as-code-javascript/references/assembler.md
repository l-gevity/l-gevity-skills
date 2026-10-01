# Architecture as Code (JavaScript) — The Assembler

Reference for [SKILL.md](../SKILL.md) §2. Read before creating or changing
`eslint.config.js`, the assembler, or the emitted block's `files`, severity,
or `ignores`. Writing or changing an `eslint.architecture.mjs` file needs
only SKILL.md §1.

## 2. Assembler

Runs once at lint startup in `eslint.config.js` (flat-config supports
top-level `await`).

```js
// 1. Discover — recursive readdirSync, skipping ignore-list
//    (node_modules, dist, _site-*, and similar build/output dirs).
const files = findFilesByName(REPO_ROOT, 'eslint.architecture.mjs');
files.sort((a, b) => b.split(sep).length - a.split(sep).length); // deeper-first

// 2. Concat. `components` is the deprecated alias for `subsystems` (pattern
//    §1): warn on it, reject a file that carries both.
const archs = await Promise.all(files.map(f => import(pathToFileURL(f).href)));
const SUBSYSTEMS = archs.flatMap((m, i) => {
    if (m.default.subsystems && m.default.components)
        throw new Error(`${files[i]}: declare subsystems or components, not both`);
    if (m.default.components)
        console.warn(`${files[i]}: 'components' is a deprecated alias for 'subsystems'`);
    return m.default.subsystems ?? m.default.components ?? [];
});
const allForbidden = archs.flatMap(m => m.default.forbidden ?? []);

// 3. Expand wildcards against the live registry.
const names = SUBSYSTEMS.map(c => c.name);
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

// 4. Emit boundaries-plugin config. Forward every field the subsystem schema
//    defines: an omitted field is unexpressible in every architecture file in
//    the repo, with no error to say so.
const elements = SUBSYSTEMS.map(c => ({
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
through declared subsystems, never by softening its severity.

Exclusions — build output, vendored code, generated bundles — belong in the flat
config's shared `ignores`, where one list governs every rule and shows up in
review. Never express them by trimming this block's `files`: a narrowed glob
looks identical to a clean repository in the lint output.

**Dependencies:** `eslint-plugin-boundaries`, plus `"type": "module"` in the
repo-root `package.json`.
