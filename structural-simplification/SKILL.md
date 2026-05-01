---
name: structural-simplification
description:
    A first-principles framework for reducing structural complexity in any
    domain — code, data models, workflows, UI layouts, org structures, or
    temporal processes. Use this skill when evaluating a refactoring, designing
    a restructuring, or deciding whether a proposed change makes a system
    simpler or more complex.
---

# Structural Simplification

> This skill governs **structural complexity analysis and reduction**. It
> applies universally to any structure — logical, spatial, temporal, or
> organizational. For coding style see `coding-standard`; for design discipline
> see `architecture-guidelines`.

> **Core Directives**
>
> 1. **Complexity has four axes**: D (diversity), K (coupling), P (depth), n
>    (quantity). A change that worsens any axis without improving another is not
>    a simplification.
> 2. **Compare before and after**: record ΔD, ΔK, ΔP, Δn before committing to
>    any restructuring. Intuition is not a metric.
> 3. **Conform over customize**: reusing an existing pattern — even at local
>    cost — eliminates a unique shape from the vocabulary and shrinks D
>    globally.
> 4. **Delete over mitigate**: removing a part or special case beats handling
>    it.
> 5. **If no axis improves while any worsens, it is not a simplification.**

---

## 1. The Complexity Model

Structural complexity is analyzed across four axes:

| Axis          | Symbol | What it counts                                           | Measurability        |
| ------------- | ------ | -------------------------------------------------------- | -------------------- |
| **Diversity** | `D`    | Distinct patterns, shapes, or concepts in the vocabulary | Requires judgment    |
| **Coupling**  | `K`    | Relationship density: `edges / (n × (n−1))`              | Countable from graph |
| **Depth**     | `P`    | Longest chain from source to sink                        | Countable from graph |
| **Quantity**  | `n`    | Total number of parts                                    | Countable from graph |

The model is domain-agnostic. _Parts_ are any discrete unit (components, steps,
screens, roles, fields). _Relationships_ are any connection (dependencies,
flows, sequences, adjacencies, authority lines).

Complexity grows when multiple axes increase simultaneously — the interaction is
worse than any single axis alone. Evaluate each axis independently; do not
collapse them into a single number.

---

## 2. Domain Mapping

| Domain       | Parts (nodes)                  | Relationships (edges)                   |
| ------------ | ------------------------------ | --------------------------------------- |
| Code         | Components, modules, functions | Dependencies, calls, imports            |
| Data model   | Entities, fields, types        | References, joins, constraints          |
| Workflow     | Steps, stages, decisions       | Transitions, triggers, sequencing       |
| UI / spatial | Screens, regions, elements     | Navigation, data flow, visual links     |
| Organization | Roles, teams, systems          | Authority, communication, data exchange |
| Temporal     | Events, states, phases         | Causal or sequential ordering           |

---

## 3. Heuristic Checks

Fast proxies — not substitutes for measurement:

| Check          | Signal                                                     |
| -------------- | ---------------------------------------------------------- |
| **Symmetry**   | Structure more uniform after → D↓                          |
| **Boundary**   | Fewer relationships crossing boundaries → K↓               |
| **Cycle**      | Dependency cycle broken → K↓ (cycles are maximum coupling) |
| **Chain**      | Fewer hops source-to-sink → P↓                             |
| **Count**      | Fewer parts → n↓                                           |
| **Vocabulary** | Describable with fewer concepts → D↓                       |

---

## 4. Reduction Operations

### D↓ — Reduce Diversity

| Operation          | Mechanism                                                                  |
| ------------------ | -------------------------------------------------------------------------- |
| **Unification**    | Merge distinct things that serve the same role into one                    |
| **Normalization**  | Reduce variants to a single canonical form                                 |
| **Generalization** | Replace N specific cases with one general case                             |
| **Abstraction**    | Hide variation behind a common interface                                   |
| **Symmetrization** | Impose mirror structure so parts become interchangeable                    |
| **Deduplication**  | Eliminate redundant copies                                                 |
| **Patternization** | Apply a recurring structure — differences become instances, not exceptions |

### K↓ — Reduce Coupling

| Operation               | Mechanism                                                             |
| ----------------------- | --------------------------------------------------------------------- |
| **Encapsulation**       | Hide internals so others cannot form dependencies on them             |
| **Indirection**         | Insert a mediator — two parts no longer reference each other directly |
| **Inversion**           | Flip a dependency (depend on abstraction, not concretion)             |
| **Stratification**      | Impose directed acyclic ordering (layering)                           |
| **Cohesion**            | Group what changes together — severs external links as side effect    |
| **Temporal decoupling** | Replace direct calls with events or queues                            |
| **Edge elimination**    | Remove a relationship entirely                                        |

### P↓ — Reduce Depth

| Operation          | Mechanism                                                                |
| ------------------ | ------------------------------------------------------------------------ |
| **Flattening**     | Merge adjacent layers that have no independent reason to exist           |
| **Inlining**       | Pull deep logic up to the level that needs it                            |
| **Direct binding** | Replace A→B→C with A→C where B adds no value (raises K — verify product) |

> [!WARNING] A **facade** hides depth; it does not reduce it. Verify actual P,
> not visible P.

### n↓ — Reduce Quantity

| Operation       | Mechanism                                                           |
| --------------- | ------------------------------------------------------------------- |
| **Elimination** | Remove a part entirely — absolute coupling drops as `K × n²`        |
| **Merging**     | Collapse two parts into one (may raise internal K — verify product) |

### Multi-axis — Reduce Simultaneously

| Operation                  | Mechanism                                                    |
| -------------------------- | ------------------------------------------------------------ |
| **Decomposition**          | Split along natural seams → K↓, D↓, P↓ in local subgraphs    |
| **Factoring**              | Extract common part → D↓ (dedup) + K↓ (N deps collapse to 1) |
| **Separation of concerns** | One responsibility per unit → D↓ internal + K↓ external      |

---

## 5. Geometric Constraint

The most natural way to bound all four axes simultaneously is to treat the
structure _as if it were a physical object_ — with surfaces, orientation, finite
volume, and locality. Physical geometry is a **complexity budget**: it imposes
limits that abstract structures lack by default.

### The constraints and what they bound

| Physical property                       | What it forces                                                                                                                        | Axis |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| **Surface / interface**                 | Only the outside is touchable — internals are unreachable without passing through a surface                                           | K↓   |
| **Orientation** (front/back/top/bottom) | Flow is directed — front faces the consumer, back faces infrastructure. No wire runs from display through motherboard back to display | P↓   |
| **Finite volume**                       | A container can only hold so many parts before it is full — growth requires explicit expansion                                        | n↓   |
| **Locality / adjacency**                | Distant parts cannot easily interact — long-range coupling requires visible, costly effort (a cable, a pipe)                          | K↓   |
| **Form factor**                         | Parts must conform to the container's shape — bespoke shapes do not fit                                                               | D↓   |

### How to apply

- **Layer front-to-back**: consumer-facing at the front, infrastructure at the
  back; dependencies flow one direction. Reverse-flow relationships are
  violations — eliminate or make them explicit.
- **Group laterally by neighborhood**: parts that collaborate sit adjacent;
  unrelated domains sit apart.
- **Bound the surface**: every structure has an enumerable set of entry points;
  everything else is internal.
- **Cap the volume**: when a part outgrows its container, decompose — do not
  stretch the container.
- **Enforce locality**: long-range relationships are like cables across a room —
  they must justify the cost.

### Decomposition strategies

Two complementary ways to partition a structure:

| Strategy         | Cut direction | What it isolates                           | Example                             |
| ---------------- | ------------- | ------------------------------------------ | ----------------------------------- |
| **Subsystem**    | Vertical      | A cohesive, locally bound part             | Auth module, billing service        |
| **Aspectsystem** | Horizontal    | A cross-cutting concern spanning all parts | Logging, validation, error handling |

A subsystem is a **neighborhood** — spatially bounded, internally cohesive, with
a defined surface. An aspectsystem is a **filter** — it selects a property
across the entire structure, like "all red pixels of an image."

Both reduce complexity, but through different axes:

- Subsystem decomposition → K↓ (severs cross-boundary coupling), n↓ (per local
  scope)
- Aspectsystem decomposition → D↓ (unifies scattered variants of the same
  concern)

Choose subsystem when the seam is **between domains**. Choose aspectsystem when
the seam is **within a shared concern**. Each resulting partition is itself a
structure — evaluate D, K, P, n recursively to assess its internal complexity
independently.

> [!NOTE] The power of geometric constraint is that humans already have spatial
> intuition. "The database is behind the API" is instantly understood — no rule
> book required. The metaphor enforces the discipline.

---

## 6. Trade-off Matrix

Reducing one axis often raises another. Classify before committing:

| Restructuring         | D   | K   | P       | n   | Typical net      |
| --------------------- | --- | --- | ------- | --- | ---------------- |
| Add abstraction layer | ↑   | ↓   | ↑       | ↑   | Measure          |
| Flatten two layers    | —   | ↑   | ↓       | ↓   | Measure          |
| Extract common part   | ↓   | ↓   | —       | ↑   | Usually ↓C       |
| Bypass a layer        | —   | ↑   | ↓       | ↓   | Measure          |
| Add facade            | ↑   | —   | hides P | ↑   | Verify actual P  |
| Introduce mediator    | ↑   | ↑   | ↑       | ↑   | Rarely justified |
| Merge two modules     | ↓   | ↑   | ↓       | ↓   | Measure          |
| Split one module      | ↓   | ↓   | ↑       | ↑   | Measure          |

---

## 7. Asymmetric Trade-offs

Valid when the net effect across axes is positive despite a local cost.

### 7a. Conformance (Pattern Alignment)

Accept local overengineering to eliminate a unique structural shape from D. One
snowflake among ten uniform parts inflates D disproportionately — its removal
has outsized global effect.

### 7b. Scope Reduction (Deletion)

Remove special functionality if its structural footprint exceeds its utility.
Special cases are complexity multipliers: D↑ (unique patterns), K↑ (conditional
paths), P↑ (extended chains), n↑ (supporting parts). The cost of a feature is
not its own code — it is every special case it forces elsewhere.

### 7c. Atomicity Requirements (Multi-System Orchestration)

When an operation coordinates multiple external systems, the atomicity decision
has direct structural cost. Decide **before implementation** — see
`architecture-guidelines` §5 _Atomicity_ for when atomicity is required.

| Decision             | Structural effect | Action                                        |
| -------------------- | ----------------- | --------------------------------------------- |
| Atomicity required   | K↑ P↑             | Accept coupling; use fail-fast / compensation |
| Eventual consistency | K↓ P↓             | Document acceptable partial-failure states    |

**Anti-Pattern:** Designing multi-step operations without deciding atomicity
first.

---

## 8. Decision Protocol

1. **Model** before-state. Record D₁, K₁, P₁, n₁.
2. **Model** after-state. Record D₂, K₂, P₂, n₂.
3. **Compare** per-axis deltas: ΔD, ΔK, ΔP, Δn.
4. **Classify**:

| Pattern                           | Action                          |
| --------------------------------- | ------------------------------- |
| All axes improve or hold          | Proceed                         |
| Mixed (some improve, some worsen) | Consult §6 trade-offs, apply §7 |
| No axis improves                  | REJECT or redesign              |

> [!IMPORTANT] If no axis improves, state: _"Complexity Warning: ΔD [X], ΔK [Y],
> ΔP [Z], Δn [W]. A simpler alternative is [...]."_
