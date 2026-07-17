# Implementation Readiness

A polished specification is not necessarily buildable. Implementation Readiness
tests whether requirements, verification, ownership, prerequisites, constraints,
and unresolved decisions are complete enough for responsible architecture and
development work.

## Why use this

- Distinguish ready, partly ready, and blocked work explicitly.
- Pull shared foundations and cross-cutting constraints forward in the sequence.
- Identify missing external contracts before dependent implementation starts.
- Derive the smallest coherent end-to-end slice instead of a layer-by-layer plan.
- Keep every capability, contract candidate, ADR seed, and test reference linked
  to stable requirement IDs.

## Fundamental principle

Readiness is a falsifiable decision, not a document-completeness score. A slice is
ready only when its outcome, actor, verification, owner, prerequisites, data
boundaries, and relevant constraints are known. Open architecture choices can be
captured as ADRs; open product or policy choices remain blockers when different
answers change the required outcome.

## How to use

Ask the agent to test and prepare a stable requirements topology:

> “Assess this requirements graph for implementation readiness. Separate ready,
> partly ready, and blocked work and identify the earliest unblock action.”

> “Derive the smallest coherent implementation slice, its requirement IDs,
> prerequisites, constraints, test references, and ADR questions.”

If only raw requirements are available, the skill routes back to grounding or
topology instead of inventing missing structure.

## What it derives

- capability maps and workstreams;
- dependency-aware implementation order;
- vertical slices and acceptance-test references;
- data ownership and lifecycle constraints;
- evidence and operational needs;
- contract candidates and domain-model seeds;
- ADR seeds and technical-design questions;
- explicit blockers, owners, and earliest unblock actions.

These are build-preparation artifacts, not automatic architecture commitments.
A requirement edge does not imply a service, event, API, or synchronous call.

## Output

The full package names its canonical grounding and topology, gives a readiness
decision, lists blocking gaps and owners, and derives only the implementation
artifacts supported by the requirements. Grounding's complete-when conditions
remain the acceptance criteria; the readiness package adds only concrete fixtures,
expected values, and edge cases. Every use starts with a `READY`, `PARTLY-READY`,
or `NOT-READY` decision record naming prerequisites, blockers, the smallest
supported slice, the next action, and verification performed.

## Post-readiness traceability

Readiness, implementation, and verification are independent. `READY` permits an
admitted slice to enter architecture and build; it does not prove an artifact
exists or a test passed. Hand stable requirement and criterion IDs plus evidence
obligations to `requirements-traceability`, which owns implementation anchors,
executed results, reverse-trace gaps, and stale-reference checks.

## When to skip

Skip when the problem and source basis are unclear; use `requirements-grounding`.
Skip when stable IDs, typed edges, dependency order, or graph checks are missing;
use `requirements-topology`.

## Next steps

- Read the operational [`implementation-readiness` SKILL.md](../.claude/skills/implementation-readiness/SKILL.md).
- Follow admitted work with [`requirements-traceability`](../.claude/skills/requirements-traceability/SKILL.md).
- Shape resulting module and service designs with [`architecture-guidelines`](../.claude/skills/architecture-guidelines/SKILL.md).
- Challenge speculative implementation surface with [`functionality-complexity-tradeoff`](../.claude/skills/functionality-complexity-tradeoff/SKILL.md).
