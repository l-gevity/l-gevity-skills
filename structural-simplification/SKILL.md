# Structural Simplification

A domain-agnostic measurement framework locates and weighs complexity. Any structure — code, data model, workflow, UI layout, organization, process — is evaluated on four independent axes of complexity; trade-offs become explicit.

## Why use this

- **Simplicity debates end with arithmetic instead of opinion.** Every claim asserts specific deltas that can be verified or contested.
- **Existing structures can be audited.** High scores on any axis flag candidates for refactoring before they ossify.
- **Trade-offs in proposed changes are forced into the open.** Raising depth to lower coupling stops being an accident.
- **Pure wins stand out.** Almost always deletions — they're the only changes that improve every axis at once.
- **The framework is domain-agnostic.** It applies to code, data, workflows, UI, organizations, and processes — not just refactors.

## Fundamental principles

Complexity is not a scalar. It is at least a four-dimensional vector — and any single-number metric (lines of code, cyclomatic complexity, file count) erases the trade-offs that actually matter.

- **Four axes, four costs.** Diversity, coupling, depth, quantity — each maps to a different cost: learning, changing, tracing, holding.
- **Most moves trade across axes.** Reducing one almost always raises another; this is structural, not a design failure.
- **Deletions are the only pure wins.** The only changes that improve every axis at once. Prefer them when possible.
- **Measurement is discipline.** "I think this is cleaner" becomes "you reduced K by 0.3 but raised P from 4 to 6." The conversation changes character.

A change that worsens any axis without improving another is not a simplification.

## How to use

The skill has two modes: **audit** an existing structure, or **evaluate** a proposed change.

1. **Identify the structure or change.** A live subsystem to audit, or a proposed restructuring to evaluate.
2. **Prompt the AI.**

   > *Audit:* "Audit the order processing pipeline for simplification opportunities."
   >
   > *Evaluate:* "Evaluate extracting `validateOrder` from `checkout.ts` and `refund.ts` into a shared module."

3. **Read the per-axis result.** Each axis is reported with its current value (audit) or its delta (evaluate). The worst-offending axis is flagged with a recommended reduction operation.
4. **Decide.** For audits: target the worst axis with the suggested operation. For evaluations: accept, reject, or redesign.

## The four axes

| Axis  | Stands for | What it counts                            | Cost it imposes                          |
|-------|------------|-------------------------------------------|------------------------------------------|
| **D** | Diversity  | Distinct patterns, shapes, or concepts    | *Learning* — every shape to understand   |
| **K** | Coupling   | Relationship density `edges / (n × (n−1))` | *Changing* — every dependency to follow  |
| **P** | Path/depth | Longest chain from source to sink         | *Tracing* — every hop to read through    |
| **n** | Quantity   | Total number of parts                     | *Holding* — every part in working memory |

A structure is a vector: *(D, K, P, n)*. A change is a delta: *(ΔD, ΔK, ΔP, Δn)*. Pure wins point negative on every axis. Trade-offs point negative on some, positive on others.

## Asymmetric trades

Three patterns where accepting a local cost wins a larger global gain:

- **Conform over customize.** A snowflake in a uniform system inflates D disproportionately. Forcing it into the standard shape costs local quality for global uniformity — a worthwhile trade.
- **Delete over mitigate.** Special cases multiply complexity across all four axes. Removing the feature is almost always cheaper than handling its consequences elsewhere.
- **Decide atomicity consciously.** Atomicity raises K and P; eventual consistency transfers the cost to compensation logic. Either is fine; choosing accidentally is not.

## When to skip

Trivial renames, content edits, dependency bumps, isolated bug fixes that don't touch structure. The framework earns its keep when the restructuring is non-obvious, contested, or large.

## Next steps

- See [SKILL.md](./SKILL.md) for the operational reference (reduction operations, full trade-off matrix, decision protocol).
- Related skills: [`architecture-guidelines`](../architecture-guidelines/) (module design), [`geometric-architecture`](../geometric-architecture/) (spatial dependency graphs).
- Run an audit on a subsystem you suspect is over-complex — the verdict often reveals which axis is really hurting.
