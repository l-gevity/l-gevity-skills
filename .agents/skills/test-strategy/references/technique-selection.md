# Test Technique Selection

Use this reference after a risk, failure mode, and preliminary oracle are
known. Select the technique that can falsify the expected behavior with the
least reliable cost. Do not select techniques from a generic checklist.

## Contents

- [Define the obligation](#define-the-obligation)
- [Technique matrix](#technique-matrix)
- [Functional design techniques](#functional-design-techniques)
- [Generative and model-based techniques](#generative-and-model-based-techniques)
- [Boundary and journey techniques](#boundary-and-journey-techniques)
- [Human evaluation](#human-evaluation)
- [Quality-risk routing](#quality-risk-routing)
- [Selection guardrails](#selection-guardrails)

## Define the obligation

Freeze this record before selecting a technique:

```text
Risk / criterion:
Failure mode:
Source of truth:
Pass / fail oracle:
Impact and exposure:
Known blind spots:
```

If the source of truth or oracle is missing, return to the requirement,
contract, specialist policy, or owner. A sophisticated harness cannot repair an
ambiguous expected result.

## Technique matrix

| Risk shape | Primary technique | Distinct confidence supplied |
| --- | --- | --- |
| Named example or acceptance case | Example-based test | Proves one important case |
| Inputs form valid/invalid classes | Equivalence partitioning | Samples each behavior class |
| Risk clusters at limits | Boundary-value analysis | Exercises transitions and off-by-one faults |
| Several conditions determine outcomes | Decision table | Covers meaningful rule combinations |
| Pair combinations dominate a large configuration space | Pairwise/combinatorial | Reduces combinations with declared interaction strength |
| Behavior depends on state and transitions | State-transition test | Covers states, events, invalid moves, and sequences |
| A model can predict system behavior | Model-based test | Generates paths and compares with the model |
| An invariant holds over broad inputs | Property-based test | Searches for counterexamples and shrinks failures |
| Output has no simple expected value but relations hold | Metamorphic test | Verifies relations across transformed inputs |
| Two independent implementations should agree | Differential test | Uses disagreement as the failure signal |
| Parser or untrusted input has a huge surface | Coverage-guided fuzzing | Finds crashes, hangs, and invariant violations |
| Consumer and provider evolve independently | Contract test | Detects expectation or compatibility drift |
| Production implementation semantics matter | Real-boundary integration test | Exercises the actual database, queue, SDK, filesystem, or runtime |
| Critical value crosses the assembled system | E2E journey test | Verifies irreducible composition and user-visible outcome |
| Unknown behavior or weak specification | Exploratory testing | Discovers risks and hypotheses not encoded in automation |
| Performance or capacity threshold matters | Benchmark/load family | Measures behavior under a declared workload |
| Known failure response matters | Deterministic fault injection | Verifies timeout, retry, fallback, failover, and recovery |
| Unknown systemic weakness matters | Chaos experiment | Challenges a steady-state hypothesis under controlled disruption |

## Functional design techniques

### Example-based

Use for:

- canonical business examples;
- acceptance criteria with concrete inputs and outputs;
- regressions for previously escaped defects;
- cases whose meaning matters more than input-space breadth.

Include a meaningful assertion on the outcome or state transition. Avoid
examples that only prove code executed.

### Equivalence partitions and boundaries

Partition inputs by behavior, not data type alone. Include valid and invalid
classes, then exercise every material boundary and its nearest meaningful
neighbors. Use this for ranges, dates, sizes, permissions, lifecycle phases,
and schema constraints.

### Decision tables and combinations

Use a decision table when independent conditions jointly determine actions.
Remove impossible combinations using authoritative constraints. Use pairwise or
stronger combinatorial coverage only after declaring which interaction strength
is sufficient; it does not replace known high-risk combinations.

### State transitions

Model:

- valid states;
- events and guards;
- permitted and forbidden transitions;
- entry/exit effects;
- timeouts, retries, cancellation, and recovery.

Test paths that carry business or operational risk. Do not enumerate every path
when a smaller transition or model coverage obligation is sufficient.

## Generative and model-based techniques

### Property-based

Use when an invariant is clearer than a list of cases. Common properties:

- round trip: decode(encode(x)) preserves x;
- conservation: totals or balances remain invariant;
- idempotency: applying an operation twice matches applying it once;
- ordering: results are sorted or monotonic;
- equivalence: optimized and reference implementations agree;
- closure: valid inputs produce valid outputs;
- no-crash: all schema-valid inputs complete safely.

Declare the input domain and persist minimal failing counterexamples. Combine
generated cases with explicit examples for known regulatory, contractual, or
historical boundaries.

### Metamorphic

Use when exact expected output is expensive or unavailable but a transformation
implies a relation. Examples include scale invariance, permutation invariance,
format conversions, monotonicity, or adding irrelevant data without changing a
decision.

### Differential

Compare two independently derived implementations, versions, providers, or a
simple reference model. Independence matters: two adapters sharing the same
faulty assumption do not create a useful oracle.

### Stateful or model-based

Generate action sequences against an explicit model. Use for caches, queues,
financial ledgers, protocols, editors, distributed workflows, or resources with
create/update/delete lifecycle. Preserve the failing sequence and initial state.

### Fuzzing

Use for parsers, codecs, protocol handlers, native code, security boundaries,
and other broad untrusted-input surfaces. Define:

- target and invariant;
- seed corpus;
- resource/time limits;
- sanitizers or runtime diagnostics;
- crash deduplication and reproduction;
- corpus persistence and scheduled/continuous execution.

Fuzzing without an invariant beyond “did not crash” supplies only crash
resistance, not business correctness.

## Boundary and journey techniques

### Contract tests

Use a shared schema or executable consumer/provider contract where systems
evolve independently. Cover used interactions, compatibility expectations,
error shapes, authorization semantics, and version skew. Contract tests do not
prove infrastructure wiring or the whole deployed journey.

### Real-boundary integration

Exercise the production-compatible implementation when behavior depends on:

- query, transaction, isolation, or migration semantics;
- queue ordering, delivery, redelivery, or acknowledgement;
- serialization and wire compatibility;
- filesystem, locale, clock, or operating-system behavior;
- framework routing, middleware, dependency injection, or configuration;
- an external SDK or service contract.

Keep cases focused on the boundary. Test combinatorial domain logic at a
smaller scope.

### End to end

Retain E2E tests for a small number of critical journeys and irreducible
composition risks. Interact through stable user-visible or public behavior.
Avoid restating every lower-level branch. Record which composition risk makes
the broader test necessary.

### Production probes and canaries

Use production probes for safe, known requests and expected outcomes. Use a
canary to limit exposure and compare release signals; do not treat it as a
deterministic pre-production test. Hand traffic, thresholds, rollback, and
verification windows to `ci-cd-reliability-architecture`.

## Human evaluation

Use exploratory, usability, accessibility, or acceptance evaluation when:

- expected quality depends on human perception or task success;
- automation covers only part of the standard;
- the specification is weak and discovery is the purpose;
- rare combinations, workflows, or abuse patterns need skilled investigation.

Give exploratory work a charter, scope, time box, evidence capture, and follow-up
owner. Human does not mean informal; automated does not mean objective.

## Quality-risk routing

| Quality risk | Strategy decision | Specialist hand-off |
| --- | --- | --- |
| Performance | Workload model, scenario, measure, threshold need | Performance/SRE policy; CI/CD for cadence |
| Reliability | Known failure mode and recovery oracle | Resilience/SRE policy |
| Chaos | Steady-state hypothesis and blast-radius controls | Operations/SRE owner |
| Security | Threat or security requirement to verify | Security baseline/OWASP/domain skill |
| Accessibility | Applicable criterion and manual/automated split | Accessibility specialist |
| Usability | Actor task and success measure | UX/user research |
| Recovery | RPO/RTO, restore, reconciliation, data-integrity oracle | Operations/data owner |
| Compatibility | Consumers, providers, versions, schemas | Contract/API owner |

Do not invent thresholds or compliance scope. Return `DEFER` when the
authoritative policy or owner is missing.

## Selection guardrails

- Do not prescribe a universal unit/integration/E2E ratio.
- Do not use E2E merely because the behavior is important.
- Do not use unit tests for semantics that only a real boundary provides.
- Do not generate cases without a falsifiable property or oracle.
- Do not claim pairwise coverage includes a known three-way interaction.
- Do not treat a canary, monitor, or chaos experiment as equivalent to a
  deterministic regression test.
- Do not automate exploratory or human-centered judgment into a weak proxy just
  to make it blocking.
