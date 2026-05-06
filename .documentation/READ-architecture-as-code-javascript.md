# Architecture-as-Code

A build step that enforces your architectural rules (the dependency graph). You declare which modules may import from which; violations fail the build.

<img width="1886" height="749" alt="image" src="https://github.com/user-attachments/assets/e6e1f085-dadd-400b-b2b5-e133e50fd650" />

## Why use this

- **Architectural violations are caught at build time**, not days later in review.
- **Refactors follow the architecture automatically.** Change a rule; lint flags every file that must update.
- **Rules document themselves.** Every violation reports a plain-English reason.
- **New developers learn the architecture from the rules**, not from mistakes.
- **Architectural drift becomes impossible.** Year-five stays as clean as year-one.

## Fundamental principles

Architecture is largely the art of managing dependencies. Most rot in long-lived codebases isn't bad logic — it's tangled imports nobody dares touch.

- **Dependencies flow one way.** Cycles couple modules; changes ripple unpredictably.
- **Stable things sit at the bottom.** Volatile code depends on stable code, never the reverse.
- **Boundaries enable local reasoning.** Constrained imports let you change a module without holding the whole system in your head.
- **Fewer dependents = cheaper change.** Encapsulation isn't aesthetic; it's leverage.

Architecture-as-code makes these principles *enforceable* instead of aspirational.

## How to use

1. **Decide your architecture.** Identify the modules and the allowed dependencies between them.
2. **Lay out a matching directory structure.** Each module gets its own path so globs can target it.
3. **Prompt the AI.** Describe the architecture; the skill generates the matching `eslint.architecture.mjs` files.

   > *"Set up architecture-as-code: UI in `src/ui`, business logic in `src/business/orders` and `src/business/billing` (independent), storage in `src/storage`. Enforce one-way layering."*

4. **Run the linter.** Violations print their `why`. Fix and commit.

   ```bash
   npx eslint .
   ```

## The classic prefab: UI → Business → Storage

A layered system with two business modules (`orders`, `billing`) that must stay independent.

### Directory layout

```
src/
├── ui/
├── business/
│   ├── orders/
│   └── billing/
└── storage/
```

### Rules

```js
// eslint.architecture.mjs
export default {
  elements: [
    { name: 'ui',      pattern: 'src/ui/**' },
    { name: 'orders',  pattern: 'src/business/orders/**' },
    { name: 'billing', pattern: 'src/business/billing/**' },
    { name: 'storage', pattern: 'src/storage/**' },
  ],
  rules: [
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

Allowed: `ui → { orders, billing } → storage`. No upward or lateral imports.

## Escape hatch

```js
// eslint-disable-next-line boundaries/dependencies -- TICKET-123
import { db } from '../storage/db.js';
```

Use sparingly. If you reach for it often, the rule is wrong.

## When to skip

Tiny projects, prototypes, throwaway scripts. Otherwise it pays off within a sprint.

## Next steps

- See [SKILL.md](./SKILL.md) for full syntax (captures, parametric rules, facades).
- Run `find . -name "eslint.architecture.mjs" | xargs cat` to read your repo's full architecture in one shot.
