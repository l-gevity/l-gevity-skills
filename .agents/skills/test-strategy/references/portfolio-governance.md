# Test Portfolio Governance

Use this reference to choose test fidelity, dependencies, data, environment,
portfolio controls, and adequacy signals after obligations and candidate
techniques are known.

## Contents

- [Fidelity scorecard](#fidelity-scorecard)
- [Test-double policy](#test-double-policy)
- [Test data](#test-data)
- [Environment policy](#environment-policy)
- [Flaky-test policy](#flaky-test-policy)
- [Adequacy signals](#adequacy-signals)
- [Portfolio economics](#portfolio-economics)
- [Audit questions](#audit-questions)

## Fidelity scorecard

Compare candidate scopes without assigning one total score:

| Dimension | Favorable evidence | Warning |
| --- | --- | --- |
| Speed | Feedback arrives before the next context switch | Results arrive after review or merge decisions |
| Maintainability | Tests survive valid refactors and explain failures | Assertions bind to private structure or broad snapshots |
| Utilization | Compute, data, and environment use stay proportional | Cost grows faster than the behavior surface |
| Reliability | Same revision and conditions yield the same result | Shared state, time, order, network, or environment leaks |
| Fidelity | The actual semantics responsible for the risk are present | A double repeats an assumption instead of testing it |

Select the smallest reliable scope that preserves required fidelity. Broader is
not automatically better: it usually reduces diagnostic precision and raises
runtime, setup, and flake risk.

Keep a broader backstop when it proves something distinct:

- deployed wiring or configuration;
- compatibility with a real dependency;
- composition across ownership boundaries;
- user-visible workflow;
- environment-specific performance or resilience.

## Test-double policy

Use precise terms:

- **Stub** — supplies controlled responses; the test does not assert its
  interactions.
- **Mock** — participates in the oracle by verifying an interaction.
- **Fake** — provides a working but simplified implementation.
- **Simulator/emulator** — reproduces selected external-system semantics.

Apply these rules:

1. Use real, fast, deterministic owned collaborators by default.
2. Stub side effects when the subject is local policy and the real dependency
   adds nondeterminism, cost, destructive behavior, or unrelated setup.
3. Mock only when the interaction is itself required behavior: number,
   ordering, idempotency, absence, authorization, or atomicity of calls.
4. Use a fake only when its supported semantics are explicit and verified
   against the real implementation.
5. Exercise the real production-compatible dependency when semantic drift is
   the failure risk.
6. Never mock a third-party API from intuition. Derive the double from an
   authoritative schema, executable contract, recorded protocol, or provider
   sandbox.
7. Avoid asserting incidental internal calls. Prefer the public outcome unless
   interaction is the contract.
8. Keep time, randomness, IDs, clocks, and schedulers injectable or controlled,
   but verify their real integration where platform behavior matters.

Every double record should state:

```text
Dependency:
Double kind:
Semantics represented:
Semantics omitted:
Drift control:
Real-boundary backstop:
```

## Test data

Define data for each obligation:

```text
Source:       generated | synthetic | anonymized | seeded | production-like
Coverage:     common cases, critical journeys, boundaries, failures
Ownership:    producer and maintainer
Isolation:    per test, worker, suite, or environment
Reset:        transaction, recreate, namespace, cleanup, immutable fixture
Version:      schema/fixture/corpus version and compatibility
Privacy:      classification, minimization, retention, access
Reproduction: seed, fixture ID, failing example, environment identity
```

Defaults:

- Generate the smallest valid data inside the test when practical.
- Share builders and schemas, not mutable fixture state.
- Persist historical regression cases and minimized generated failures.
- Prefer synthetic or anonymized data over copied production data.
- Preserve realistic distributions only where distribution affects the risk.
- Provision on demand so external queues do not serialize the suite.
- Make reset deterministic and safe under parallel execution.

Production data is not automatically representative, complete, lawful to copy,
or stable enough for a test oracle.

## Environment policy

Match environment fidelity to the behavior:

| Environment | Appropriate use |
| --- | --- |
| Process/hermetic | Pure logic, properties, state machines, deterministic components |
| Container/ephemeral dependency | Database, queue, filesystem, protocol, migration semantics |
| Isolated preview | Assembled service, browser journeys, configuration, smoke checks |
| Staging/pre-production | Version skew, larger workload, recovery, integration with managed dependencies |
| Production bounded | Probes, canary observation, safe synthetic journeys, controlled experiments |

Record material differences from production. Do not call a staging test
high-fidelity when scale, configuration, data, topology, or provider behavior
differs in the dimension being tested.

Hand pipeline execution trigger, schedule, concurrency, artifact identity,
freshness, and failure action to `ci-cd-reliability-architecture`. Keep the
test's input, actor action, event, or injected fault named `stimulus`.

## Flaky-test policy

A test is flaky when unchanged relevant inputs can yield different pass/fail
results. Common causes:

- uncontrolled time, randomness, ordering, locale, or resource limits;
- shared mutable data or environment;
- async races and eventual-consistency assumptions;
- external network or provider instability;
- overly broad tests and cascading setup failures;
- environment leaks or insufficient cleanup.

Rules:

1. Reproduce and classify the nondeterminism; do not normalize blind retries.
2. Retain the original failure and retry evidence separately.
3. Fix isolation, oracle, synchronization, or environment control at the
   earliest capable stage.
4. Quarantine only to protect the main signal while repair proceeds.
5. Require quarantine owner, reason, issue, start date, expiry, and visible
   non-blocking execution.
6. Do not count quarantined, skipped, or eventually-passing retries as verified
   evidence.
7. Delete a flaky test only when its obligation is obsolete or replaced by
   equal or stronger reliable evidence.

Track flake rate per test and suite, rerun cost, quarantine age, and developer
wait time. A green result obtained after enough retries is not reliability.

## Adequacy signals

Use several independent signals:

| Signal | What it can show | What it cannot prove |
| --- | --- | --- |
| Criterion/risk mapping | Intended obligations have tests | Tests are useful or passed |
| Executed evidence | Named checks passed for a revision | Future or unobserved behavior |
| Line/branch coverage | Code was executed; gaps exist | Assertion strength or requirement satisfaction |
| Mutation results | Tests detect selected injected changes | All real faults or non-functional quality |
| Escaped-defect analysis | Portfolio missed a real failure | Absence of future defects |
| Contract/version matrix | Declared compatibility combinations | Full deployed composition |
| Critical-journey inventory | Important workflows have broad evidence | Every branch within those workflows |
| Flake and quarantine data | Evidence trust is degrading | Product correctness |
| Runtime and resource cost | Portfolio affects flow and capacity | Confidence delivered per test |

Do not choose a universal coverage or mutation threshold. Set policy by
criticality, change frequency, complexity, lifetime, external obligations, and
available alternative evidence. Explain every threshold and exclusion.

## Portfolio economics

Treat tests as maintained production assets:

- Optimize confidence per unit of feedback time and maintenance cost.
- Run fast deterministic obligations per change.
- Schedule expensive load, soak, fuzz, resilience, restore, or compatibility
  matrices according to risk and required evidence freshness.
- Keep a full-repository or otherwise unbypassable backstop when change-based
  selection can miss dependencies.
- Parallelize only tests with isolated data, environments, ports, quotas, and
  rate limits.
- Remove same-scope duplicates after the cheaper reliable replacement proves
  equivalent coverage.
- Preserve broader tests that cover a distinct boundary or failure surface.
- Treat suite duration, environment queues, data provisioning, reruns, and
  debugging time as flow costs.

Use `system-optimization` to measure and change those flow costs. Test strategy
defines the required confidence floor; optimization must not remove it.

## Audit questions

- Which requirement, risk, incident, or contract authorizes each expensive
  test?
- Which material risk has no credible oracle?
- Which tests pass without asserting a meaningful outcome?
- Which broad tests repeat branches already proven at a smaller scope?
- Which doubles can drift from production semantics?
- Which fixtures contain hidden state, sensitive data, or schema drift?
- Which tests fail for unrelated environmental reasons?
- Which quarantines have no owner or expiry?
- Which coverage targets cause low-value test creation?
- Which critical journeys rely only on mocks?
- Which non-functional thresholds lack an authoritative source?
- Which production incidents should become a smaller deterministic regression?
- Which checks need a broader unbypassable backstop rather than duplication?
