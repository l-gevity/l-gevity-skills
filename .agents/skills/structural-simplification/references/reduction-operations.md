# Structural Simplification — Reduction Operations

Reference for [SKILL.md](../SKILL.md) §4. Read when proposing or reviewing a
simplification. Measuring the four deltas of a given candidate needs only
SKILL.md.

## 4. Reduction Operations

### D↓ — Reduce Diversity

| Operation          | Mechanism                                                                  |
| ------------------ | -------------------------------------------------------------------------- |
| **Unification**    | Merge distinct things that serve the same role                             |
| **Normalization**  | Reduce variants to a single canonical form                                 |
| **Generalization** | Replace N specific cases with one general case                             |
| **Abstraction**    | Hide variation behind a common interface                                   |
| **Symmetrization** | Impose mirror structure so subsystems become interchangeable               |
| **Deduplication**  | Eliminate redundant copies                                                 |
| **Patternization** | Apply a recurring structure — differences become instances, not exceptions |
| **Cohesion**       | Group what changes together; the subsystem expresses one concept           |

> [!WARNING] **Unification guardrail — referencing-list uniformity.** Merging
> vocabulary items (rights, routes, types, statuses, config keys) is safe only
> when every member is uniform with respect to every *other* list that
> references them — ban/allow lists, separation-of-duties pairs, fixed scopes,
> party or tenant restrictions, protocol mappings. A merged item cannot be
> half-banned or half-granted: one non-uniform member blocks the merge or must
> stay separate. Enumerate the referencing lists and check uniformity before
> claiming a D↓ or n↓ from Unification, Generalization, or Merging.

### K↓ — Reduce Coupling

| Operation               | Mechanism                                                             |
| ----------------------- | --------------------------------------------------------------------- |
| **Encapsulation**       | Hide internals so others cannot form dependencies on them             |
| **Indirection**         | Insert a mediator — two subsystems no longer reference each other directly |
| **Inversion**           | Flip a dependency (depend on abstraction, not concretion)             |
| **Stratification**      | Impose directed acyclic ordering (layering)                           |
| **Temporal decoupling** | Replace synchronous direct binding with asynchronous mediation        |

### P↓ — Reduce Depth

| Operation          | Mechanism                                                                |
| ------------------ | ------------------------------------------------------------------------ |
| **Flattening**     | Merge adjacent layers with no independent reason to exist                |
| **Inlining**       | Pull deep content up to the level that uses it                           |
| **Direct binding** | Replace A→B→C with A→C where B adds no value (raises K — verify product) |

> [!WARNING] A **facade** hides chain depth; it does not reduce it. Verify
> actual P, not visible P.

### n↓ — Reduce Quantity

| Operation       | Mechanism                                                           |
| --------------- | ------------------------------------------------------------------- |
| **Elimination** | Remove a subsystem entirely — absolute edge count can drop with every deleted incident edge; recompute both edge count and density |
| **Merging**     | Collapse two subsystems into one (may raise internal K — verify product) |

### Multi-axis — Reduce Simultaneously

| Operation                  | Mechanism                                                    |
| -------------------------- | ------------------------------------------------------------ |
| **Decomposition**          | Split along natural seams → K↓, D↓, P↓ in local subgraphs    |
| **Factoring**              | Extract common subsystem → D↓ (dedup) + K↓ (N deps collapse to 1) |
| **Separation of concerns** | One responsibility per subsystem → D↓ internal + K↓ external |
| **Aspect extraction**      | Move an aspect interleaved in n subsystems into one mechanism → K: n×m edges → n + m; D↓ only where the copies had diverged; P +1 on the aspect path; n +1 |

---
