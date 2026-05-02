# Architecture-as-Code: Strategic Guide

> This document explains the **why** and **when** of architecture-as-code. For
> the **how** (file format, syntax, assembler), see
> [SKILL.md](./architecture-as-code-javascript/SKILL.md).

---

## Overview

**Architecture-as-Code** is a pattern that moves architectural rules from
**implicit agreements** → **explicit, enforced code**.

Instead of:

- "Don't import services directly from components" (hopes someone remembers)
- "Use the facade" (documented somewhere, maybe)
- "No cross-domain imports" (caught in code review, maybe)

You have:

- Lint-time violations (caught in seconds)
- Rules visible in the repository tree
- Zero ambiguity about boundaries

---

## What It Solves

Most non-trivial codebases enforce several architectural constraints
simultaneously. Common examples:

| Pattern                     | Example constraint                                                                                         |
| --------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Layered architecture**    | Presentation → Orchestrator → Service → Data; no upstream imports.                                         |
| **Module facades**          | Public entry file is the only allowed import target from outside the module.                               |
| **Domain isolation**        | Sibling domain directories cannot import each other; shared logic lives in a separate `shared/` directory. |
| **Internal stratification** | Inside a module, lower tiers cannot import higher tiers.                                                   |
| **Data / UI separation**    | Content packages cannot import UI code; reusable across platforms.                                         |

**Without enforcement**, any of these can be violated by accident:

- A new contributor doesn't know services are off-limits.
- A quick bug fix shortcuts through the facade.
- A domain handler imports from another domain to "save code".
- A new developer doesn't know about the event bridge.

**With architecture-as-code**, violations **fail at lint time**, before code
review, before deployment.

---

## The Feedback Loop: Why Speed Matters

### Traditional Approach (Manual Review)

```
Developer writes code
         ↓
  (24+ hours pass)
         ↓
Code review finds architecture violation
         ↓
Developer fixes (context is cold)
         ↓
   Re-review
```

Violation caught late. Developer context is cold. Fixes are rushed.

### Architecture-as-Code Approach

```
Developer writes code
         ↓
    (seconds)
         ↓
npm run lint → ARCHITECTURE VIOLATION + `why` message
         ↓
Developer fixes immediately (context is warm)
         ↓
Done. No review needed.
```

Violation caught while code is fresh. The developer learns the rule, not just
fixes the error.

---

## What It Enables

### 1. Safe Refactoring

Want to move a module or change its structure?

```bash
# Update the rule in eslint.architecture.mjs
npm run lint
# See every file that would break
# Fix them all → done
```

Without it: hope you didn't miss anything. Find out months later when something
subtle breaks.

### 2. Scaling with Confidence

Each new module is checked against the **same rules**. No drift accumulates as
the codebase grows or the team turns over.

### 3. Faster Onboarding

A new developer arrives. Instead of reading scattered docs, asking teammates,
and learning by mistake, they:

```bash
find . -name "eslint.architecture.mjs" | xargs cat
```

…and see the entire architecture, with a `why` for every rule.

### 4. Proof of Design

When someone asks _"why doesn't component X import service Y?"_, the answer
isn't _"we decided that once"_ — it's:

```js
{ from: 'component', to: 'service',
  why: 'Components are presentation; use the event bridge instead.' }
```

The rule **is** the documentation. It can't drift because it's enforced.

---

## When Architecture-as-Code Shines

### Perfect fit

- **Multi-domain systems** (APIs split by domain, multi-tenant code).
- **Layered architectures** (UI / services / data).
- **Facade patterns** (encapsulated modules with a public entry point).
- **Growing teams** (new developers shouldn't break patterns).
- **Long-lived projects** (prevent drift over years).
- **High-consequence domains** (rules that affect correctness directly).

### Less critical

- **Tiny projects** (< 5 files; everyone knows everyone).
- **Stateless services** (few architectural constraints).
- **Rapid prototyping** (rules slow exploration).
- **Scripts / CLI tools** (too small to benefit).

If your codebase has complex rules, growing surface area, and a high-consequence
domain, architecture-as-code pays dividends.

---

## How It Works

### The Assembler

At lint startup, the root `eslint.config.js` discovers and merges every
`eslint.architecture.mjs` file in the tree:

```
repo-root/
├── eslint.architecture.mjs              ← system composition rules
└── packages/
    ├── <module-a>/
    │   └── eslint.architecture.mjs      ← module-a's internal rules
    ├── <module-b>/
    │   └── ...
    └── ...
```

**Deeper files register first** (first-match-wins for module resolution).
Module-internal rules take precedence over root-level catch-alls for files
inside that module's directory.

### Three Types of Rules

| Rule type                           | Where it lives                          | Example                                             |
| ----------------------------------- | --------------------------------------- | --------------------------------------------------- |
| **Afferent** ("who may import me?") | Higher up in the tree                   | "Only the orchestrator may import the core facade." |
| **Efferent** ("what may I import?") | Module's own file                       | "Core code only imports core code."                 |
| **Parametric** (sibling-isolation)  | Higher up (where siblings are composed) | "Sibling domain dirs may not import each other."    |

**Key principle.** A module's own file references only itself (`<own-prefix>-*`)
or the anonymous `*`. It never names another module. That keeps each module
ignorant of how it's composed with the rest of the system, while letting it
state everything it knows about itself.

---

## Best Practices

### 1. Rules should reflect design, not accidents

```js
// ✅ Good — reflects intentional design
{ from: 'component', to: 'service',
  why: 'Components are presentation; use the event bridge instead.' }

// ❌ Bad — arbitrary restriction
{ from: 'component', to: 'utils', why: 'Just because.' }
```

Every rule should answer: _"why would we ever prevent this?"_

### 2. Keep `why` actionable

```js
// ✅ Tells the developer what to do
why: 'Services live behind the event bridge. Listen on window for
      typed events instead of importing the service.'

// ❌ Just restates the rule
why: 'Components may not import services.'
```

The `why` is the developer's guide to fixing the violation.

### 3. Use wildcards, not hardcoded lists

```js
// ✅ Scales when you add new tiers
{ from: 'core-*', except: ['core-test'], to: 'core-test',
  why: 'Production code must not import tests.' }

// ❌ Breaks when you add core-tier6
{ from: ['core-tier1', 'core-tier2', 'core-tier3'], to: 'core-test',
  why: '...' }
```

---

## Workflow: Adding a New Module

### Scenario: Add a new domain to a multi-domain API

**Without architecture-as-code:**

1. Create `packages/api/src/<new-domain>/handlers/...`
2. Hope no one violates the _"no cross-domain imports"_ rule.
3. Code review catches violations (maybe).

**With architecture-as-code:**

1. **Declare the module** (or, if a parametric pattern already covers it, do
   nothing — the new directory is matched automatically by the existing capture
   rule):

    ```js
    { name: 'domain-handler',
      pattern: 'packages/api/src/*/**',
      capture: ['domain'] }
    ```

2. **The rule already exists:**

    ```js
    { from: { type: 'domain-handler', captured: { domain: '*' } },
      to:   { type: 'domain-handler',
              captured: { domain: '!{{from.captured.domain}}' } },
      why: 'Cross-domain import: extract shared helpers to a sibling shared/ directory.' }
    ```

3. **Done.** Lint automatically prevents cross-domain handler imports. New
   developers can't accidentally violate it.

---

## Maintenance Checklist

### Before merging a PR with architecture changes

- [ ] No module's own file names another module (it references only itself or
      `*`).
- [ ] `components` is ordered narrowest-first (file-mode → sub-directories →
      catch-all) within each file.
- [ ] Wildcard rules use `<prefix>-*` instead of hardcoded lists.
- [ ] Every `why` explains the design decision, not just restates the rule.
- [ ] `npx eslint .` passes (or new warnings are intentional).

### When adding a new module with internal complexity

1. Create `<module>/eslint.architecture.mjs`.
2. Declare internal sub-modules (tiers, layers, sub-domains).
3. Express layering with prefix wildcards (`<own-prefix>-*`).
4. **Do not reference any other module** — keep the file self-contained.
5. Afferent rules (who may import this module) live higher up in the tree, not
   inside the module's own file.

---

## Common Patterns

### Pattern 1: Facade + internal tiers

```js
// In the module's own eslint.architecture.mjs
{ name: 'core-facade', pattern: 'packages/<module>/index.js', mode: 'file' },
{ name: 'core-tier1',  pattern: 'packages/<module>/tier1/**' },
{ name: 'core-tier2',  pattern: 'packages/<module>/tier2/**' },
// ...
{ name: 'core-other',  pattern: 'packages/<module>/**' },          // catch-all

// Enforce tier stratification
{ from: 'core-tier1', to: ['core-tier2', 'core-tier3', 'core-facade', 'core-other'],
  why: 'tier1 is foundation; cannot import higher tiers.' }

// Enforce purity (the module doesn't reach outside itself)
{ from: 'core-*', to: '*', except_to: ['core-*'],
  why: 'Module is self-contained.' }
```

### Pattern 2: Parametric sibling-isolation

```js
// Higher up (root or a level that composes the siblings)
{ name: 'domain-handler',
  pattern: 'packages/api/src/*/**',
  capture: ['domain'] }

{ from: { type: 'domain-handler', captured: { domain: '*' } },
  to:   { type: 'domain-handler', captured: { domain: '!{{from.captured.domain}}' } },
  why: 'Cross-domain import: extract shared helpers to a sibling shared/ directory.' }
```

### Pattern 3: Layer direction

```js
// Presentation may not reach into the service layer (use the event bridge)
{ from: 'component', to: 'service',
  why: 'Components are presentation; use the event bridge instead of direct imports.' }

// Service layer may not reach back up into presentation
{ from: 'service', to: ['component', 'page-script', 'app'],
  why: 'Services are downstream of UI; reaching upward is a layer violation.' }
```

---

## Limitations

### Can enforce

- Import restrictions (A may not import B).
- Layer direction (downstream may not import upstream).
- Encapsulation (only the facade is importable).
- Domain isolation (domain X may not import domain Y).

### Cannot enforce

- **Business logic placement** ("don't do calculations in the UI" — handled by
  code review).
- **Organizational boundaries** (who reports to whom).
- **Runtime behavior** (lint-time only).
- **Complexity** (no rule against 1000-line functions).
- **Naming conventions** (beyond what other lint rules already check).

Use architecture-as-code for **dependencies**. Use testing, code review, and
team discipline for everything else.

---

## Integration with Daily Workflow

### Local development

```bash
# Write code
git add .

# Lint check (includes architecture rules)
npx eslint .

# If architecture violation:
# 1. Read the error message
# 2. Read the `why` explanation
# 3. Fix the import
# 4. Done — no review time spent on this
```

### Code review

**Old.** The reviewer manually checks architecture; trust-based.

**New.** Lint already caught it. The reviewer focuses on logic, correctness, and
tests rather than re-checking layer rules.

### Refactoring

```bash
# Change a rule
vim eslint.architecture.mjs

# Run lint
npx eslint .

# See every file that would break
# Fix them all → done with confidence
```

---

## FAQ

### "What if I need to break a rule?"

You shouldn't, but if you must:

```js
// eslint-disable-next-line boundaries/dependencies -- TICKET-123: temporary until refactor
import { service } from '...';
```

Use this sparingly. If you reach for it often, the rule is wrong — re-evaluate
and update the rule, don't paper over it.

### "Can I disable architecture-as-code?"

Yes — flip the `boundaries/dependencies` severity in `eslint.config.js` from
`'warn'` (or `'error'`) to `'off'`. But then you lose the benefits. Better to
fix the rule.

### "What if a rule is outdated?"

Update it. The rule lives in the repository, not in your head.

```js
// Old — too strict
{ from: 'component', to: 'service', ... }

// New — service writes go through the bridge, but reads of derived
// metrics are allowed directly
{ from: 'component', to: 'service', except_to: ['metrics'], ... }
```

Run lint, fix the resulting violations, merge, done.

### "Does this work with absolute / aliased imports?"

`eslint-plugin-boundaries` only enforces rules on imports it can resolve to a
real file path. Bare relative imports work out of the box. For host-served
absolute paths (e.g. `/js/...` served by an import map) or path aliases
(`@/components/...`), register `eslint-import-resolver-alias` (or the resolver
matching your tooling) under `settings['import/resolver']`. Until you do, the
plugin will silently skip those imports.

---

## Long-Term Value

### Without architecture-as-code

```
Year 1:  Team knows the rules → clean architecture.
Year 2:  Team grows; some violations slip through → slight drift.
Year 3:  Onboarding is slower; violations regular → significant drift.
Year 4:  Refactoring is risky; new features are slow → architecture
         is a legacy burden.
```

### With architecture-as-code

```
Year 1:  Rules are explicit; every violation fails lint → clean.
Year 2:  New people learn rules from the code, not training → clean.
Year 3:  Onboarding is fast (read the .mjs files); zero drift → clean.
Year 4:  Architecture scales naturally; refactoring is safe → clean.
Year N:  Codebase grows, architecture stays clean. Drift is impossible.
```

---

## Next Steps

1. **Read [SKILL.md](./architecture-as-code-javascript/SKILL.md)** for the
   technical reference (file format, syntax, assembler).
2. **Read your repo-root `eslint.architecture.mjs`** to see the actual system
   composition rules.
3. **Read any module-local `eslint.architecture.mjs`** to see how a
   self-contained module declares its own internals.
4. **Run `npx eslint .`** to see the rules in action.
5. **Ask questions** if a rule's purpose isn't clear — the `why` field should
   explain it. If it doesn't, that's a documentation bug; fix it.

---

## See Also

- [SKILL.md](./architecture-as-code-javascript/SKILL.md) — technical reference
  (file format, syntax, assembler)
- [architecture-guidelines](./architecture-guidelines/) — first-principles
  design rules
- [geometric-architecture](./geometric-architecture/) — spatial / coordinate
  model of dependencies
