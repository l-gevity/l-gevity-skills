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
> 1. **Patternization & Local Suboptimality**: Accept suboptimal local
>    implementations if they allow the system to use universal patterns. A
>    unified, simpler whole is ALWAYS more valuable than a fragmented system of
>    locally perfect solutions. _(See `structural-simplification` §7a
>    Conformance for the formal justification.)_
> 2. **Minimalism First**: Deliver the smallest viable solution. ZERO
>    speculative extensibility (YAGNI).
> 3. **Duplication Over Wrong Abstraction**: Always copy < 20 lines of code
>    rather than creating a premature abstraction. Wait for the proven business
>    need (Rule of 3).
> 4. **Architectural Traceability**: Names of functions, variables, directories,
>    and all structural components MUST explicitly reflect their architectural
>    layer, domain logic, and technical purpose.
> 5. **A design is perfect when there is nothing left to remove.**
> 6. **Dependency Graph Discipline**: Dependency graphs MUST be directed,
>    acyclic, and shallow. Cycles are forbidden. Depth is cost.

## 1. Minimalism & Abstraction

- **YAGNI**: No speculative features or extensibility hooks.
- **Rule of 3**: Wait for three proven instances before abstracting.
- **Complexity Threshold**: Reconsider any task requiring > 3 implementation
  steps or a novel abstraction pattern.

## 2. Consistency & Coupling

- **Full Migration**: When adopting a new pattern, migrate all sibling
  components in the same PR.
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

- **Fail Fast**: Validate and sanitize inputs at all system boundaries.
- **Idempotency**: Design operations to be safe for multiple executions.
- **Statelessness**: Prefer stateless services to minimize side effects and
  simplify scaling and testing.

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
