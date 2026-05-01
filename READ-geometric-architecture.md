# Geometric Architecture — In-Depth Explanation

> **The core claim:** Spaghetti architecture is not a discipline problem. It is
> a vocabulary problem. When a system has no spatial structure, every connection
> is equally expressible. Geometry fixes that by making long-range connections
> _harder to express than short-range ones_ — not through rules people can
> ignore, but through the structure of the language itself.

---

## 1. Why Software Rots: The Unconstrained Graph Problem

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

## 2. The Physical Analogy: Why Geometry Works

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

## 3. The Cellular Automaton: Locality as a First Principle

The locality rule this skill uses is taken directly from cellular automata — the
computational model introduced by John von Neumann and popularized by Conway's
Game of Life. In a cellular automaton:

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

This is the insight that geometric architecture applies to software. A system
does not need unrestricted coupling to be powerful. It needs **well-structured
local coupling** that composes. The global behavior — the full capability of the
system — emerges from the chain of face-adjacent interactions, not from
individual components reaching across the entire graph.

The benefit is not just cleanliness. It is **predictability**. In a cellular
automaton, you can reason about a cell's behavior by looking at its six
neighbors. You do not need to understand the entire grid. The same property
holds in a geographically structured software system: you can reason about a
component by reading its six neighbors. The cognitive surface area is bounded by
geometry, not by the size of the codebase.

---

## 4. The Three Axes and What They Encode

The grid is three-dimensional. Each axis encodes a distinct architectural
concern. This is not arbitrary — the three concerns are orthogonal in the
mathematical sense: changing position on one axis does not imply anything about
position on the others.

### Z — Depth (Environmental Layer)

The Z-axis runs from **front** (consumer-facing) to **back** (infrastructure).
It encodes how far a component is from the outside world. A REST handler sits at
Z=0. An ORM sits at Z=3. A raw database connection sits at Z=4.

This axis directly encodes the principle behind Clean Architecture and Hexagonal
Architecture: **domain logic must not know about infrastructure**. In geometric
terms: domain logic sits at some Z position, and infrastructure sits at a higher
Z. For domain logic to depend on infrastructure, it would need to form a
connection across multiple Z-layers — a direct violation of the locality rule.
The geometry makes the violation visible and costly before a single line of code
is written.

The Z-axis also encodes **dependency direction**. Dependencies flow from front
to back (Z increases). A connection that flows back-to-front is a direction
violation — it means a lower-level component is reaching up to control a
higher-level one, which is the classic inversion smell. The face role of the
Back face (outward calls) and the Front face (inward interface) make this
impossible to do accidentally: you would be connecting the wrong face to the
wrong face, and the geometry flags it immediately.

### X — Width (Domain / Bounded Context)

The X-axis runs left to right and encodes **business domain**. A `billing`
component sits at some X-position. `identity` sits at another. `inventory` at
another. Components in the same domain share an X-column. Components in
different domains occupy different columns.

The locality rule on this axis directly produces Domain-Driven Design's bounded
contexts. A component can only couple to the column immediately to its left or
right. To reach a domain two columns away, the signal must propagate through the
intermediate domain — or the intermediate domain must be refactored so that a
shared neighbor is extracted at the boundary.

This has a profound consequence for microservices. When each X-column becomes
independently deployable, the locality rule _automatically defines the correct
service boundaries_. You do not need to decide where to draw the microservice
line. The geometry draws it for you: a service boundary sits between any two
X-columns that have only face-to-face connections. No lateral jump, no shared
database hidden beneath both domains — because the hidden shared database would
be a violation.

### Y — Height (Abstraction Level)

The Y-axis runs from **top** (orchestrators, coordinators, use-case handlers) to
**bottom** (primitives, utilities, pure functions). It encodes how abstract or
foundational a component is.

The locality rule on this axis prevents two classic failure modes. First, it
prevents **god objects**: a component at Y=2 cannot directly reach Y=5 — it must
delegate to Y=3, which delegates to Y=4, and so on. Each level has a limited,
well-defined abstraction responsibility. Second, it prevents **upward
coupling**: a utility function at Y=5 cannot reach up to an orchestrator at Y=1
— that would require a face-direction violation (connecting Bottom face to
Bottom face, or forming an upward Z-direction connection). Low-level components
remain ignorant of the high-level world that uses them.

---

## 5. The Six Faces: Directionality as a First-Class Constraint

Most architectural models talk about coupling but not direction. The six-face
model adds direction as a structural constraint, not a convention.

Each face of a component's cell corresponds to one of the six possible
connection directions. Each face has a fixed semantic role:

- **Front** — the public interface that callers see. This is the only face
  through which incoming calls are valid.
- **Back** — the outward face for external calls, I/O, infrastructure access.
- **Top** — receives orchestration from above (the use-case layer calls down).
- **Bottom** — delegates to primitives below.
- **Left / Right** — cross-domain communication at the same abstraction level.

A connection is valid only when two matching faces connect: A's Back face
connects to B's Front face. Any other combination is a direction violation.

This is more powerful than it first appears. Consider the classic problem of
circular dependencies: A depends on B and B depends on A. In geometric terms,
A's Back face connects to B's Front face (valid), and B's Back face connects to
A's Front face (valid in isolation). But together they form a cycle — a loop in
the dependency graph. The face model catches this immediately: you cannot have
both A→B and B→A without one of the connections traversing a face in the wrong
direction. The geometry rules out cycles structurally.

This is the same reason a physical building does not have circular pipe loops
between rooms: the geometry of space makes it impossible to plumb from A to B
and simultaneously from B to A without the pipe visibly crossing itself. In
software, the face model provides the same self-crossing detection.

---

## 6. How Geometry Prevents Spaghetti: A Precise Account

Spaghetti architecture has several distinct failure modes. The geometry
addresses each one through a different structural constraint:

**Failure mode 1: Unrestricted long-range coupling.** Any component can import
any other. Results in a fully connected graph with no discernible structure.
_Geometric fix:_ Locality rule. Direct coupling costs distance. Long-range
connections require naming and building every intermediate cell. The cost is
legible and proportional to the architectural violation.

**Failure mode 2: Circular dependencies.** A depends on B depends on C depends
on A. Breaks build systems, prevents independent testing, makes change cascades
unpredictable. _Geometric fix:_ Face directionality. Every connection has a
direction encoded in which face it uses. Cycles require at least one connection
to traverse a face in the wrong direction — a direction violation that is
detectable before coding.

**Failure mode 3: Layer violations.** A UI component imports from the database
layer directly. A domain entity imports a logging framework. High-level policy
depends on low-level detail. _Geometric fix:_ Z-axis + face roles. A UI
component sits at Z=0; a database layer at Z=4. A direct connection is a Δ4 skip
— an immediate violation. The back face of Z=0 connects only to Z=1. You cannot
reach Z=4 without building through Z=1, Z=2, and Z=3.

**Failure mode 4: God objects.** One class or service accumulates
responsibilities across many concerns. Every other component depends on it. The
graph converges on a single node. _Geometric fix:_ The god cell rule. A cell
with all six faces occupied is a god object by definition. The face model makes
the symptom immediately visible: count the faces. If all six are used,
decompose. The geometry shows _which_ axis to decompose along: the axis with the
most connections is the seam.

**Failure mode 5: Hidden shared state.** Two domains secretly share a database,
a global variable, or a singleton. They appear decoupled in the call graph but
are tightly coupled through the shared state. _Geometric fix:_ The phantom
neighbor rule. Hidden shared state is a phantom neighbor — a coupling that
exists without a declared cell. Making it a real cell at a declared address
forces it into the open. Now it has a position, a set of faces, and its
connections are subject to the locality rule. The hidden coupling becomes an
explicit component — and explicit components can be reasoned about, refactored,
and replaced.

**Failure mode 6: Semantic drift.** Over time, a module accumulates
responsibilities that no longer match its name or position. The name says
`UserService`, but it now handles billing, notifications, and audit logging. The
graph topology tells the true story, but nobody reads graphs. _Geometric fix:_
The single-address rule. A component that has drifted semantically will
accumulate connections that pull it in multiple directions — toward different
X-domains, different Y-levels, or different Z-layers simultaneously. These show
up as diagonal connections or multi-axis violations. The geometry diagnoses
drift early, before it becomes technical debt.

---

## 7. What Emerges for Free

The most important property of the geometric model is what it produces without
explicit effort. When you enforce locality consistently, the following patterns
appear as consequences — not as additional rules you have to remember and apply:

**Clean / Hexagonal Architecture.** When Z-flow is strict (front-to-back only),
domain logic is automatically isolated from infrastructure. The geometry
produces the ports-and-adapters pattern without naming it.

**Domain-Driven Design bounded contexts.** When X-columns are independent (no
skips, no phantom neighbors), each column is a bounded context. The context
boundary is the face between column X and column X+1. The geometry draws the
boundary.

**Microservice boundaries.** When X-columns are independently deployable, the
locality rule defines correct service cuts. Services share only through their
adjacent face — the interface boundary — and nothing beneath it.

**Layered abstractions.** When Y-stratification is enforced (no orchestrator
reaching directly to a primitive), abstraction levels are automatically
respected. Each layer knows only the layer immediately below it.

**Explicit dependency chains.** When long-range connections must propagate,
every intermediate step becomes an explicit, named component. There are no
hidden paths through the graph. The chain from consumer to infrastructure is
always fully visible in the grid.

These are not aspirational outcomes that require additional architectural
effort. They are **geometric consequences** — they appear automatically when the
locality rule is followed. The architecture improves not because developers are
more disciplined, but because the grid makes the correct structure the path of
least resistance.

---

## 8. The Cognitive Benefit: Bounded Reasoning Surface

The final benefit is the one that matters most at scale: **bounded cognitive
surface**.

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

## 9. Mechanical Enforcement: From Mental Model to Lint

The grid is a thinking tool — but a useful subset of it can be turned into a
_checking_ tool. ESLint does not understand "address" or "Manhattan distance,"
but it understands file paths, import statements, and AST nodes. That is enough
to make the locality rule self-enforce on the parts that matter most.

### What lint can enforce

| Geometric rule                                                       | Lint mechanism                                                             | Tool                       |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------- |
| Coupling restricted to face-adjacent neighbors                       | `boundaries/dependencies` with `from`/`disallow`                           | `eslint-plugin-boundaries` |
| External code must use the engine facade, not internal tiers         | Declare each tier as an element; disallow imports from outside the engine  | `eslint-plugin-boundaries` |
| Y-stratified tiers (lower may not import higher)                     | One disallow rule per tier                                                 | `eslint-plugin-boundaries` |
| External SDKs reachable only via their wrapping cells                | `no-restricted-imports` with `paths` + per-file overrides for the wrappers | ESLint built-in            |
| Dynamic import path must be a literal (no runtime-computed coupling) | `no-restricted-syntax` matching `ImportExpression[source.type!="Literal"]` | ESLint built-in            |
| Tests not imported by production                                     | Dependencies rule disallowing `test` from prod elements                    | `eslint-plugin-boundaries` |

The pattern: each cell becomes an _element_ (a glob), and the directional rules
become `disallow` lists between element types. A wormhole — A→C skipping B —
surfaces as a glob of A trying to import a glob of C that the rule forbids.

### What lint cannot enforce

Three classes of geometric truth stay out of reach:

1. **Address quality.** Lint cannot judge whether a component is _placed
   correctly_. It only checks the consequences of placement. A component placed
   at the wrong (X, Y, Z) may still pass lint because its imports happen to fit
   the rule for its declared zone. Address quality is a review-time judgment.
2. **Behavioral coupling.** A pub/sub bus, a runtime registry, an event
   listener, or a global window can connect two cells without a static `import`
   statement. Lint sees no edge; the geometric model still recognizes one.
   Detection requires runtime tooling or convention.
3. **Face roles beyond direction.** Lint can express "A may import B." It cannot
   express "A's _Back_ face connects to B's _Front_ face." The directional
   semantics live in the human mental model, not in glob rules.

### How to roll it out without breaking the build

A complete rule set will catch real violations on first run. Promoting them all
to `error` immediately turns the dependency-guard rollout into a
mass-merge-block event. Two-phase rollout works better:

1. **Phase 1 — warnings.** Add every rule at `warn`. Lint exits zero, CI passes,
   violations become visible. The team sees which cells are misplaced.
2. **Phase 2 — promotion.** As each rule's existing violations are resolved (or
   accepted with explicit overrides), flip that rule to `error`. Promote one
   rule at a time so each promotion is a small, reviewable PR.

A rule that starts as `error` on a green codebase enforces forever. A rule that
starts as `error` on a codebase with twenty violations gets disabled the first
time someone needs to merge.

### Where the configuration lives

In practice, lint enforcement lives in `eslint.config.js` (or `.eslintrc`) at
the repo root. Each tier or layer of the geometric model becomes an _element_
glob; rules express directional constraints between them. Build tooling —
directory-walking validators, ESM-from-CJS configs, codegen scripts — should
be excluded from the dependency rules because computed paths are legitimate
there.

The geometric model is the _why_. The lint config is the _how_. The two should
be read together: when a rule fires, it is not the lint catching a typo — it is
the geometry refusing a connection.

---

## 10. Summary: What the Geometry Gives You

| Property                  | Without geometry                        | With geometry                                                   |
| ------------------------- | --------------------------------------- | --------------------------------------------------------------- |
| **Coupling vocabulary**   | All connections equally expressible     | Long-range connections are harder and more expensive to express |
| **Circular dependencies** | Possible anywhere, caught only by tools | Ruled out structurally by face directionality                   |
| **Layer violations**      | Caught only by convention or review     | Visible as ΔZ violations before code is written                 |
| **God objects**           | Identified by counting responsibilities | Identified by counting occupied faces                           |
| **Hidden shared state**   | Invisible until it breaks               | Must become a named cell subject to locality                    |
| **Semantic drift**        | Diagnosed by reading all imports        | Diagnosed by multi-axis violations in the grid                  |
| **Clean Architecture**    | Must be explicitly imposed and enforced | Emerges from Z-axis locality                                    |
| **Bounded contexts**      | Must be explicitly drawn and documented | Emerge from X-axis locality                                     |
| **Reasoning surface**     | Grows with the system                   | Constant: at most six neighbors                                 |
| **Discipline required**   | High — relies on humans, reviews, wikis | Low — the grid resists bad connections structurally             |

The geometry is not a diagram you draw once and hang on a wall. It is a living
coordinate system in which every design decision has a position, every
connection has a direction, and every violation has a measurable distance. The
architecture is not described by the geometry. **It is the geometry.**
