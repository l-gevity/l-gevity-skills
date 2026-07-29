# Test Strategy

`test-strategy` turns accepted behavior and quality risks into the smallest
sufficient portfolio of trustworthy evidence. It answers **what must be
proved, with which oracle, technique, scope, dependency fidelity, data, and
environment**.

It does not prescribe a universal test pyramid or coverage target. A fast test
that cannot observe the named failure is cheap noise; a broad test that adds no
distinct confidence is expensive duplication.

## Fundamental principle

Work in this order:

```text
requirement or risk
→ observable failure mode
→ credible oracle
→ accepted architecture
→ technique
→ smallest sufficient fidelity
→ dependency, data, and environment policy
→ residual risk
```

Choose tests by the failure they must detect, not by a preferred framework or
test-level ratio.

## The workflow

1. **Qualify the subject.** Bound the strategy to a requirement slice,
   component, contract, workflow, change, or release risk.
2. **Build the risk ledger.** Keep impact, exposure, and evidence confidence
   separate. Unknown exposure is not low exposure.
3. **Define the oracle.** Name the source of truth, pass/fail observation,
   tolerances, and false-pass risk before selecting a harness.
4. **Refine after architecture.** Revisit the portfolio after accepted
   architecture fixes the relevant boundaries and dependency semantics.
5. **Select the technique.** Match examples, boundaries, decisions, states,
   properties, fuzzing, contracts, real-boundary integration, E2E journeys, or
   human evaluation to the risk shape.
6. **Select fidelity.** Compare candidates across speed, maintainability,
   utilization, reliability, and fidelity. Keep the smallest scope that can
   faithfully observe the failure.
7. **Govern dependencies, data, and environments.** Use doubles deliberately,
   control drift, isolate data, and make evidence reproducible.
8. **Audit adequacy.** Find missing obligations, hollow assertions, redundant
   broad tests, stale doubles, flaky results, and unowned quarantines.

The decision is `ADEQUATE`, `PARTIAL`, `NOT-ADEQUATE`, or `DEFER`. Counts,
coverage percentages, a pyramid shape, and green CI cannot produce
`ADEQUATE` by themselves.

## Alchemy alignment

`test-strategy` is a task-matched Alchemy companion, not another letter, gate,
or qualification stage. Use it when verification design is material:

```text
Implementation Readiness
→ Test Strategy — Obligation pass: risks, failure modes, oracles, confidence
→ A/L/C/E: accepted architecture and enforcement
→ Test Strategy — Portfolio pass: technique, scope, fidelity, dependencies,
  data, environment, stimulus
→ Defect Shift-Left: earliest capable stage
→ CI/CD Reliability: execution trigger, gate, artifact, freshness, failure action
→ Requirements Traceability: implemented and executed-evidence state
→ System Optimization: suite flow, cost, duplication, and bottlenecks
```

Use a Combined pass only for a stable accepted architecture. A test `stimulus`
is the input, actor action, event, state transition, time condition, or injected
fault exercised by a test; it is not the CI/CD execution trigger.

This separation matters:

- `implementation-readiness` supplies admitted criteria and obligations;
- `test-strategy` designs the risk-driven evidence portfolio;
- `defect-shift-left` places each check at the earliest capable stage;
- `ci-cd-reliability-architecture` runs and gates it reliably;
- `requirements-traceability` distinguishes a test definition from passing,
  revision-specific proof.

## Test doubles and real boundaries

Use a stub for controlled responses, a mock when the interaction itself is
required behavior, and a fake only when its supported semantics and drift
control are explicit. Exercise a production-compatible dependency when
database, wire, queue, framework, migration, or provider semantics create the
risk.

A double representing an external boundary needs a schema, executable
contract, recorded protocol, provider sandbox, or real-boundary backstop.

## Portfolio health

Use several signals together:

- criterion and risk mappings;
- executed evidence for the relevant revision;
- coverage as a gap locator;
- selective mutation testing for assertion strength;
- escaped-defect analysis;
- contract and version matrices;
- flake rate, quarantine age, runtime, and resource cost.

A quarantined, skipped, or eventually-passing retry cannot count as verified
evidence. Keep unknowns and accepted residual risks visible.

## When to skip or hand off

Return to requirements work when expected behavior, permissions, actors, or
completion conditions are unclear. Hand framework-specific implementation to
the matching stack skill, specialist security/accessibility/safety policy to
the relevant domain skill, pipeline placement to `defect-shift-left`, and
execution policy to `ci-cd-reliability-architecture`.

For the complete workflow, decision rules, output contract, technique matrix,
and portfolio-governance reference, read the canonical
[`test-strategy` skill](../.claude/skills/test-strategy/SKILL.md).
