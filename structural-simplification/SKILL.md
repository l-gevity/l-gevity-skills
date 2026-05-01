---
name: structural-simplification
description: >-
    A domain-agnostic complexity model and decision protocol. Complexity is
    treated as a 4-axis vector — D (diversity), K (coupling), P (depth), n
    (quantity) — and any proposed restructuring is judged by its per-axis effect
    rather than by intuition. Applies to code, data models, workflows, UI
    layouts, organizational structures, and temporal processes. TRIGGER when:
    evaluating a refactoring, designing a restructuring, or deciding whether a
    proposed change makes a system simpler or more complex. SKIP for: trivial
    renames, content edits, dependency bumps, isolated bug fixes that touch no
    structure. For coding style see `coding-standard`; for module-level design
    discipline see `architecture-guidelines`; for spatial dependency-graph
    constraints see `geometric-architecture`.
---

# Structural Simplification

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

Treating a structure as a physical object — with surfaces, orientation, finite
volume, and locality — bounds all four axes simultaneously: surface and locality
cap K, orientation caps P, volume caps n, and conforming form factors cap D.
Subsystem decomposition (vertical) reduces K and n; aspect- system decomposition
(horizontal) reduces D.

For a full treatment of spatial dependency-graph constraints — placement
addresses, face directionality, locality rules, and lint enforcement — see
`geometric-architecture`.

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
