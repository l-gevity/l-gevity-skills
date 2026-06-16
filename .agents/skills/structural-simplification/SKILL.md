---
name: structural-simplification
description: >-
    A domain-agnostic complexity model and decision protocol. Complexity is
    treated as a 4-axis vector — D (diversity), K (coupling), P (depth), n
    (quantity) — and any proposed restructuring is judged by its per-axis effect
    rather than by intuition. Applies to code, project organization, runtime
    topology, data models, workflows, UI layouts, organizational structures,
    and temporal processes. TRIGGER when: evaluating a refactoring, designing
    a restructuring, or deciding whether a proposed change makes a system
    simpler or more complex. SKIP for: trivial renames, content edits,
    dependency bumps, isolated bug fixes that touch no structure. For
    module-level design discipline see `architecture-guidelines`; for spatial
    dependency-graph constraints see `geometric-architecture`.
---

# Structural Simplification

> **Core Directives**
>
> 1. **Complexity has four axes**: D (diversity), K (coupling), P (depth), n
>    (quantity). Score each independently; never collapse into a single number.
> 2. **Compare before and after.** Intuition is not a metric.
> 3. **Conform when semantics match.** Reusing an existing pattern shrinks D
>    globally only when the semantics, lifecycle, and constraints actually fit.
> 4. **Remove over mitigate, safely.** Removing a part or special case beats
>    handling it when functionality, migration, rollback, and external
>    constraints permit removal.

---

## Reporting Vocabulary

The skill may reason with axis symbols, but reports are for a coding agent that
must choose an edit, test, lint rule, or rejection. Use the coder-facing field
names below in every emit block, gate table, and cross-skill citation.

| Internal symbol  | Coder-facing field used in reports                                    |
| ---------------- | --------------------------------------------------------------------- |
| `ΔD` (diversity) | **Component-kinds Δ** — distinct component/interface/pattern types added or removed |
| `ΔK` (coupling)  | **Dependency-edges Δ** — imports, calls, package edges, or runtime links added or removed |
| `ΔP` (depth)     | **Max-chain-depth Δ** — longest import/call/build chain before vs after |
| `Δn` (quantity)  | **Module-count Δ** — files, modules, jobs, services, or instances added or removed |
| Wormhole         | **Layer-skip violation** (term carried over from `geometric-architecture`) |

**Naming guardrails.** `P` is **max-chain-depth**, never "depth" alone — bare "depth" collides with the layer axis in `geometric-architecture`. Symbols appear in exactly three places: inside a formula, inside this table, and inside §§1–7 (the internal model). Anywhere else in narrative, use the coder-facing field name.

> **2026-05-22 — emit field-name change.** Field labels in emit blocks
> changed from internal symbols to coder-facing fields:
> `ΔD → Component-kinds Δ`, `ΔK → Dependency-edges Δ`,
> `ΔP → Max-chain-depth Δ`, `Δn → Module-count Δ`.
> Any downstream consumer (script, hook, agent prompt) that pattern-matched
> on the old labels must update. Internal symbols remain in §§1–7 and in
> formulas; they are no longer emitted in reports.

---

## 1. The Complexity Model

| Axis          | Symbol | What it counts                      | Measurement recipe                                                    |
| ------------- | ------ | ----------------------------------- | --------------------------------------------------------------------- |
| **Diversity** | `D`    | Distinct patterns, shapes, concepts | Count distinct patterns / vocabulary items in the structure           |
| **Coupling**  | `K`    | Relationship count and density      | Count edges, then compute density (`edges / (n × (n−1))` for directed graphs where `n > 1`) after defining edge kind and direction |
| **Depth**     | `P`    | Longest chain from source to sink   | Longest path from any origin to any terminus in the DAG               |
| **Quantity**  | `n`    | Total number of parts               | Direct count of parts (use §2 to identify parts in your domain)       |

Domain-agnostic. *Parts* = any discrete unit; *relationships* = any
connection (dependency, flow, sequence, authority). Multi-axis interactions
usually cost more than any single-axis change alone; verify against the
domain's actual constraints.

> [!IMPORTANT] **Cycles are property violations, not just high K.** A cycle
> breaks the DAG assumption only when the chosen projection is required to be
> acyclic, such as imports, ownership, authority, or layer dependencies. See §5
> for the geometric framing that rules those cycles out; `geometric-architecture`
> §2 enforces them as lint. If the domain intentionally contains cycles
> (feedback loops, state machines, workflows), define the acyclic projection or
> cycle semantics before scoring.

---

## 2. Domain Mapping

| Domain                | Parts (nodes)                                       | Relationships (edges)                                                       |
| --------------------- | --------------------------------------------------- | --------------------------------------------------------------------------- |
| Code                  | Components, modules, functions                      | Dependencies, calls, imports                                                |
| Project organization  | Repos, packages, workspaces, build targets          | Package dependencies, version constraints, build-time references, ownership |
| Runtime / deployment  | Services, processes, containers, instances, threads | RPC/HTTP calls, message flows, network paths, replication, lifecycle order  |
| Data model            | Entities, fields, types                             | References, joins, constraints                                              |
| Workflow              | Steps, stages, decisions                            | Transitions, triggers, sequencing                                           |
| UI / spatial          | Screens, regions, elements                          | Navigation, data flow, visual links                                         |
| Organization (people) | Roles, teams, systems                               | Authority, communication, data exchange                                     |
| Temporal              | Events, states, phases                              | Causal or sequential ordering                                               |

---

## 3. Heuristic Checks

Fast proxies — not substitutes for measurement.

| Check            | Signal                                                  | Axis          |
| ---------------- | ------------------------------------------------------- | ------------- |
| **Symmetry**     | Structure more uniform after                            | D↓            |
| **Vocabulary**   | Describable with fewer concepts                         | D↓            |
| **Boundary**     | Fewer relationships crossing boundaries                 | K↓            |
| **Cycle broken** | Dependency cycle eliminated                             | K↓ + §1 fault |
| **Chain**        | Fewer hops source-to-sink                               | P↓            |
| **Count**        | Fewer parts                                             | n↓            |
| **Ripple**       | Typical change in this area touches many parts          | K             |

---

## 4. Reduction Operations

### D↓ — Reduce Diversity

| Operation          | Mechanism                                                                  |
| ------------------ | -------------------------------------------------------------------------- |
| **Unification**    | Merge distinct things that serve the same role                             |
| **Normalization**  | Reduce variants to a single canonical form                                 |
| **Generalization** | Replace N specific cases with one general case                             |
| **Abstraction**    | Hide variation behind a common interface                                   |
| **Symmetrization** | Impose mirror structure so parts become interchangeable                    |
| **Deduplication**  | Eliminate redundant copies                                                 |
| **Patternization** | Apply a recurring structure — differences become instances, not exceptions |
| **Cohesion**       | Group what changes together; the unit expresses one concept                |

### K↓ — Reduce Coupling

| Operation               | Mechanism                                                             |
| ----------------------- | --------------------------------------------------------------------- |
| **Encapsulation**       | Hide internals so others cannot form dependencies on them             |
| **Indirection**         | Insert a mediator — two parts no longer reference each other directly |
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
| **Elimination** | Remove a part entirely — absolute edge count can drop with every deleted incident edge; recompute both edge count and density |
| **Merging**     | Collapse two parts into one (may raise internal K — verify product) |

### Multi-axis — Reduce Simultaneously

| Operation                  | Mechanism                                                    |
| -------------------------- | ------------------------------------------------------------ |
| **Decomposition**          | Split along natural seams → K↓, D↓, P↓ in local subgraphs    |
| **Factoring**              | Extract common part → D↓ (dedup) + K↓ (N deps collapse to 1) |
| **Separation of concerns** | One responsibility per unit → D↓ internal + K↓ external      |

---

## 5. Geometric Constraint

Treating a dependency structure as a physical object — with surfaces,
orientation, finite volume, and locality — helps bound all four axes: surface
and locality cap K, orientation caps P, volume caps n, and conforming form
factors cap D. Subsystem decomposition (vertical) can reduce K and n;
aspect-system decomposition (horizontal) can reduce D. In dependency graphs
that require directionality, cycles require a back-to-back face; the geometry
rules those cycles out without a separate axiom.

For the full spatial treatment — placement addresses, face directionality,
locality rules, lint enforcement — see `geometric-architecture`.

---

## 6. Trade-off Matrix

Reducing one axis usually raises another. Examples lean software but the
moves apply to any structure.

| Restructuring                                       | D   | K        | P       | n   | Verdict                                                       |
| --------------------------------------------------- | --- | -------- | ------- | --- | ------------------------------------------------------------- |
| Add abstraction tier — ≥3 concrete instances        | ↑   | ↓        | ↑       | ↑   | Candidate proceed (§7a Conformance); verify semantics match   |
| Add abstraction tier — <3 instances or speculative  | ↑   | ↑        | ↑       | ↑   | Candidate reject — Rule of 3; verify no external constraint   |
| Add facade — over a 4-step chain                    | ↑   | —        | hides P | ↑   | Keep only if K↓ measurable; never claim P↓ (§4 warning)       |
| Flatten — intermediate part has no independent role | —   | ↑        | ↓       | ↓   | Candidate proceed; verify internal K and invariants bounded   |
| Extract common part — ≥3 dependents                 | ↓   | ↓        | —       | ↑   | Candidate proceed; verify lifecycle and ownership match       |
| Bypass a part — bypassed has no independent role    | —   | ↑        | ↓       | ↓   | Candidate proceed; verify no boundary or policy is bypassed   |
| Introduce mediator between 2 parts                  | ↑   | ↑        | ↑       | ↑   | Candidate reject unless it enforces a boundary or decouples time |
| Merge two cohesive parts                            | ↓   | within ↑ | ↓       | ↓   | Candidate proceed; verify internal K stays bounded            |
| Split overloaded part along an SoC seam             | ↓   | ↓        | ↑       | ↑   | Candidate proceed; verify caller paths remain understandable  |

---

## 7. Asymmetric Trade-offs

Cases where net axis effect is positive despite local cost.

### 7a. Conformance (Pattern Alignment)

Accept local structural cost to eliminate a unique shape from D only when the
standard pattern fits the same semantics, lifecycle, ownership, and external
constraints. One snowflake among ten uniform parts can inflate D
disproportionately, but a real domain distinction should be named and preserved.

### 7b. Scope Reduction (Deletion)

Remove or deprecate special functionality if its structural footprint exceeds
its utility and the `functionality-complexity-tradeoff` verdict allows safe
removal. Special cases are complexity multipliers: D↑ (unique patterns), K↑
(conditional paths), P↑ (extended chains), n↑ (supporting parts). The cost of
a feature includes every special case it forces elsewhere, plus the migration
and compatibility work needed to remove it safely.

### 7c. Atomicity Requirements

When an action coordinates multiple independent participants (services,
actors, steps, partners), the atomicity decision has direct structural cost.
Decide **before implementation** — see `architecture-guidelines` §5
*Atomicity*.

| Decision             | Structural effect | Action                                        |
| -------------------- | ----------------- | --------------------------------------------- |
| Atomicity required   | K↑ P↑             | Accept coupling; use fail-fast / compensation |
| Eventual consistency | K↓ P↓             | Document acceptable partial-failure states    |

**Anti-Pattern:** designing multi-step operations without deciding atomicity
first.

---

## 8. Decision Protocol

1. **Model** before-state and after-state. Record D, K, P, n for each
   (internal axes; see Reporting Vocabulary for the coder-facing field names).
2. **Cycle check.** If the modeled projection is required to be acyclic, a
   cycle in the after-state is a hard fault — fix before continuing. If the
   domain permits cycles, record the cycle semantics and score the chosen
   acyclic projection separately.
3. **Answer the forcing questions in writing** (one line each):
    - **D:** What unique pattern does this introduce that no sibling uses?
      *(Name the 2nd concrete instance; absence = Rule-of-3 violation.)*
    - **K:** Which previously-independent parts does this link?
    - **P:** How long is the longest dependency chain a typical change
      traverses? *(>3 hops → max-chain-depth is itself the cost.)*
    - **n:** If deleted, what would dependents do? *(If "use the thing it
      wraps," it's a no-op facade.)*
    - **Counterfactual:** Does §7a or §7b apply? What is the 12-month
      removal cost?
4. **Check non-structural gates.** Confirm the candidate still satisfies
   required behavior, security/privacy, compliance, observability,
   performance, migration, and rollback constraints. Structural improvement is
   not permission to break a required property.
5. **Classify**:

    | Pattern                           | Action                          |
    | --------------------------------- | ------------------------------- |
    | All axes improve or hold          | Proceed if non-structural gates pass |
    | Mixed (some improve, some worsen) | Consult §6 trade-offs, apply §7, then check gates |
    | No axis improves                  | Reject or redesign unless required by an external gate |

6. **Emit a coder-facing decision record** (see Reporting Vocabulary for the symbol mapping):

    ```
    Subject:              <structure / module / refactor under review>
    Decision:             Proceed | Redesign | Reject
                          (retrospective: KEEP | SIMPLIFY | DELETE)
    Component-kinds Δ:    <±n>   (evidence: novel pattern, 2nd concrete instance)
    Dependency-edges Δ:   <±n>   (evidence: what newly couples to what)
    Max-chain-depth Δ:    <±n>   (evidence: longest path before → after)
    Module-count Δ:       <±n>   (evidence: parts added / removed)
    Cycle:                Pass | Fail
    Non-structural gates: Pass | Fail | Not evaluated
    Trade-off:            <§6 row matched; §7 sub-section if asymmetric>
    Rationale:            <1–3 sentences tying the four deltas and forcing-Q answers → decision>
    Next action:          <edit, test, lint rule, measurement, or smaller alternative>
    Verification:         <command / graph check / review evidence, or Not run + reason>
    ```

> [!IMPORTANT] If no axis improves, state: *"Complexity Warning:
> Component-kinds Δ [X], Dependency-edges Δ [Y], Max-chain-depth Δ [Z],
> Module-count Δ [W]. A simpler alternative is [...]."*

---

## 9. See also

- **`architecture-guidelines`** — first-principles discipline that informs Δ scoring (YAGNI, Rule of 3, DRY, SoC).
- **`geometric-architecture`** — spatial rationale; cycles forbidden by face directionality.
- **`functionality-complexity-tradeoff`** — consumes `D, K, P, n` deltas in its cost ledger.
- **`defect-shift-left`** — earliest stage to catch each axis violation.
- **`continuous-improvement`** — when a recurring axis violation signals a missing rule.
