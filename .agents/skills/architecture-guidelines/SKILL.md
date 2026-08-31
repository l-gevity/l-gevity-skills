---
name: architecture-guidelines
description: >-
    First-principles architectural rules for module/service/abstraction design:
    minimalism, modularity, functional core, resilience, layer self-sufficiency,
    naming, and concurrency. TRIGGER when introducing a
    module/service/abstraction, refactoring across module boundaries, applying
    SOLID, deciding whether a control may rely on the layer beneath it, or
    reviewing architectural concerns (purity, idempotency, naming, fail-fast).
    SKIP for bug fixes within an existing module, content/copy edits, CSS-only
    changes, dependency bumps, and trivial renames. Emits an `Enforcement`
    handoff to `architecture-as-code` when a design decision yields an
    enforceable dependency constraint.
---

# Architectural Discipline (First Principles)

> **Core Directives**
>
> - **Patternization**: A unified, simpler whole beats a fragmented system of
>   locally perfect solutions. Accept local suboptimality for universal
>   patterns.
> - **Minimalism**: Smallest viable solution. ZERO speculative extensibility.
> - **Traceability**: Names reflect architectural layer, domain role, and
>   technical purpose.
> - **Dependency Discipline**: Graphs MUST be directed, acyclic, shallow. Cycles
>   forbidden. Depth is cost.

## 1. Minimalism & Abstraction

- **YAGNI**: No speculative features or extensibility hooks.
- **Rule of 3**: Wait for three proven instances before abstracting. Prefer
  copying < 20 lines over premature abstraction.
- **DRY (knowledge, not shape)**: A business rule, constant, or schema has
  exactly one authoritative representation. Code-shape duplication defers to
  Rule of 3.
- **Frame-check before execute**: When an issue, spec, or PRD prescribes
  implementation steps (a numbered "Implementation Approach" section, a
  multi-step task list, a build/CI plumbing plan), DO NOT start by executing
  step 1. First run the necessity gate from `functionality-complexity-tradeoff`
  §1 against the _framing_ the steps assume — what problem is this code actually
  addressing, does that problem still occur in this stack, is it already owned
  by another layer? Issue authors prescribe solutions; the gate asks whether the
  prescription matches a problem we have. A prescribed plan exceeding 3 steps or
  introducing a novel abstraction is the strongest trigger for this check.

## 2. Consistency & Coupling

- **Eventual Consistency by Default**: Strong consistency couples components.
  Accept idempotency / compensation to preserve modularity.
- **Full Migration**: When adopting a new pattern, migrate all sibling
  components in the same PR — but **always ask the user** and pick a pattern
  that fits both new and existing logic.
- **Dependency Inversion**: Domain logic depends on abstractions, never concrete
  implementations.

## 3. Functional Core

- **Pure Domain Logic, I/O at the Edges**: Business logic is pure, side-effect
  free, environment-agnostic. External systems live at the edges.
- **Testability**: A pure core is unit-testable without mocks. If the domain
  needs mocks, purity has been violated.

## 4. Modularity

- **SoC**: One concern per module; cross-cutting concerns are extracted, not
  interleaved.
- **SRP**: One reason to change per module. Two forces of change → split.
- **Capability Boundary = Module Boundary**: A capability with its own domain
  name, lifecycle, dependency surface, test surface, or reason to change gets
  its own module directory. Do not group multiple atomic capabilities in one
  subsystem directory unless they form a higher-level capability with a single
  public interface and shared change reason.
- **High Cohesion, Loose Coupling**: Internals tightly related; external
  dependencies minimized and abstracted.
- **Interface Discipline**:
    - _Caller_: depend on the contract, never the implementation.
    - _Module_: internals encapsulated; the interface is the only access point.
    - _Designer_: expose everything every caller needs and only what every
      caller needs.

**Review check:** If a directory contains multiple named capabilities, require
one of: a single facade/interface proving they are one higher-level capability,
or a split into capability-named module directories.

## 5. Resilience

- **Fail Fast**: Validate and sanitize inputs at all system or atomicity
  boundaries.
- **Idempotency**: Safe under repeated execution; succeeds when the desired
  state already holds. Does not suppress errors that prevent reaching it.
- **Statelessness**: Prefer stateless services.
- **Failure Classification**: Categorize each external call as **hard** (blocks
  subsequent steps) or **best-effort** (logged, no cascade) before
  implementation.
- **Atomicity**: Decide whether partial success is acceptable or rollback is
  required.
- **State Visibility**: Log decision and outcome at each step.

## 6. Naming & Traceability

- **Domain-Driven Names**: Every function, variable, directory reveals
  architectural layer, domain role, and technical purpose. `utils` / `helpers`
  fail this test.
- **Self-Documenting Structure**: Directory and filename alone should reveal
  architectural boundaries and business rules.

## 7. Concurrency & Shared Mutable State

Every shared mutable state must declare its concurrency model:

- **Per-instance** (multi-tab) → use `navigator.locks` or `BroadcastChannel`.
- **Per-tab** → fine; document in JSDoc.
- **Global** → atomic writes or locks.

**Review check:** if state is modified after an `await`, ask: _"is this guarded
against concurrent mutation?"_

## 8. Layer Self-Sufficiency

- **Controls complete at their own layer**: a control a layer owns must hold on
  that layer alone. One that works only because a lower layer limits who can
  reach it is inherited, not implemented.
- **Assume the layer below is absent**: every authentication and authorization
  decision must hold with the endpoint publicly reachable. Network isolation,
  private connectivity, and firewall placement are additional layers, never the
  control.
- **Ambient guarantees are invisible dependencies**: the assumption lives
  outside the codebase, so the deployment or infrastructure change that
  invalidates it never appears in a diff, review, or test of the code relying
  on it.
- **Name the reason for every gap**: when a control is weakened, deferred, or
  dropped, state why. A reason that cites a property of a lower layer or the
  deployment environment means the control is missing, not satisfied.

**Review check:** for each control, ask _"does this still hold when the layer
below it disappears?"_ A "no" is a defect in the layer under review, never a
requirement on the layer below.

> [!IMPORTANT] **Complexity Warning**: If a solution violates any guideline
> above, state: _"Complexity Warning: introduces [X]. A simpler alternative is
> [Y]."_ If the violation is non-trivial, see `structural-simplification` §8
> Decision Protocol for a per-axis comparison before accepting it.

## 9. Enforcement Handoff

Use `architecture-as-code` only for constraints that can be enforced as import
or dependency rules. Do not duplicate this skill's principles there; hand off
the specific rule to encode.

Examples:

```
Principle:   DI / functional core
Constraint:  domain must not import infrastructure
Enforcement: add architecture rule: forbid <domain-component> -> <infra-component>
```

```
Principle:   interface discipline
Constraint:  external callers use the facade only
Enforcement: add architecture rule: forbid * -> <module-internal-*>, except <module-*>
```

A principle can also settle as no handoff. Record that outcome rather than
omitting it:

```
Principle:   layer self-sufficiency
Constraint:  the control holds with the layer below absent
Enforcement: none - not an import or dependency edge; verify by exercising the
             component without that layer (`defect-shift-left`)
```

## 10. Output Contract

When this skill changes or rejects a design, emit a coder-facing decision
record:

```
Subject:        <module / service / abstraction / PR / code path>
Decision:       Proceed | Simplify | Split | Inline | Reject | Defer
Principle:      <YAGNI | Rule of 3 | DRY | SoC | SRP | capability-boundary | DI | fail-fast | idempotency | atomicity | layer-self-sufficiency | naming | concurrency>
Evidence:       <callers, imports, tests, runtime invariant, or file paths checked>
Enforcement:    <none | add architecture rule: constraint | update architecture rule: constraint>
Next action:    <edit, delete, extract, add test, add lint rule, or ask user>
Verification:   <command / review check / Not run + reason>
```

## See also

- **`functionality-complexity-tradeoff`** — necessity gate and worth ledger applied to individual decisions.
- **`structural-simplification`** — per-axis complexity comparison (`D, K, P, n`).
- **`morphogenetic-architecture`** — declared placement, observed coupling fields, and topology evolution.
- **`architecture-as-code`** — consumes explicit `Enforcement` handoffs and turns enforceable dependency constraints into lint rules.
