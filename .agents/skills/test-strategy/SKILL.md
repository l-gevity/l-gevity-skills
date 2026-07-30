---
name: test-strategy
description: >-
    Designs and audits risk-driven test strategies that map grounded
    requirements, acceptance criteria, quality risks, architecture, and escaped
    defects to the smallest sufficient evidence portfolio. Use when deciding
    what to test, which design technique or test fidelity to use, when to use
    real dependencies versus fakes, stubs, or mocks, how to manage test data
    and environments, or whether unit, component, integration, contract, E2E,
    exploratory, property, fuzz, performance, resilience, or recovery testing
    is justified. Also use to audit hollow assertions, redundant coverage,
    flaky tests, and residual risk. Do not use for framework-specific test
    implementation, pipeline placement or gating, or trace evidence state;
    hand those to stack skills, defect-shift-left,
    ci-cd-reliability-architecture, and requirements-traceability.
---

# Test Strategy

Convert accepted behavior and quality risks into the smallest reliable evidence
portfolio. Choose tests by the failure they must detect, not by a universal
pyramid ratio, coverage target, or preferred tool.

## Core Directives

1. **Risk before test type.** Start from a requirement, failure mode, quality
   risk, incident, or contract. Never start from “we need more unit tests.”
2. **Oracle before harness.** State how correct and incorrect behavior can be
   distinguished before selecting a test level, framework, or environment.
3. **Minimum sufficient fidelity.** Use the smallest scope that can faithfully
   observe the named failure. Add broader tests only for distinct confidence.
4. **Evidence over percentages.** Coverage locates unexecuted code; it does not
   prove useful assertions, satisfied requirements, or acceptable residual risk.
5. **Real boundaries where semantics matter.** A fast double cannot prove
   database, wire, framework, migration, or provider compatibility.
6. **Reliability is part of validity.** A flaky or order-dependent result is not
   trustworthy verification.
7. **Keep unknowns visible.** Record untested risks, manual obligations, missing
   environments, and accepted residual risk instead of silently marking them
   covered.

## Boundary

Use this skill after a requirement or remediation slice has usable completion
conditions, or retrospectively when an existing behavior, incident, or test
portfolio provides a bounded subject. In Design mode, use two passes when
architecture can change boundaries, dependency semantics, deployment topology,
or observability:

1. **Obligation pass — after readiness, before A.** Define risks, failure
   modes, oracles, and required confidence without freezing architecture-
   dependent scope or fidelity.
2. **Portfolio pass — after final A/L/C and E when applicable, before H.**
   Consume the accepted architecture and finalize technique, scope, fidelity,
   dependencies, data, environment, and stimulus.

Use a **Combined pass** only for Audit mode against a stable architecture, or
when the relevant architecture is already accepted and will not change.

Consume:

- canonical requirement and acceptance-criterion IDs when available;
- actor workflows, contracts, current or accepted architecture boundaries, and
  data ownership;
- functional and quality constraints;
- historical defects, incidents, change hotspots, and production signals;
- delivery, environment, privacy, compliance, and cost constraints.

If requirement meaning, actors, permissions, or completion conditions are
unclear, return to `requirements-grounding` or `implementation-readiness`.
Existing tests and code are evidence, not product intent.

This skill owns:

- the risk-to-evidence mapping;
- the oracle, technique, scope, fidelity, dependency, data, and environment
  decisions for each test obligation;
- portfolio adequacy, duplication, and residual-risk analysis.

This skill does not own:

- requirement meaning or readiness;
- implementation recipes for a specific test framework;
- the earliest pipeline stage, job structure, blocking action, or evidence
  freshness;
- the distinction between implemented and executed/verified evidence;
- specialist security, accessibility, safety, or domain policy.

Use this Alchemy hand-off when both passes apply:

```text
Implementation Readiness
→ Test Strategy — Obligation pass: risks, failure modes, oracles, confidence
→ A → L/C → E, as justified: accepted architecture and enforcement
→ Test Strategy — Portfolio pass: technique, scope, fidelity, dependencies,
  data, environment, stimulus
→ Defect Shift-Left: earliest capable stage
→ CI/CD Reliability: execution trigger, gate, artifact, freshness, failure action
→ Requirements Traceability: implementation and executed-evidence state
→ System Optimization: suite flow, cost, duplication, and bottlenecks
```

Do not restart the Obligation pass after architecture unless the architecture
changes requirement meaning, a failure mode, or an oracle. If accepted
architecture changes after the Portfolio pass, rerun only the affected
portfolio rows before handing them to H.

`test-strategy` is a task-matched Alchemy companion. It is not a new
A.L.C.H.E.M.Y. letter, qualification stage, or gate.

## Workflow

### 1. Qualify the subject

Select a mode:

- **Design** — derive evidence obligations for admitted or clearly bounded work.
- **Audit** — assess an existing portfolio against current requirements, risks,
  incidents, and architecture.

In Design mode, also select the strategy pass defined under Boundary:
Obligation, Portfolio, or Combined.

Define the subject as a requirement slice, component, contract, workflow,
change, release risk, or bounded system. Do not strategize for “the whole
application” when no risk or decision boundary is stated.

### 2. Build the risk ledger

For each material risk, record:

```text
Risk / criterion: <canonical ID or named risk>
Failure mode:     <observable wrong outcome>
Impact:           <user, business, security, operational, or compliance harm>
Exposure:         <where and how plausibly it occurs>
Risk evidence:    <requirement, incident, telemetry, contract, or assumption>
```

Keep impact, exposure, and evidence confidence separate. Do not collapse them
into one score. Unknown exposure is not low exposure. External legal,
contractual, accessibility, safety, or security obligations remain required
even when usage is low.

### 3. Define the oracle

For every required obligation, state:

- the source of truth;
- the observable pass and fail condition;
- tolerances, time windows, ordering, or eventual-consistency rules;
- false-pass and false-fail risks;
- the data and instrumentation needed to observe the result.

If no credible oracle exists, emit `DEFER` for that obligation and name the
missing requirement, contract, signal, or human judgment. A test that merely
runs code or asserts “not null” is not evidence unless that is the actual
criterion.

### 4. Select the technique

Read [references/technique-selection.md](references/technique-selection.md)
when the technique is not obvious, the subject has several failure modes, or
property, model-based, contract, fuzz, exploratory, performance, resilience, or
recovery testing may apply.

Select the technique that attacks the risk directly:

- examples for named business cases;
- partitions and boundaries for classified input ranges;
- decision tables or combinations for interacting rules;
- state-transition or model-based tests for workflows;
- property, metamorphic, or differential tests for invariants and broad input;
- contract or real-boundary integration tests for compatibility;
- a few E2E tests for irreducible critical journeys;
- exploratory or user evaluation for unknown, subjective, or human-centered
  risks.

Record why each rejected technique would add less confidence or more cost. In
an Obligation pass, stop at the architecture-independent technique family; the
Portfolio or Combined pass fixes the concrete harness and scope.

### 5. Select scope and fidelity

Describe every proposed test by its:

```text
System under test | exercised dependencies | environment | stimulus | oracle
```

`stimulus` is the input, actor action, event, state transition, elapsed time, or
injected fault exercised by the test. It is not the CI/CD execution trigger
(push, pull request, schedule, manual dispatch, deployment, or production
event), which belongs to `ci-cd-reliability-architecture`.

Only then apply labels such as unit, component, integration, contract, system,
E2E, or production probe. Labels vary across teams; the five dimensions above
must not.

Compare candidate scopes on speed, maintainability, utilization, reliability,
and fidelity with the scorecard in
[references/portfolio-governance.md](references/portfolio-governance.md).

Prefer the smallest candidate whose fidelity can observe the failure. Keep a
broader test only when it covers composition, environment, or behavior the
smaller test cannot.

### 6. Decide dependencies, data, and environment

Read the same reference for test doubles, production-compatible dependencies,
test data, environment isolation, quarantine policy, adequacy signals, and
suite budgets.

Apply these defaults:

- Use real, deterministic, in-process owned collaborators.
- Stub slow, nondeterministic, destructive, or unavailable side effects when
  testing local decisions.
- Use a mock only when the interaction itself is required behavior.
- Exercise the real dependency when compatibility or provider semantics are
  the risk.
- Protect every double that represents an external boundary with a shared
  schema, executable contract, or real-boundary backstop.
- Make data self-contained, resettable, privacy-safe, versioned where needed,
  and provisionable in parallel.

### 7. Complete the quality scan

Check the applicable surface without inventing requirements:

- functional correctness and actor outcomes;
- compatibility, concurrency, version skew, and migrations;
- performance, capacity, and resource use;
- reliability, resilience, recovery, and data integrity;
- security, privacy, compliance, and auditability;
- usability, accessibility, and supported environments;
- operability, configuration, deployment, and production verification.

When a quality area is material but lacks an authoritative requirement or
specialist policy, record a blocker or route to the matching companion skill.
Do not manufacture thresholds.

### 8. Audit the portfolio

In Audit mode:

1. Map current tests to risks, criteria, boundaries, and observed incidents.
2. Find missing obligations, hollow oracles, stale tests, unverified doubles,
   excessive E2E coverage, and same-scope duplicates.
3. Treat every escaped defect as evidence that the portfolio missed a risk,
   technique, oracle, fidelity, or placement decision.
4. Treat flakes, order dependence, uncontrolled time, shared state, and
   environment leakage as test defects.
5. Use coverage as a gap locator. Use mutation testing selectively on changed
   or high-risk deterministic logic when assertion strength is uncertain.
6. Remove a redundant broader test only after the smaller replacement proves
   the same scope; keep distinct broader backstops.

A quarantine must name an owner, reason, expiry, and retained signal. A
quarantined test cannot count as verified evidence.

### 9. Hand off

- Hand selected checks to `defect-shift-left` only after a Portfolio or
  Combined pass finalizes their architecture-dependent fields.
- Send pipeline execution triggers, schedules, blocking behavior, artifacts,
  freshness, and failure actions to `ci-cd-reliability-architecture`.
- Send criterion mappings and executed results to
  `requirements-traceability`.
- Send suite latency, resource cost, flakiness, queues, and duplication to
  `system-optimization`.
- Send security, accessibility, safety, UX, data, or domain-specific
  obligations to the applicable companion skill without weakening them.

## Decision Rules

| Condition | Decision |
| --- | --- |
| Every material risk has a credible oracle and sufficient evidence path | `ADEQUATE` |
| The critical path is covered but named residual gaps remain | `PARTIAL` |
| A material risk has no credible evidence path, or the portfolio gives false confidence | `NOT-ADEQUATE` |
| Meaning, oracle, environment, specialist policy, or owner is unresolved | `DEFER` |

An Obligation pass is provisional by design and cannot emit `ADEQUATE`. Reserve
`ADEQUATE` for a Portfolio or Combined pass against accepted architecture.

Do not emit `ADEQUATE` from test counts, pyramid shape, coverage percentage,
green CI, or one successful release.

## Output Contract

Emit one row per material obligation:

| Risk / criterion | Failure mode | Oracle | Technique | Scope / fidelity | Dependencies | Data / environment | Evidence | Residual blind spot |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Then emit:

```text
Subject:              <requirement, slice, component, change, or system>
Mode:                 Design | Audit
Strategy pass:        Obligation | Portfolio | Combined
Decision:             ADEQUATE | PARTIAL | NOT-ADEQUATE | DEFER
Test basis:           <requirements, criteria, contracts, incidents, signals>
Architecture basis:   <not yet fixed | accepted decision refs | stable existing>
Quality risks:        <ranked risks or none found>
Manual evaluation:    <exploratory, usability, accessibility, acceptance, none>
Adequacy signals:     <trace coverage, gaps, mutation, escaped defects, flakes>
Handoffs:             <shift-left, CI/CD, traceability, optimization, companions>
Residual risk:        <accepted, blocked, deferred, unknown, or none identified>
Next action:          <one concrete evidence, decision, or removal step>
Verification:         <portfolio/test review, commands, results, or Not run + reason>
```

## Guardrails

- Do not invent requirement meaning, thresholds, users, traffic, or risk
  acceptance.
- Do not use a test framework preference as a strategy.
- Do not require every technique for every system.
- Do not equate mocks with isolation or real dependencies with confidence.
- Do not automate subjective evaluation merely to make it countable.
- Do not retain expensive tests because they were expensive to create.
- Do not claim an ownership boundary listed under Boundary; hand it off.
