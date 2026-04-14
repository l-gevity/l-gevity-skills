---
name: architecture-guidelines
description:
    Ensures all code adheres to the project's core platform-agnostic
    architectural principles (consistency, minimalism, reliability, and
    traceability). Use this skill when designing or modifying any system
    component or feature.
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
> - **Duplication Over Wrong Abstraction**: Always copy < 20 lines of code
>   rather than creating a premature abstraction. Wait for the proven business
>   need (Rule of 3).
> - **Architectural Traceability**: Names of functions, variables, directories,
>   and all structural components MUST explicitly reflect their architectural
>   layer, domain logic, and technical purpose.
> - **A design is perfect when there is nothing left to remove.**
> - **Dependency Graph Discipline**: Dependency graphs MUST be directed,
>   acyclic, and shallow. Cycles are forbidden. Depth is cost.

## 1. Minimalism & Abstraction

- **YAGNI**: No speculative features or extensibility hooks.
- **Rule of 3**: Wait for three proven instances before abstracting.
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

## 3. Isolation

- **Functional Core**: Business logic must be pure, side-effect free, and
  environment-agnostic.
- **No External Dependencies**: Domain logic must not depend on external systems
  or services.
- **Separation of Concerns**: Modules or subsystems should have a single
  responsibility.

## 4. Resilience

- **Fail Fast**: Validate and sanitize inputs at all system or atomicity
  boundaries.
- **Idempotency**: Design operations to be safe for multiple executions by
  achieving the desired end state. Distinguish:
    - **DELETE on 404** (already deleted) → return success ✓
    - **CREATE on 409** (already exists) → return existing resource ✓
    - **GET on 404** (missing) → return null/empty ✓
    - **PATCH/PUT on 404** (user/target gone) → log & observe degradation, do
      not silently succeed ⚠️
    - **Race conditions (409 on write)** → throw error; let client
      retry/reconcile ✗

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

## 5. Naming & Traceability

- **Domain-Driven Names**: Every function, variable, and directory must reveal
  its architectural layer, domain role, and technical purpose.
- **No Generic Names**: Avoid `utils`, `helpers`, or other catch-all names when
  a domain-specific name applies.
- **Self-Documenting Structure**: Directory structure and filenames alone should
  let any developer infer architectural boundaries and business rules.

> [!IMPORTANT] **Complexity Warning**: If a solution violates any guideline
> above, state: _"Complexity Warning: This introduces [X]. A simpler alternative
> is [Y]."_ Use `structural-simplification` §8 Decision Protocol to compare
> per-axis deltas before accepting the violation.
