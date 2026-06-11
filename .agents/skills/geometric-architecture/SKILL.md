---
name: geometric-architecture
description: >-
    A 3-D spatial coordinate system for the dependency graph. Every component is
    given an address (X = domain, Y = abstraction tier, Z = layer), dependency
    coupling is routed through declared adjacent positions, and connection
    direction is encoded by which face links to which. Long-range and forbidden
    cyclic connections become structurally expensive instead of merely
    discouraged. Includes ESLint
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

Place every component at an address `(X, Y, Z)` in a 3-D grid; route dependency
coupling through declared adjacent positions. The medium itself resists
long-range and forbidden cyclic connections — the way a building's geometry
resists impossible plumbing.

## Reporting Vocabulary

The skill may reason in coordinates and faces, but reports are for a coding
agent that must choose files, imports, lint rules, or review checks. The
internal model (§§1–2) uses `(X, Y, Z)` and the six face names. Every emit block,
gate-table output, failure-mode citation, and cross-skill reference uses the
coder-facing field below.

| Internal term                | Coder-facing field used in reports                                    |
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
- Internal terms appear in exactly three places: inside a formula, inside this table, and inside §§1–2 (the internal model). Anywhere else in narrative, use the coder-facing field.

> **2026-05-22 — emit field-name change.** Field labels and failure-mode
> names changed from internal terms to coder-facing fields:
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
| Z    | layer (environment depth)   | consumer (Z=0) → infrastructure (Z=N). Dependency arrows point toward declared dependency surfaces; imports may point the opposite way when dependency inversion is used. |
| X    | domain / bounded context    | one column per business domain.                                        |
| Y    | abstraction tier            | orchestrators (top) → primitives (bottom).                             |

Same X = same domain. Same Y = same abstraction tier. Same Z = same layer. The
three concerns are orthogonal — position on one axis says nothing about the
others.

## 2. Six faces (directionality)

Every cell exposes six conceptual faces with fixed semantic roles
(coder-facing fields in *italics* — used in all reports):

- **Front** — *inbound interface*; the public surface through which callers enter.
- **Back** — *outbound interface*; outward calls / I/O / infrastructure access.
- **Top** — *caller* face; receives orchestration from above.
- **Bottom** — *callee* face; delegates to primitives below.
- **Left / Right** — *peer / sibling* faces; same-tier neighbors (cross-domain siblings).

A dependency connection is valid when **A's outbound interface connects to B's
inbound interface** through an allowed adjacent position or an explicitly named
boundary component. Other pairings are direction violations. A forbidden import
cycle in an acyclic projection is impossible without at least one connection
crossing a face the wrong way; intentional runtime cycles such as event loops or
state machines must be modeled as runtime behavior, not static import edges.

## 3. Failure modes the geometry rules out

| Failure mode          | Geometric fix                                                                             |
| --------------------- | ----------------------------------------------------------------------------------------- |
| Long-range coupling   | Locality: distance costs. A→C skipping B requires a named boundary or intermediate position. |
| Circular dependencies | Face directionality: forbidden import cycles require a back-to-back face, which is invalid in acyclic projections. |
| Layer-skip violations | Z-axis + face: ΔZ > 1 is a layer-skip violation unless a declared boundary adapter owns the jump. |
| God objects           | God-cell rule: many occupied faces or unrelated edge clusters → decompose along the axis with the most edges. |
| Hidden shared state   | Phantom-neighbor rule: implicit coupling must be promoted to a real component with an address or documented as runtime-only coupling. |
| Semantic drift        | Single-address rule: a drifting component accumulates multi-axis edges and surfaces diagonal. |

## 4. What emerges for free

When locality and face direction are enforced for static dependencies, several
conventional patterns become easier to maintain:

- Strict Z-flow plus dependency inversion → **Clean / Hexagonal architecture**:
  domain logic isolated from
  infrastructure.
- Independent X-columns → **DDD bounded contexts** and correct microservice
  cuts.
- Y-stratification → **tiered abstractions**: each tier knows only the tier
  immediately below.
- Locality → **bounded reasoning surface**: each component has a small declared
  neighbor set, even when a physical package contains many files.

The geometry decides _where a cell lives and what it may import_. It does not
prescribe what goes inside the cell.

## 5. Mechanical enforcement (ESLint)

Lint expresses import-edge rules statically; placement quality, runtime
coupling, and face semantics remain review-time or runtime-tooling concerns.

| Geometric rule                                       | Lint mechanism                                           | Tool                       |
| ---------------------------------------------------- | -------------------------------------------------------- | -------------------------- |
| Declared adjacency / allowed dependency routes       | `boundaries/dependencies` with `from` / `allow` / `disallow` | `eslint-plugin-boundaries` |
| Boundary facade is the only external entry point     | Each boundary as an element; disallow bypass imports     | `eslint-plugin-boundaries` |
| Lower Y-tiers may not import higher in the chosen projection | One `disallow` rule per tier                     | `eslint-plugin-boundaries` |
| External SDKs reachable only via their wrapper components | `no-restricted-imports` + per-file override          | ESLint built-in            |
| Dynamic import paths must be literals                | `no-restricted-syntax` on non-literal `ImportExpression` | ESLint built-in            |
| Tests not imported by production                     | Dependencies rule: disallow `test` from prod elements    | `eslint-plugin-boundaries` |

Pattern: each component or position = one element glob; directional rules are
encoded as allowed or disallowed imports between element types. A layer-skip
violation surfaces as a forbidden glob-to-glob import. Config usually lives in
`eslint.config.js` at repo root, or in generated flat config when
`architecture-as-code-javascript` assembles per-module rules.

**Lint cannot enforce:**

1. **Address quality** — whether a cell is _placed_ correctly. (Review
   judgment.)
2. **Behavioral coupling** — pub/sub buses, runtime registries, globals.
   (Convention or runtime tooling.)
3. **Face roles** — lint sees "A imports B" but not whether the code respects
   the intended inbound/outbound interface semantics. (Review/API design.)

**Rollout:** add every rule at `warn`. Promote per-rule to `error` only after
that rule's violations clear. A rule that starts as `error` on a non-green
codebase gets disabled the first time someone needs to merge.

## 6. Audit Output

When applying this skill, emit one row per violation and include the exact code
action Codex should take next:

| Component / import | Domain / tier / layer | Violation | Evidence | Decision | Next action | Verification |
| ------------------ | --------------------- | --------- | -------- | -------- | ----------- | ------------ |

Use these violation names: **layer-skip violation**, **tier inversion**,
**cross-domain coupling**, **forbidden import cycle**, **god component**,
**hidden runtime coupling**, **external SDK bypass**, **placement ambiguity**.
If lint can enforce the finding, name the rule to add or update. If lint cannot
enforce it, name the review, runtime, or architecture-as-code guard that owns it.

## 7. See also

- **`architecture-guidelines`** — what rules belong inside a cell.
- **`structural-simplification`** — measuring whether a placement change is a real simplification.
- **`architecture-as-code`** — lint-enforceable encoding of the geometry's edge rules.
