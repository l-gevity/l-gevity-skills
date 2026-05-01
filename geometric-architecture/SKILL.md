---
name: geometric-architecture
description: >
    Maps any software structure onto a 3D spatial grid where each component
    occupies a cell with a unique (X, Y, Z) address. Direct coupling is
    restricted to the six face-adjacent neighbors only — a cellular automaton
    locality rule. Long-range coupling must propagate through intermediate cells
    or be restructured. Use this skill when designing module boundaries,
    evaluating coupling, placing a new component, or deciding whether a
    dependency is structurally valid. Trigger whenever the user asks about
    coupling, module placement, service boundaries, dependency direction, or
    says something like "where does this belong?" or "is this dependency OK?"
---

# Geometric Architecture

> This skill fits a software structure into a 3D spatial grid and enforces
> **face-adjacent coupling only** — inspired by cellular automaton locality. For
> complexity measurement use `structural-simplification`. For coding discipline
> use `architecture-guidelines`.

> **Core Directives**
>
> 1. **Every component has exactly one address (X, Y, Z).** If it cannot be
>    placed without ambiguity, it is doing too many things — split it.
> 2. **Coupling is face-to-face only.** A component may directly depend on its
>    six immediate face-neighbors and nothing else.
> 3. **Long-range signals propagate — they never shortcut.** Route through
>    intermediate cells or extract a shared neighbor.
> 4. **Each face has a fixed role.** Coupling through the wrong face is a
>    direction violation regardless of distance.
> 5. **A fully occupied cell is a god cell only if its 6 faces serve unrelated
>    concerns.** A façade or orchestrator that uses all 6 faces along a coherent
>    axis (e.g., aggregating Y-below primitives) is fine. Decompose only when
>    face usage spans unrelated responsibilities.

---

## 1. The Three Axes

| Axis           | Span                   | What it encodes                                                     | Allowed step |
| -------------- | ---------------------- | ------------------------------------------------------------------- | ------------ |
| **Z — Depth**  | Front (0) → Back (max) | Environmental layer: consumer-facing → infrastructure               | Z ± 1        |
| **X — Width**  | Left → Right           | Domain / bounded context (a _graph_, embedded onto a line — see §3) | X ± 1        |
| **Y — Height** | Top (0) → Bottom (max) | Abstraction level: orchestrators → primitives                       | Y ± 1        |

A component's **address** is **(X, Y, Z)**. Two components are **neighbors** if
and only if their addresses differ by exactly **1 on exactly one axis** — the 3D
Von Neumann neighborhood — exactly **6 neighbors** in the interior, fewer at
grid edges.

---

## 2. The Six Faces

Each face defines both _who may connect_ and _in which direction_:

| Face       | Axis | Coupling role                                   |
| ---------- | ---- | ----------------------------------------------- |
| **Front**  | Z−   | Exposes public interface to callers (consumers) |
| **Back**   | Z+   | Calls external systems, infrastructure, I/O     |
| **Left**   | X−   | Receives from the adjacent domain               |
| **Right**  | X+   | Sends to the adjacent domain                    |
| **Top**    | Y−   | Receives orchestration from the layer above     |
| **Bottom** | Y+   | Delegates to the primitive or utility below     |

**A dependency is only valid when two matching faces connect.** A's Back face →
B's Front face is valid (B is the Z+1 neighbor of A). Any connection that does
not align face roles is a **direction violation**.

**Faces represent dependency direction, not data direction.** In event-driven
flows, an emitter couples to a subscriber the same way a synchronous caller does
— the dependency arrow points from the side that _names_ the other.

---

## 3. Placement Rules

Assign an address _before_ writing any code.

| Question                                           | Determines |
| -------------------------------------------------- | ---------- |
| Does it face consumers or infrastructure?          | Z position |
| Which business domain does it belong to?           | X position |
| Does it orchestrate others, or is it orchestrated? | Y position |

**Placement test:** If a component needs connections to non-adjacent cells to
function, it is either misplaced _or_ doing too many things. Try repositioning
first; if that fails, split the component along the axis of the violation.

**X is an ordering you choose, not one you discover.** Domains form a graph; the
X-axis is your _embedding_ of that graph onto a line. Place frequently-coupled
domains adjacent. When three or more domains converge on one, drop a **mediator
cell** on the shared X-face rather than forcing all neighbors onto a single
line. Mediators on X are the norm, not the exception.

---

## 4. The Locality Rule

> A component's behavior may only depend on the state of its immediate
> face-neighbors — exactly as in a cellular automaton.

| Connection                                                   | Manhattan distance¹ | Status                                                  |
| ------------------------------------------------------------ | ------------------- | ------------------------------------------------------- |
| Face-adjacent                                                | 1                   | ✅ Valid                                                |
| Diagonal _within one domain_ (ΔX = 0, ΔY + ΔZ = 2, each ≤ 1) | 2                   | ✅ Valid — normal layered call (e.g. controller → repo) |
| Diagonal _crossing domains_ (ΔX ≥ 1 _and_ ΔY ≥ 1 or ΔZ ≥ 1)  | ≥ 2                 | ⚠️ Justify or split A                                   |
| Layer skip (one axis ≥ 2)                                    | ≥ 2                 | ❌ Violation                                            |
| Long-range (multiple axes ≥ 2)                               | ≥ 3                 | ❌ Violation                                            |

¹ Manhattan distance = |ΔX| + |ΔY| + |ΔZ|

**Resolving violations — in order of preference:**

1. **Propagate.** Route A→B→C instead of A→C directly. The intermediate cell
   earns its place as a real component in the path.
2. **Extract.** If A and C both need X, move X to a new cell adjacent to both.
   The new cell becomes the canonical owner.
3. **Boundary event.** At a domain boundary (X-axis), place a mediator cell on
   the shared face. Neither domain reaches across; both speak to the mediator.

---

## 5. Structural Violations

| Violation                 | Symptom                                              | Fix                                                                                                                       |
| ------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **Wormhole**              | A → C skipping B (ΔZ ≥ 2)                            | Route through B, or merge B into A if B is vacuous                                                                        |
| **Domain reach**          | A depends on a non-adjacent domain (ΔX ≥ 2)          | Propagate or extract a shared neighbor                                                                                    |
| **Cross-domain diagonal** | Dependency spans X _and_ (Y or Z) simultaneously     | Split A, or extract a mediator on the shared X-face                                                                       |
| **Direction violation**   | Dependency flows against face role (e.g. Back→Front) | Invert via event, callback, or interface                                                                                  |
| **God cell**              | All 6 faces serve _unrelated_ concerns               | Decompose along the axis with the most concerns (a façade with all 6 faces serving one coherent axis is _not_ a god cell) |
| **Phantom neighbor**      | Coupling to an implicit or missing intermediate      | Make the intermediate cell an explicit component                                                                          |

---

## 6. What Emerges

Following the locality rule consistently produces known good patterns — for
free:

| Axis discipline                                       | Emergent pattern                              |
| ----------------------------------------------------- | --------------------------------------------- |
| Strict Z-flow (front→back only)                       | Approximates Clean / Hexagonal Architecture   |
| Independent X-columns                                 | Domain-Driven Design bounded contexts         |
| Independent X-columns + deployability                 | Microservice boundaries                       |
| Y-stratification (no orchestrator↔primitive shortcut) | Layered abstractions, no god classes          |
| Propagation over shortcuts                            | Explicit dependency chains, no hidden globals |

---

## 7. Decision Protocol

When adding a dependency from A to B:

1. **Look up addresses.** Confirm (Xₐ, Yₐ, Zₐ) and (X_b, Y_b, Z_b).
2. **Compute deltas.** ΔX = |Xₐ−X_b|, ΔY = |Yₐ−Y_b|, ΔZ = |Zₐ−Z_b|.
3. **Classify:**

| ΔX + ΔY + ΔZ | Axes with Δ > 0 | ΔX  | Verdict                                              |
| ------------ | --------------- | --- | ---------------------------------------------------- |
| 1            | 1               | any | ✅ Proceed                                           |
| 2            | 1               | any | ❌ Layer/domain skip — propagate or extract          |
| 2            | 2               | 0   | ✅ Same-domain layered call (e.g. controller → repo) |
| 2            | 2               | ≥ 1 | ⚠️ Cross-domain diagonal — justify or split A        |
| ≥ 3          | any             | any | ❌ Long-range — redesign required                    |

4. **Check face alignment.** Does A's connecting face match B's receiving face?
5. **If violation**, state: _"Locality Violation at Δ(X,Y,Z) = (ΔX, ΔY, ΔZ).
   Nearest valid path: [intermediate cell(s)]. Alternative: extract [shared
   neighbor]."_
