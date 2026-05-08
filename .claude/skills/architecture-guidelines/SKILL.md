---
name: architecture-guidelines
description: >-
    First-principles architectural rules for this project: minimalism (YAGNI,
    Rule of 3, DRY), modularity (SoC, SRP, interface discipline, dependency
    inversion), functional core (pure domain logic, I/O at the edges),
    resilience (fail-fast, idempotency, atomicity, failure classification),
    domain-driven naming, and concurrency on shared mutable state. TRIGGER when:
    introducing a new module/service/abstraction, refactoring across module
    boundaries, applying SOLID, or reviewing a PR for architectural concerns
    (purity, idempotency, naming, fail-fast). SKIP for: bug fixes within an
    existing module, content/copy edits, CSS-only changes, dependency bumps,
    trivial renames. For implementation patterns specific to this app see
    `technical-design`; for refactor cost/benefit analysis see
    `structural-simplification`; for spatial dependency-graph constraints and
    lint enforcement see `geometric-architecture`.
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
  step 1. First run the necessity gate from `functionality–complexity-tradeoff`
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
- **High Cohesion, Loose Coupling**: Internals tightly related; external
  dependencies minimized and abstracted.
- **Interface Discipline**:
    - _Caller_: depend on the contract, never the implementation.
    - _Module_: internals encapsulated; the interface is the only access point.
    - _Designer_: expose everything every caller needs and only what every
      caller needs.

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

> [!IMPORTANT] **Complexity Warning**: If a solution violates any guideline
> above, state: _"Complexity Warning: introduces [X]. A simpler alternative is
> [Y]."_ If the violation is non-trivial, see `structural-simplification` §8
> Decision Protocol for a per-axis comparison before accepting it.
