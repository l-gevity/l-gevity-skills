# Geometric Software Architecture

A 3-D spatial coordinate system for your dependency graph. Every component gets an address `(X, Y, Z)` and may only couple to face-adjacent neighbors; long-range and cyclic dependencies become structurally hard to express — the way a building's geometry resists impossible plumbing.

## Why use this

- **Long-range coupling becomes structurally hard to express.** The grid resists wormholes the way a building resists pipes that jump three floors.
- **Circular dependencies become structurally impossible.** Cycles require a connection that crosses a face the wrong way — the geometry refuses.
- **Existing tangles can be diagnosed.** God objects, layer violations, and cross-domain coupling each surface as named defects with standard fixes.
- **Reasoning surface stays bounded.** Each component has at most six neighbors regardless of codebase size.
- **Established patterns emerge for free.** Clean architecture, DDD bounded contexts, and layered abstractions are consequences of the rule, not extra rules to remember.

## Fundamental principles

Software is, by default, an unconstrained graph: any module may import any other module with a single line. The language offers no resistance to bad connections. Geometry imposes structure on the *vocabulary of connections* — the way physical space imposes structure on a building's plumbing.

- **Position is meaningful.** Each component lives at *(X, Y, Z)* — domain, abstraction level, depth. The address says where it belongs and what it may touch.
- **Locality is a constraint, not a guideline.** Coupling is allowed only between face-adjacent cells. Long-range edges become structurally expensive to express, not merely discouraged.
- **Faces have direction.** Every connection runs from one cell's Back face to its neighbor's Front face. Cycles require a face crossed the wrong way — the geometry forbids them.
- **Global complexity emerges from local rules.** Conway's Game of Life is Turing-complete with a six-word ruleset and only nearest-neighbor interactions. Software does not need unrestricted coupling to be powerful — it needs well-structured local coupling that composes.

The geometry doesn't *describe* the architecture — it *enforces* it, the way a wall enforces separation between rooms.

## How to use

The skill has two modes: **audit** an existing dependency graph, or **design** the address of a new component.

1. **Identify the structure or proposal.** An existing tangle to diagnose, or a new component whose address you need to assign.
2. **Prompt the AI.**

   > *Audit:* "Diagnose the dependency graph in `src/`. Flag layer skips, cycles, god cells, and cross-domain coupling."
   >
   > *Design:* "Where does `OrderShipmentNotifier` belong in (X, Y, Z)? It's currently imported by both the order and notification domains."

3. **Read the verdict.** The skill names the geometric defect (Z-skip, X-edge, god cell, phantom neighbor) and gives the standard fix.
4. **Apply the fix.** Add the missing intermediate cell, extract a shared neighbor, decompose the god cell along its busiest axis.

## The three axes and six faces

Every component gets an address `(X, Y, Z)` and exposes six faces with fixed semantic roles.

### Axes — where a cell lives

| Axis  | Encodes           | Direction                                                              |
|-------|-------------------|------------------------------------------------------------------------|
| **X** | Domain / context  | One column per business domain; siblings stay isolated.                |
| **Y** | Abstraction level | Orchestrators (top) → primitives (bottom).                             |
| **Z** | Depth / layer     | Consumer (Z=0) → infrastructure (Z=N). Dependencies flow Z-increasing. |

### Faces — how a cell connects

| Face           | Role                                                       |
|----------------|------------------------------------------------------------|
| **Front**      | Public interface — the only valid face for incoming calls. |
| **Back**       | Outward calls, I/O, infrastructure access.                 |
| **Top**        | Receives orchestration from above.                         |
| **Bottom**     | Delegates to primitives below.                             |
| **Left/Right** | Same-tier neighbors (cross-domain siblings).               |

A connection is valid only when **A's Back connects to B's Front**. Anything else is a direction violation; cycles are impossible without one.

## Common defects

The geometry refuses certain connections. When it does, the violation has a name and a standard fix.

| Defect                  | Geometric reading                                    | Standard fix                                                    |
|-------------------------|------------------------------------------------------|-----------------------------------------------------------------|
| **Z-skip**              | Wormhole through Z (e.g. controller → repository).   | Insert or use the intermediate cell.                            |
| **Y-skip**              | Layer violation (lower tier → higher tier).          | Split the cell or fix the tier boundary.                        |
| **Cross-domain X-edge** | Sibling domains coupling directly.                   | Extract a shared neighbor on the X-boundary.                    |
| **God cell**            | All six faces occupied; the cell does too much.      | Decompose along the axis with the most edges.                   |
| **Phantom neighbor**    | Hidden coupling via globals or runtime registries.   | Promote the implicit dependency to a real cell with an address. |
| **SDK wormhole**        | Many cells importing the same external SDK directly. | Route through a single wrapper cell.                            |

When a rule fires, it is not the lint catching a typo — it is the geometry refusing a connection.

## When to skip

Routine logic inside existing modules, bug fixes, content edits, CSS-only changes, dependency bumps, trivial renames. The framework earns its keep when the dependency graph itself is being shaped or diagnosed.

## Next steps

- See [SKILL.md](./SKILL.md) for the operational reference (full failure-mode table, ESLint mechanism mapping, lint can/cannot-enforce list, rollout strategy).
- For first-principles rules on what goes inside a module, see [`architecture-guidelines`](../architecture-guidelines/).
- For evaluating whether a structural change actually reduces complexity, see [`structural-simplification`](../structural-simplification/).
- Run an audit on the subsystem you suspect is most tangled — the verdict often names the geometric defect on the first pass.
