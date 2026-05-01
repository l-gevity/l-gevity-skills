---
name: architecture-guidelines
description:
    First-principles architectural rules (minimalism, modularity, resilience,
    naming, concurrency) for this project.
    TRIGGER when: introducing a new module/service/layer, refactoring across
    module boundaries, designing a new abstraction, reviewing a PR for
    architectural concerns, or applying SOLID.
    SKIP for: bug fixes within an existing module, content/copy edits, CSS-only
    changes, dependency bumps, and trivial renames. For implementation
    patterns specific to this app see `technical-design`; for refactor
    cost/benefit analysis see `structural-simplification`.
---

# Architectural Discipline (First Principles)

> **Core Directives**
>
> - **Patternization & Local Suboptimality**: Accept suboptimal local
>   implementations if they allow the system to use universal patterns. A
>   unified, simpler whole is ALWAYS more valuable than a fragmented system of
>   locally perfect solutions.
> - **Minimalism First**: Deliver the smallest viable solution. ZERO speculative
>   extensibility (YAGNI).
> - **Architectural Traceability**: Names of functions, variables, directories,
>   and all structural components MUST explicitly reflect their architectural
>   layer, domain logic, and technical purpose.
> - **Dependency Graph Discipline**: Dependency graphs MUST be directed,
>   acyclic, and shallow. Cycles are forbidden. Depth is cost.

## 1. Minimalism & Abstraction

- **YAGNI**: No speculative features or extensibility hooks.
- **Rule of 3**: Wait for three proven instances before abstracting. Prefer
  copying < 20 lines over creating a premature abstraction.
- **DRY (knowledge, not shape)**: A business rule, constant, or schema has
  exactly one authoritative representation. Code _shape_ duplication defers to
  Rule of 3.
- **Complexity Threshold**: Reconsider any task requiring > 3 implementation
  steps or a novel abstraction pattern.

## 2. Consistency & Coupling

- **Eventual Consistency by Default**: Strong consistency couples components.
  Prefer eventual consistency — accept operational complexity (idempotency,
  compensation) to preserve modularity.
- **Full Migration**: When adopting a new pattern, migrate all sibling
  components in the same PR but **always ask the user** and choose a pattern
  that fits both new and existing logic.
- **Dependency Inversion**: Domain logic depends on abstractions, never concrete
  implementations.

## 3. Functional Core

Isolate business logic from the runtime environment so it can be reasoned about,
tested, and ported without rewiring.

- **Pure Domain Logic, I/O at the Edges**: Business logic is pure, side-effect
  free, and environment-agnostic. External systems, services, and platform APIs
  live at the edges — never invoked from the core.
- **Testability as a Consequence**: A pure core is unit-testable without mocks,
  fixtures, or environment setup. If the domain needs mocks to test, purity has
  been violated.

## 4. Modularity

- **Separation of Concerns (SoC)**: Each module addresses one concern;
  cross-cutting concerns are extracted, not interleaved.
- **Single Responsibility (SRP)**: One reason to change per module. If two
  forces of change pull on the same file, split it.
- **High Cohesion, Loose Coupling**: Internals tightly related; external
  dependencies minimized and abstracted. Cohesion is the positive pull; coupling
  is the cost.
- **Interface Discipline**: Three perspectives on the same contract.
    - **Program to the Interface** (caller): callers depend on the contract,
      never the implementation.
    - **Modules Hide Behind Interfaces** (module): internals are encapsulated;
      the interface is the only legitimate access point.
    - **Minimal but Complete** (designer): expose _everything_ every caller
      needs and _only_ what every caller needs — no leaked internals, no methods
      kept "just in case."

## 5. Resilience

- **Fail Fast**: Validate and sanitize inputs at all system or atomicity
  boundaries.
- **Idempotency**: Design operations to be safe for multiple executions by
  achieving the desired end state.

    _Principle_: Idempotency succeeds when the desired outcome is already true.
    It does not suppress errors that prevent achieving the outcome.

- **Statelessness**: Prefer stateless services to minimize side effects and
  simplify scaling and testing.
- **Failure Classification**: When coordinating external API calls, categorize
  each as **hard** (blocks subsequent steps) or **best-effort** (logged, does
  not cascade). Design the failure model before implementation.
- **Atomicity**: Determine whether partial success is acceptable or full
  rollback is required.
- **State Visibility**: Log decision point and outcome at each step.

## 6. Naming & Traceability

- **Domain-Driven Names**: Every function, variable, and directory must reveal
  its architectural layer, domain role, and technical purpose. Catch-all names
  like `utils` or `helpers` fail this test.
- **Self-Documenting Structure**: Directory structure and filenames alone should
  let any developer infer architectural boundaries and business rules.

## 7. Concurrency & Shared Mutable State

Every shared mutable state (e.g., `#isSyncing`, `auth.user`, `#pendingWrites`)
must declare its concurrency model:

- **Per-instance?** Accessible from multiple tabs concurrently → use
  `navigator.locks` or BroadcastChannel for coordination.
- **Per-tab?** Per-instance is fine; document in JSDoc.
- **Global?** Needs atomic writes or locks.

**Code Review Check:** If state is modified after an `await`, ask: _"Is this
guarded against concurrent mutation?"_

> [!IMPORTANT] **Complexity Warning**: If a solution violates any guideline
> above, state: _"Complexity Warning: This introduces [X]. A simpler alternative
> is [Y]."_ Use `structural-simplification` §8 Decision Protocol to compare
> per-axis deltas before accepting the violation.
