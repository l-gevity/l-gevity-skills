# Architecture-as-Code — JavaScript

> **Prerequisite.** Read
> [`architecture-as-code`](./READ-architecture-as-code.md) first — it
> defines the universal pattern (schema, rule placement, anti-patterns,
> "why this works"). This primer documents the JavaScript / TypeScript
> implementation: `eslint.architecture.mjs` files merged into one ESLint
> flat-config and enforced by `eslint-plugin-boundaries`.

## How to use

1. **Decide your architecture.** Identify modules and allowed dependency
   edges. (Pattern primer covers the universals.)
2. **Lay out a matching directory structure.** Each module gets its own
   path so globs can target it.
3. **Drop an `eslint.architecture.mjs` next to each module that needs its
   own rules.** Most modules don't need their own file — they're declared
   once higher up.
4. **Prompt the AI.** Describe the architecture; the skill generates the
   matching `.mjs` files.

   > *"Set up architecture-as-code in JS: UI in `src/ui`, business logic in
   > `src/business/orders` and `src/business/billing` (independent),
   > storage in `src/storage`. Enforce one-way layering."*

5. **Run the linter.** Violations print their `why`.

   ```bash
   npx eslint .
   ```

## The classic prefab in JavaScript

```js
// eslint.architecture.mjs — repo root
export default {
  components: [
    { name: 'ui',      pattern: 'src/ui/**' },
    { name: 'orders',  pattern: 'src/business/orders/**' },
    { name: 'billing', pattern: 'src/business/billing/**' },
    { name: 'storage', pattern: 'src/storage/**' },
  ],
  forbidden: [
    // Layer direction
    { from: 'ui', to: 'storage',
      why: 'UI must not import storage directly. Go through a business module.' },

    { from: ['orders', 'billing'], to: 'ui',
      why: 'Business logic is below UI; it never imports upward.' },

    { from: 'storage', to: ['ui', 'orders', 'billing'],
      why: 'Storage is the bottom layer. It depends on nothing above it.' },

    // Module independence
    { from: 'orders',  to: 'billing',
      why: 'Business modules stay independent. Move shared logic into its own module.' },

    { from: 'billing', to: 'orders',
      why: 'Business modules stay independent. Move shared logic into its own module.' },
  ],
};
```

## JavaScript-specific notes

- **File extension matters.** Use `.mjs` only — `.js` trips source-discovery
  walkers and ESLint's own config-loader.
- **Facade-as-file.** Single-file facades use `mode: 'file'` plus an
  exact-path `pattern` (no glob).
- **Unresolved imports bypass enforcement.** `eslint-plugin-boundaries`
  only enforces rules on imports it can resolve to a file path. Host-served
  absolute paths (e.g. SWA's `/js/...`) need
  `eslint-import-resolver-alias`.
- **Computed dynamic imports bypass enforcement.** Add
  `no-restricted-syntax` for non-literal `ImportExpression` nodes so every
  dynamic import path remains statically resolvable.
- **Keep test code out of production.** Match test files as narrower boundary
  components before the production catch-all, then forbid production
  components from importing test-only components.
- **Repo-root `package.json` must include `"type": "module"`** for the
  `.mjs` discovery and dynamic import to work.

## Escape hatch

```js
// eslint-disable-next-line boundaries/dependencies -- TICKET-123
import { db } from '../storage/db.js';
```

Use sparingly. If you reach for it often, the rule is wrong.

## Next steps

- See [SKILL.md](../.claude/skills/architecture-as-code-javascript/SKILL.md)
  for the full assembler code, advanced features (captures, parametric
  rules), and JS-specific gotchas.
- For the universal pattern, see
  [READ-architecture-as-code](./READ-architecture-as-code.md).
- Run `find . -name "eslint.architecture.mjs" | xargs cat` to read your
  repo's full architecture in one shot.
