# Geometric Architecture — Companion

> **Companion to [`SKILL.md`](./SKILL.md).** Read SKILL.md first — that is the
> canonical operational reference (axes, faces, failure modes, lint rules,
> rollout). This file argues _why_ the model is shaped the way it is, derives it
> from first principles, and walks through a complete ESLint configuration. It
> does not repeat definitions; it explains them.

> **The core claim:** Spaghetti architecture is not a discipline problem. It is
> a vocabulary problem. When a system has no spatial structure, every connection
> is equally expressible. Geometry fixes that by making long-range connections
> _harder to express than short-range ones_ — not through rules people can
> ignore, but through the structure of the language itself.

---

## 1. Why software rots: the unconstrained graph problem

Every software system is, at its root, a directed graph. Modules are nodes.
Dependencies are edges. And in the default state — the state you get without
deliberate constraint — that graph is **fully connected**: any node can reach
any other node with a single edge.

This is the precise technical definition of spaghetti. Not messy code. Not bad
naming. The problem is that the _vocabulary of connections_ has no structure. An
import between `PaymentService` and `UserNotificationFormatter` is exactly as
expressible as an import between `PaymentService` and `PaymentRepository`. The
language offers no resistance to the bad connection. It requires human
discipline — code reviews, conventions, architectural diagrams that live in a
wiki and are forgotten — to keep the bad connections out.

Human discipline at scale is unreliable. It degrades under pressure, turns over
with staff, and is invisible to automated tooling. The graph keeps growing.
Entropy wins.

The question geometric architecture answers is: **what if the language of
connections had structure that made bad connections harder to form than good
ones?**

---

## 2. The physical analogy: why geometry works

Consider a physical building. Every room has a position. Connections between
rooms — doors, windows, pipes, cables — are constrained by adjacency and
direction. You cannot run a water pipe from the basement directly to the roof
without passing through every floor in between. You cannot have a door between
two rooms that do not share a wall. The geometry of the building is not a rule
written in a manual. It is a property of space itself, and it enforces itself.

Physical buildings do not suffer from "spaghetti plumbing" — not because
plumbers are more disciplined than programmers, but because **the medium resists
it**. A pipe that jumps three floors is not just forbidden by convention; it is
visibly, physically expensive and awkward. The cost of the bad connection is
legible in the structure.

Geometric architecture imports this property into software design. It assigns
every component a position in a three-dimensional grid and then imposes the same
rule physical space imposes on buildings: **you may only connect to what is
immediately adjacent**. The cost of a long-range dependency becomes legible —
you have to propagate through every intermediate cell, naming and justifying
each step.

The geometry does not describe the architecture. **It enforces it**, the same
way a wall enforces separation between rooms.

---

## 3. The cellular automaton: locality as a first principle

The locality rule the SKILL prescribes is taken directly from cellular automata
— the computational model introduced by John von Neumann and popularized by
Conway's Game of Life. In a cellular automaton:

- The world is a grid of cells.
- Each cell has a state.
- A cell's next state depends **only on its immediate neighbors** — the Von
  Neumann neighborhood of face-adjacent cells.
- No cell can "see" or "reach" a distant cell in a single step.

The extraordinary result — known since the 1940s — is that **arbitrarily complex
global behavior emerges from purely local rules**. Conway's Game of Life,
operating on a two-dimensional grid with a six-word ruleset, can simulate a
Turing machine. Complexity is not achieved by allowing long-range connections.
It is achieved by **chaining short-range ones**.

This is the insight geometric architecture applies to software. A system does
not need unrestricted coupling to be powerful. It needs **well-structured local
coupling** that composes. The global behavior — the full capability of the
system — emerges from the chain of face-adjacent interactions, not from
individual components reaching across the entire graph.

The benefit is not just cleanliness. It is **predictability**. In a cellular
automaton, you can reason about a cell's behavior by looking at its six
neighbors. You do not need to understand the entire grid. The same property
holds in a geometrically structured software system: you can reason about a
component by reading its six neighbors. The cognitive surface area is bounded by
geometry, not by the size of the codebase.

---

## 4. The cognitive benefit: bounded reasoning surface

The benefit that matters most at scale is **bounded cognitive surface**.

In a fully connected graph of N components, understanding any one component
requires potentially understanding all N. The cognitive surface scales with the
size of the system. This is why large legacy codebases become unmaintainable —
not because the components are complex individually, but because the graph of
connections between them is too large to hold in a human mind.

In a geometrically constrained system, understanding a component requires
understanding at most its **six immediate neighbors**. That number is constant.
It does not grow with the system. A developer joining a 1,000-component codebase
has the same local reasoning surface as a developer working on a 10-component
one. The global behavior is complex — because it emerges from the chain of local
interactions — but the local reasoning is always bounded.

This is precisely the property that makes cellular automata tractable despite
their global complexity. Conway's Game of Life has no component that must "know
about" the whole grid. Each cell knows only its neighbors. Yet the global
behavior — gliders, oscillators, Turing-complete computation — emerges from that
local knowledge alone.

Geometric architecture imports that tractability into software. The grid does
not simplify the system's behavior. It simplifies the **act of reasoning about
the system** — and at scale, that is the constraint that matters most.

---

## 5. Worked example: a complete ESLint configuration

The SKILL summarizes which lint mechanisms map to which geometric rule. This
section walks through a working setup end-to-end. A complete config has three
layers, each answering one question.

### Layer 1 — define the cells

Every cell becomes an _element_: a name plus a glob that matches its files. Most
plugins resolve files first-match-wins, so list specific patterns before
catch-alls. Use a `*` capture in the glob to turn a path segment into a
matchable attribute — that is what makes X-axis (domain) rules expressible
without enumerating every domain by hand.

```js
settings: {
    'boundaries/elements': [
        // Z-axis: depth (front → back). Listed front-to-back for clarity.
        { type: 'controller', pattern: 'src/controllers/**' },
        { type: 'service',    pattern: 'src/services/**' },
        { type: 'repository', pattern: 'src/repositories/**' },

        // Y-axis: stratified engine. The facade is `mode: 'file'` so the
        // single entry point is distinguishable from its internals.
        { type: 'engine-facade', pattern: 'src/engine/index.ts', mode: 'file' },
        { type: 'engine-tier1',  pattern: 'src/engine/tier1/**' },
        { type: 'engine-tier2',  pattern: 'src/engine/tier2/**' },
        { type: 'engine-tier3',  pattern: 'src/engine/tier3/**' },

        // X-axis: domains. The `*` captures the folder name; the rule
        // below uses `captured.name` to compare two domains.
        { type: 'domain', pattern: 'src/domains/*/**', capture: ['name'] },
    ],
},
```

### Layer 2 — express direction and locality

A geometric rule is a `from → disallow.to` relation. Group rules by axis so
violation messages stay legible.

```js
rules: {
    'boundaries/dependencies': [
        'warn', // start as `warn`; promote per rule once violations clear
        {
            default: 'allow',
            rules: [
                // Z-axis: controller may not skip the service layer.
                {
                    from: { type: 'controller' },
                    disallow: { to: { type: 'repository' } },
                    message: 'Z-skip: route the call through a service.',
                },

                // Y-axis: lower engine tiers may not import higher ones.
                {
                    from: { type: 'engine-tier1' },
                    disallow: {
                        to: { type: ['engine-tier2', 'engine-tier3', 'engine-facade'] },
                    },
                    message: 'tier1 is foundation; it cannot reach upward.',
                },

                // External callers reach the facade, not the internals.
                {
                    from: { type: ['controller', 'service'] },
                    disallow: {
                        to: { type: ['engine-tier1', 'engine-tier2', 'engine-tier3'] },
                    },
                    message: 'Use the facade; do not reach into engine internals.',
                },

                // X-axis: each domain is isolated. The capture comparison
                // says "A may not import B when their captured names differ."
                {
                    from: { type: 'domain', captured: { name: '*' } },
                    disallow: {
                        to: {
                            type: 'domain',
                            captured: { name: '!{{from.captured.name}}' },
                        },
                    },
                    message:
                        'Cross-domain: {{from.captured.name}} → {{to.captured.name}}. Extract a shared neighbor.',
                },
            ],
        },
    ],
},
```

### Layer 3 — lock external boundaries

Two ESLint built-ins close the holes the boundaries plugin cannot.
`no-restricted-imports` pins each external SDK to exactly one wrapper cell.
`no-restricted-syntax` blocks runtime-computed imports and direct call-site
escape hatches (e.g. `fetch()` from a presentation cell that should call its
service neighbor instead).

```js
// SDK lockdown: only the declared wrapper imports the package.
{
    files: ['**/*.{js,ts}'],
    rules: {
        'no-restricted-imports': [
            'error',
            {
                paths: [
                    { name: 'pg',    message: 'Use repositories/db-client.ts.' },
                    { name: 'redis', message: 'Use repositories/cache-client.ts.' },
                ],
            },
        ],
    },
},
// The wrapper exempts itself.
{
    files: ['src/repositories/db-client.ts'],
    rules: { 'no-restricted-imports': 'off' },
},

// Dynamic imports with a non-literal path defeat static analysis.
{
    files: ['src/**/*.{js,ts}'],
    rules: {
        'no-restricted-syntax': [
            'error',
            {
                selector: 'ImportExpression[source.type!="Literal"]',
                message: 'Dynamic import path must be a string literal.',
            },
        ],
    },
},

// Call-site discipline: ban network calls from cells that should delegate.
{
    files: ['src/views/**', 'src/components/**'],
    rules: {
        'no-restricted-syntax': [
            'warn',
            {
                selector: "CallExpression[callee.name='fetch']",
                message: 'Z-skip: call a service neighbor instead of fetch().',
            },
        ],
    },
},
```

Build tooling and validation scripts that legitimately use computed paths or
reach into SDKs (directory walkers, codegen, test harnesses) need an explicit
exemption block — list them in `files` and turn the relevant rule `off`.

---

## 6. Reading a violation

A violation message tells you what the geometry sees. Translate it back to the
model and the fix becomes obvious:

| Lint message                                                | Geometric reading              | Standard fix                                             |
| ----------------------------------------------------------- | ------------------------------ | -------------------------------------------------------- |
| `from: controller, to: repository, disallow`                | Z-skip (wormhole through Z)    | Add or use the intermediate service cell                 |
| `from: tier1, to: tier3, disallow`                          | Y-skip (layer skip)            | Split tier1 or fix the tier boundary                     |
| `from: domain (name=billing), to: domain (name=invoice)`    | Cross-domain X-edge            | Extract a shared neighbor on the X-boundary              |
| `no-restricted-imports: 'pg'`                               | SDK wormhole                   | Route through the declared wrapper cell                  |
| `no-restricted-syntax: ImportExpression`                    | Hidden edge (runtime coupling) | Replace with a static registry of factories              |
| `no-restricted-syntax: CallExpression[callee.name='fetch']` | Call-site Z-skip               | Move the call into a service; the cell delegates instead |

When a rule fires, it is not the lint catching a typo — it is the geometry
refusing a connection.

---

## 7. Resolver gotchas

The boundaries plugin is only as good as its module resolver. Three things are
silently invisible to it unless configured:

- **TypeScript imports without an explicit extension** (`from './foo'` resolving
  to `foo.ts`). Install `eslint-import-resolver-typescript` and register it
  under `settings['import/resolver']`. Without this, every extension-less TS
  edge is a phantom — the rule never sees it.
- **Absolute paths used at runtime** (`from '/js/foo.js'` served from a static
  site root). The plugin treats these as filesystem-root paths and finds
  nothing. Either configure an alias resolver or normalize source files to
  relative imports.
- **Path aliases from `tsconfig.json`** (`@/services/foo`). The TS resolver
  above also reads `tsconfig.json` `paths` — but only when wired in.

If a known violation does not surface, suspect the resolver before the rule.

---

## 8. A caution: lint flags edges, not value

The lint plugin sees every disallowed edge as equally bad. The geometry does
not. A rule that fires on a routine, single-use call wrapped behind a thin
service can flag _ceremony_ rather than a real wormhole. Before promoting a rule
to `error`, ask: does the violation describe coupling that will hurt at scale,
or does the rule force every call into a wrapper whose body is a single
passthrough? Locality is about the coupling vocabulary, not about an abstraction
quota. If extracting a cell to satisfy the rule produces a service file with one
function and no logic, the rule is over-fitting — narrow the glob, lower the
severity, or accept the inline call where the destination is genuinely a
one-of-one.
