---
name: geometric-architecture
description: >-
    A 3-D spatial coordinate system for the dependency graph. Every component is
    given an address (X = domain, Y = abstraction tier, Z = layer), coupling is
    restricted to face-adjacent neighbors, and connection direction is encoded
    by which face links to which. Long-range and cyclic connections become
    structurally expensive instead of merely discouraged. Includes ESLint
    enforcement via `eslint-plugin-boundaries` and `no-restricted-imports`.
    TRIGGER when: deciding where a new module/service/layer lives, designing or
    refactoring the dependency graph, diagnosing
    layer/cycle/god-object/cross-domain tangles, or configuring dependency-
    guard lint rules. SKIP for: routine business logic inside an existing
    module, bug fixes, content/copy edits, CSS-only changes, dependency bumps,
    trivial renames. For first-principles rules on what goes inside a module see
    `architecture-guidelines`; for evaluating whether a structural change
    actually reduces complexity see `structural-simplification`.
---

# Geometric Software Architecture

Place every component at an address `(X, Y, Z)` in a 3-D grid; allow coupling
only to face-adjacent neighbors. The medium itself resists long-range and cyclic
connections — the way a building's geometry resists impossible plumbing.

## Reporting Vocabulary

The skill thinks in coordinates and faces; the **report it emits speaks
architect**. The internal model (§§1–2) uses `(X, Y, Z)` and the six face
names. Every emit block, gate-table output, failure-mode citation, and
cross-skill reference uses the architect phrase instead.

| Internal term                | Architect phrase used in reports                                      |
| ---------------------------- | --------------------------------------------------------------------- |
| `(X, Y, Z)` address          | **Domain / abstraction tier / layer** (kept visible as three concerns) |
| `X` axis                     | **Domain** (bounded context)                                          |
| `Y` axis                     | **Abstraction tier** (orchestrator → primitive)                       |
| `Z` axis                     | **Layer** (consumer → infrastructure)                                 |
| Face: **Front**              | **Inbound interface** (public API)                                    |
| Face: **Back**               | **Outbound interface** (dependency surface)                           |
| Face: **Top**                | **Caller** (orchestrator above)                                       |
| Face: **Bottom**             | **Callee** (primitive below)                                          |
| Face: **Left / Right**       | **Peer / sibling**                                                    |
| **Wormhole**                 | **Layer-skip violation**                                              |
| Cell (the thing at an address) | **Component**                                                       |
| Cell (the address / slot)    | **Position** or **placement at <Domain / Tier / Layer>**              |
| Port (hexagonal term)        | — see "inbound/outbound interface"; deprecated alias, not used elsewhere |

**Naming guardrails.**
- **Layer** = Z only. **Abstraction tier** = Y only. Never let "layer" leak onto Y.
- "Inbound/outbound interface" is the only primary phrasing. "Port" appears once above as a deprecated alias and nowhere else.
- **Component** = the thing at an address (behavior + interface). **Position** = the address itself (the slot). Conflating them is the most common reader mistake — when a sentence is about *where* something lives, use "position" or "placement at <Domain/Tier/Layer>", not "component."
- Internal terms appear in exactly three places: inside a formula, inside this table, and inside §§1–2 (the internal model). Anywhere else in narrative, use the architect phrase.

> **2026-05-22 — emit field-name change.** Field labels and failure-mode
> names changed from internal terms to architect phrases:
> `(X, Y, Z) → Domain / Tier / Layer`,
> `Front/Back/Top/Bottom/Left/Right → inbound/outbound interface / caller / callee / peer`,
> `wormhole → layer-skip violation`,
> `cell → component (or position, for the address sense)`.
> Any downstream consumer (script, hook, agent prompt) that pattern-matched
> on the old terms must update. Internal terms remain in §§1–2 and in
> formulas; they are no longer emitted in reports.

---

## 1. Three axes (orthogonal concerns)

| Axis | Encodes                     | Direction                                                              |
| ---- | --------------------------- | ---------------------------------------------------------------------- |
| Z    | layer (environment depth)   | consumer (Z=0) → infrastructure (Z=N). Dependencies flow Z-increasing. |
| X    | domain / bounded context    | one column per business domain.                                        |
| Y    | abstraction tier            | orchestrators (top) → primitives (bottom).                             |

Same X = same domain. Same Y = same abstraction tier. Same Z = same layer. The
three concerns are orthogonal — position on one axis says nothing about the
others.

## 2. Six faces (directionality)

Every cell exposes six faces with fixed semantic roles (architect phrases in *italics* — used in all reports):

- **Front** — *inbound interface*; the only valid face for incoming calls.
- **Back** — *outbound interface*; outward calls / I/O / infrastructure access.
- **Top** — *caller* face; receives orchestration from above.
- **Bottom** — *callee* face; delegates to primitives below.
- **Left / Right** — *peer / sibling* faces; same-tier neighbors (cross-domain siblings).

A connection is valid only when **A's Back connects to B's Front**. Any other
pairing is a direction violation. Cycles are impossible without one connection
crossing a face the wrong way.

## 3. Failure modes the geometry rules out

| Failure mode          | Geometric fix                                                                             |
| --------------------- | ----------------------------------------------------------------------------------------- |
| Long-range coupling   | Locality: distance costs. A→C skipping B forces building B and naming the chain.          |
| Circular dependencies | Face directionality: cycles require a back-to-back face, which is invalid.                |
| Layer-skip violations | Z-axis + face: ΔZ > 1 is a layer-skip violation. UI cannot reach DB without traversing each layer. |
| God objects           | God-cell rule: all six faces occupied → decompose along the axis with the most edges.     |
| Hidden shared state   | Phantom-neighbor rule: implicit coupling must be promoted to a real cell with an address. |
| Semantic drift        | Single-address rule: a drifting cell accumulates multi-axis edges and surfaces diagonal.  |

## 4. What emerges for free

When locality and face direction are enforced, several conventional patterns
appear as consequences — not as additional rules to remember:

- Strict Z-flow → **Clean / Hexagonal architecture**: domain logic isolated from
  infrastructure.
- Independent X-columns → **DDD bounded contexts** and correct microservice
  cuts.
- Y-stratification → **tiered abstractions**: each tier knows only the tier
  immediately below.
- Locality → **bounded reasoning surface**: at most six neighbors per cell,
  regardless of codebase size.

The geometry decides _where a cell lives and what it may import_. It does not
prescribe what goes inside the cell.

## 5. Mechanical enforcement (ESLint)

Lint expresses most of the locality rule statically; the rest is review-time.

| Geometric rule                                       | Lint mechanism                                           | Tool                       |
| ---------------------------------------------------- | -------------------------------------------------------- | -------------------------- |
| Face-adjacent coupling only                          | `boundaries/dependencies` with `from` / `disallow`       | `eslint-plugin-boundaries` |
| Engine facade is the only entry point                | Each tier as an element; disallow external imports       | `eslint-plugin-boundaries` |
| Lower Y-tiers may not import higher                  | One `disallow` rule per tier                             | `eslint-plugin-boundaries` |
| External SDKs reachable only via their wrapper cells | `no-restricted-imports` + per-file override              | ESLint built-in            |
| Dynamic import paths must be literals                | `no-restricted-syntax` on non-literal `ImportExpression` | ESLint built-in            |
| Tests not imported by production                     | Dependencies rule: disallow `test` from prod elements    | `eslint-plugin-boundaries` |

Pattern: each cell = one element glob; directional rules = `disallow` between
element types. A layer-skip violation surfaces as a forbidden glob-to-glob
import. Config lives in `eslint.config.js` at repo root.

**Lint cannot enforce:**

1. **Address quality** — whether a cell is _placed_ correctly. (Review
   judgment.)
2. **Behavioral coupling** — pub/sub buses, runtime registries, globals.
   (Convention or runtime tooling.)
3. **Face roles** — lint sees "A imports B" but not "Back→Front." (Mental
   model.)

**Rollout:** add every rule at `warn`. Promote per-rule to `error` only after
that rule's violations clear. A rule that starts as `error` on a non-green
codebase gets disabled the first time someone needs to merge.

## 6. See also

- **`architecture-guidelines`** — what rules belong inside a cell.
- **`structural-simplification`** — measuring whether a placement change is a real simplification.
- **`architecture-as-code`** — lint-enforceable encoding of the geometry's edge rules.
