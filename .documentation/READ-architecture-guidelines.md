# Architecture Guidelines

A first-principles ruleset for module design. Minimalism, modularity, functional core, resilience, naming, concurrency — the things every module decision should test against before code is written.

## Why use this

- **Module decisions become checkable.** Each principle is a yes/no question, not a vibe.
- **Speculative complexity stops at the door.** YAGNI and Rule of 3 are the null hypothesis; abstractions need three proven instances, not one imagined one.
- **Domain logic stays pure.** Side effects live at the edges; the core is unit-testable without mocks.
- **Failure modes are decided up front.** Every external call is classified hard or best-effort *before* implementation, not after the first incident.
- **Names carry architecture.** `utils` and `helpers` fail the test; every name reveals layer, domain role, and technical purpose.

## Fundamental principles

Architecture is the art of keeping a system reasonable as it grows. These rules exist because their inverses produce the same failure modes in every codebase: speculative abstractions, tangled dependencies, untestable logic, undeclared concurrency, vague names.

- **Patternization beats local optimization.** A unified, simpler whole beats a fragmented system of locally perfect solutions.
- **Minimalism is the default.** Smallest viable solution; zero speculative extensibility.
- **Dependencies are directed, acyclic, shallow.** Cycles are forbidden; depth is cost.
- **Pure core, I/O at the edges.** If domain logic needs mocks, purity has been violated.
- **Fail fast at boundaries.** Validate at system or atomicity boundaries; classify every external call hard or best-effort.

## How to use

The skill applies in two situations: **designing** a new module, or **reviewing** a change that crosses module boundaries.

1. **Identify the trigger.** Introducing a new module, refactoring across module boundaries, applying SOLID, or reviewing a PR for architectural concerns (purity, idempotency, naming, fail-fast).
2. **Prompt the AI.**

   > *Design:* "I'm adding a new `notifications` module that sends emails and SMS. Walk me through the architecture-guidelines checklist."
   >
   > *Review:* "Audit this PR against architecture-guidelines. Flag any violation with the section number."

3. **Read the verdict.** The skill names the principle violated (e.g. "§3 — pure core: `OrderService` calls `fetch()` directly") and proposes the smallest fix.
4. **Apply the fix.** Pull I/O to the edge; raise the abstraction only when the third instance arrives; rename the module so its layer is visible.

## The seven sections at a glance

| §   | Topic                       | Core question                                                                |
|-----|-----------------------------|------------------------------------------------------------------------------|
| **1** | Minimalism & abstraction    | Does this exist? Is there a third instance? Is the rule one source of truth? |
| **2** | Consistency & coupling      | Eventual consistency by default; depend on contracts, not implementations.   |
| **3** | Functional core             | Is the domain logic pure? Does I/O live at the edge?                         |
| **4** | Modularity                  | One concern, one reason to change, interface as the only access point.       |
| **5** | Resilience                  | Validated at boundaries? Idempotent? Failure mode classified? Atomic?        |
| **6** | Naming & traceability       | Does the name reveal layer, domain role, and technical purpose?              |
| **7** | Concurrency & shared state  | Is the concurrency model declared (per-instance / per-tab / global)?         |

## The complexity warning

When a proposal violates a guideline, the skill states the trade explicitly:

> *"Complexity Warning: introduces [X]. A simpler alternative is [Y]."*

If the violation isn't trivial, route through `structural-simplification` §8 (Decision Protocol) for a per-axis comparison before accepting it. The warning is the gate; the per-axis comparison is the receipt.

## When to skip

Bug fixes inside an existing module, content/copy edits, CSS-only changes, dependency bumps, trivial renames. The framework earns its keep when module boundaries are being drawn or crossed.

## Next steps

- See [SKILL.md](./SKILL.md) for the full ruleset (numbered sections, examples, complexity-warning protocol).
- For refactor cost/benefit analysis once a violation is found, see [`structural-simplification`](../structural-simplification/).
- For spatial dependency-graph constraints and lint enforcement, see [`geometric-architecture`](../geometric-architecture/).
- For deciding whether a piece of functionality justifies its cost, see [`functionality-complexity-tradeoff`](../functionality-complexity-tradeoff/).
