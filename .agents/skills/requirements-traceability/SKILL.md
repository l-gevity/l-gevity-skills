---
name: requirements-traceability
description: >-
    Maintains bidirectional traceability between canonical requirements and
    implementation, verification, decision, operational, and outcome evidence.
    Use when planning, implementing, reviewing, or closing work that must prove
    which requirement authorized a change, where it is implemented, which
    executed evidence verifies it, whether a linked outcome hypothesis is
    supported by current measurement, what remains unmapped, or whether
    references have gone stale. Do not use to invent requirement or hypothesis
    meaning, normalize the requirement graph, decide implementation readiness,
    or issue a functionality-worth verdict.
---

# Requirements Traceability

Keep requirement intent connected to implementation and executed evidence
without turning code, tests, or a trace registry into a second requirements
source.

> **Core Directives**
>
> 1. **Canonical requirements keep meaning.** Trace links identify evidence;
>    they never authorize new product, policy, legal, or domain behavior.
> 2. **Trace both directions.** Check requirement to evidence and changed
>    artifact to requirement or an explicit non-requirement rationale.
> 3. **Implementation is not verification.** A code anchor or test definition
>    proves coverage exists; only an executed passing result proves verification.
> 4. **Place anchors naturally.** Prefer stable IDs in contracts, tests, ADRs,
>    operations evidence, and issue closeout over a duplicate central registry.
> 5. **Fail on stale references.** Unknown IDs, removed criteria, ambiguous
>    aliases, and unverifiable success claims are blocking trace defects.
> 6. **Completion is not outcome evidence.** Acceptance and implementation
>    evidence may verify a capability; only a linked, representative measurement
>    can assess its downstream outcome hypothesis.
> 7. **Every representation gap names its expiry condition.** A declared
>    asymmetry without the condition that ends it becomes permanent by accident.

## Boundary

Use this skill after a passing `implementation-readiness` decision when work
enters architecture, implementation, verification, review, or closeout.

Use `requirements-grounding` to establish meaning and authority,
`requirements-topology` to own IDs, relationships, lineage, schemas, and
generated views, and `implementation-readiness` to decide whether work may
start. Apply the project's requirements profile for repository paths, ID
formats, evidence stores, commands, and classifications.

This skill owns live evidence relationships and outcome-evidence state.
`requirements-grounding` owns hypothesis meaning, thresholds, guardrails, and
revisit intent. `functionality-complexity-tradeoff` owns the resulting
functionality-worth verdict. This skill does not add another stage or letter to
A.L.C.H.E.M.Y.

## Minimum Inputs

Require:

- canonical requirement and acceptance-criterion IDs for completion tracing;
- canonical outcome-hypothesis IDs and versions when outcome evidence is in
  scope;
- the passing readiness decision and admitted slice;
- the changed implementation, contract, decision, or operations artifacts;
- the project's accepted anchor forms and executable verification sources;
- commit, build, run, or environment identity when operational evidence is
  offered as proof.

If canonical IDs or criterion references are unstable, return to
`requirements-topology`. If the admitted slice or acceptance conditions are
unclear, return to `implementation-readiness`.

## Completion Evidence States

Classify every criterion independently:

| State | Required evidence | What it does not prove |
| --- | --- | --- |
| `unmapped` | No accepted implementation or verification anchor | Whether work is planned elsewhere |
| `implemented` | Stable implementation anchor or executable test definition | That the behavior passed |
| `verified` | Implemented anchor plus a passing test or accepted operational result for this revision | Continued correctness after later changes |
| `blocked` | Named missing dependency, decision, environment, or evidence owner | That the requirement may be silently skipped |
| `not-applicable` | Explicit scoped rationale approved by the requirement owner | A general waiver for other slices or actors |

A passed test tag without a matching test definition is not verification. A test
definition without a result is implementation evidence only. Operational
evidence without revision and run identity is an observation, not reproducible
proof.

## Outcome Evidence States

Classify each linked empirical hypothesis independently for its exact version:

| State | Required evidence | What it does not prove |
| --- | --- | --- |
| `unmeasured` | No accepted representative observation yet | That the expected impact is absent |
| `supported` | Current evidence covers the defined cohort and window, meets the primary threshold, and satisfies the guardrails | That implementation remains complete or the causal explanation is universally true |
| `rejected` | Current evidence misses the primary threshold or violates a required guardrail | That the underlying actor problem never existed |
| `inconclusive` | Evidence exists but cannot support or reject the hypothesis because of power, exposure, attribution, quality, or guardrail gaps | That value is zero or that more measurement will resolve the ambiguity |
| `stale` | Earlier evidence was invalidated by its freshness rule or a material change to the cohort, capability, measure, environment, or hypothesis | A current worth decision |

Use the hypothesis's declared threshold, window, cohort, and guardrails. Never
rewrite them to fit observed data. If a causal claim is material but the evidence
cannot distinguish the capability's effect from confounders, classify it
`inconclusive`, not `supported`.

When Grounding records outcome hypotheses as `not applicable` for an
authoritative obligation, carry its scope and reason into the trace summary but
do not create an outcome-evidence record. Completion evidence remains required.

Use this linked record:

```text
Outcome evidence: <hypothesis slug>
Hypothesis version: <canonical source and version>
Applies to requirements: <requirement slugs>
Observation identity: <dataset, query, study, experiment, or run reference>
Cohort and exposure: <who was measured and evidence they used the capability>
Measurement window: <start/end or bounded period>
Baseline: <value and source, or unavailable + limitation>
Observed result: <primary measure result>
Threshold evaluation: met | missed | not-evaluable
Guardrail results: <each guardrail result or missing>
Comparison or attribution: <method, or unavailable + limitation>
Freshness: current | stale — <rule or invalidating change>
Evidence state: unmeasured | supported | rejected | inconclusive | stale
Confidence: low | medium | high
Owner: <evidence owner>
Next measurement or revisit: <trigger, date, or none + reason>
```

The evidence state is a projection over an immutable hypothesis version, not a
rewrite of canonical meaning. A new threshold, cohort, measure, or causal claim
creates a new hypothesis version and invalidates dependent assessments.

## Workflow

1. Resolve the canonical requirement set, version, and admitted slice.
2. Inventory changed or planned artifacts at public boundaries: contracts,
   commands, events, exports, routes, domain rules, migrations, domain and data
   model views, tests, ADRs, runbooks, and deployment evidence.
3. Reuse stable requirement and criterion IDs; resolve aliases only through the
   canonical lineage model.
4. Place the smallest useful anchor in the artifact a maintainer will inspect
   first.
5. Map each criterion to implementation and verification evidence separately.
6. When linked outcome hypotheses are in scope, map each hypothesis version to
   its measurement plan and current observation; evaluate exposure, threshold,
   guardrails, attribution limits, and freshness separately from completion.
7. Reverse-check each non-trivial changed artifact for a requirement ID or an
   explicit `platform`, `operations`, `technical-debt`, `spike`, or
   `product-gap` or `outcome-evidence` rationale.
8. Classify gaps, stale references, and stale outcome assessments.
9. Run the repository's blocking trace check and the closest behavior tests.
10. Emit the trace decision and unresolved owners before closeout.

## Anchor Placement

| Artifact | Preferred stable anchor |
| --- | --- |
| Contract or public API | Requirement ID in schema metadata, operation metadata, or contract test |
| Domain behavior | Named rule/function plus a criterion-tagged behavior test |
| UI or workflow | Stable route/action/state identifier plus acceptance test |
| Data or migration | Schema/migration identifier plus compatibility or migration test |
| Domain or data model view | Stable entity/node identifier plus the requirement IDs that authorize it |
| ADR or architecture record | Requirement IDs in the decision context |
| Operations | Runbook/check identifier plus revision, environment, run, and outcome |
| Issue or change record | Canonical IDs, admitted slice, evidence links, and named gaps |

Do not add long requirement prose to source files when the ID and a nearby
contract or test already preserve the relationship.

## Formal Completion Records

Formalize completion in the project's natural issue or change record. Do not
rewrite canonical requirement meaning, approval, or readiness state merely to
signal that delivery finished. Completion evidence, release state, and outcome
evidence remain independent.

Close the record only when it preserves:

- the bounded canonical requirement and criterion IDs;
- the completion boundary, such as acceptance, release, or production;
- the exact revision, artifact, environment, and executed run evidence;
- implementation and verification anchors;
- evidence freshness when the operational proof can expire; and
- named gaps, deferrals, and owners without implying a broader completion state.

Use repository markers according to the repository's existing convention:

- an immutable checkpoint or tag is optional when the exact source snapshot
  matters; its name must not imply release, production, or outcome proof that
  the evidence does not establish;
- a milestone groups multiple work items toward a shared objective; do not
  invent one for a single closeout unless the project explicitly uses that
  convention; and
- keep unresolved release or production work separate from an accepted slice.

```text
Completion record:
- Subject: <capability or bounded slice>
- Decision: TRACEABLE | PARTIAL | BLOCKED
- Canonical scope: <requirement and criterion IDs>
- Completion boundary: <acceptance | release | production | other>
- Revision/artifact/environment: <immutable identities>
- Implementation: <stable anchors>
- Executed evidence: <run identities and results>
- Evidence freshness: <current through date, stale, or not applicable>
- Gaps/deferred: <gap, owner, and follow-up record>
- Outcome status: <linked states or not assessed>
- Repository marker: <change record; optional checkpoint; aggregate milestone>
```

## Gap Taxonomy

| Gap | Meaning |
| --- | --- |
| `missing-requirement` | Work may be justified but has no canonical requirement or accepted rationale |
| `missing-implementation` | Requirement exists but no implementation anchor covers it |
| `missing-test` | Implementation exists but no executable verification covers it |
| `stale-reference` | Anchor targets an unknown, replaced, or removed ID or criterion |
| `scope-deferred` | Work is intentionally later and cites an accepted deferral |
| `decision-blocked` | An unresolved product, policy, platform, or ownership decision blocks proof |
| `evidence-unreproducible` | Claimed evidence lacks revision, run, environment, or result identity |
| `outcome-unmeasured` | A decision-relevant hypothesis has no accepted observation |
| `outcome-stale` | Outcome evidence no longer satisfies its freshness rule |
| `outcome-not-evaluable` | Threshold, exposure, window, guardrail, or attribution evidence is insufficient |
| `representation-aggregated` | One artifact carries several canonical concepts because they share a write or release unit |
| `representation-derived` | A concept exists only as a computation; the computation's source is named |
| `representation-projected` | A concept is rebuilt from another artifact's records rather than stored |

## CI Enforcement

Put deterministic trace checks in the earliest capable blocking gate:

- validate anchor syntax while authoring when editor tooling can do so;
- reject unknown IDs, criteria, aliases, and stale references in static CI;
- reject a representation gap that names no expiry condition;
- require criterion-tagged tests to exist before accepting test-result tags;
- ingest executed test results before promoting `implemented` to `verified`;
- require operational evidence to carry revision and run identity;
- reject unknown hypothesis IDs and outcome assessments that omit the hypothesis
  version, observation identity, window, threshold evaluation, or freshness;
- invalidate current outcome assessments when their hypothesis version or
  declared freshness inputs change;
- report coverage counts, but never convert a percentage target into invented
  requirement meaning.

Keep fast local checks for feedback and a full-repository CI backstop for
unbypassable coverage. Automation may validate links, record shape, and explicit
freshness; it cannot manufacture causal validity from structurally complete
fields. Route gate placement through `defect-shift-left`.

## Output Contract

```text
Subject:             <change, slice, release, or requirement scope>
Decision:            TRACEABLE | PARTIAL | BLOCKED
Canonical source:    <requirement set and version>
Requirement IDs:     <IDs covered>
Implemented:         <criteria count and anchors>
Verified:            <criteria count and executed evidence>
Outcome hypotheses:  <IDs + unmeasured/supported/rejected/inconclusive/stale/not-applicable>
Outcome evidence:    <current measurement links, or none>
Reverse-trace gaps:  <changed artifacts without requirement/rationale>
Stale references:    <none or exact references>
Representation gaps: <class, artifact, and expiry condition, or none>
Other gaps:          <gap taxonomy entries and owners>
Next action:         <implement, test, decide, repair reference, or close>
Verification:        <trace check and tests run, or Not run + reason>
```

For implementation or review closeout, append a compact note:

```text
Trace:
- Source: <requirement set, issue, or admitted slice>
- IDs: <requirement and criterion IDs>
- Implementation: <stable artifacts>
- Evidence: <executed tests or operational results>
- Outcomes: <hypothesis IDs, evidence states, freshness, and observation links>
- Gaps/deferred: <none or named gaps; representation gaps carry expiry>
```

## Guardrails

- Do not mark a requirement verified because code, a route shell, a fixture, or
  a test definition exists.
- Do not use issue text as canonical when it conflicts with requirements.
- Do not hide unrelated work under a convenient requirement ID.
- Do not duplicate every trace edge in a giant registry and nearby artifacts.
- Do not use completion, deployment, adoption, or telemetry presence alone as
  evidence that an outcome hypothesis is supported.
- Do not change a hypothesis threshold, cohort, window, or guardrail in an
  evidence record; return meaning changes to `requirements-grounding`.
- Do not issue BUILD, KEEP, SIMPLIFY, DROP, or removal decisions; hand current
  outcome evidence to `functionality-complexity-tradeoff`.
- Do not recycle IDs; follow topology lineage after splits, merges, and
  replacements.
- If grounding, topology, or readiness changes materially, invalidate or refresh
  affected trace decisions.

## See also

- `requirements-grounding` — requirement meaning, source authority, and evidence.
- `functionality-complexity-tradeoff` — worth decisions using current outcome evidence.
- `requirements-topology` — stable IDs, lineage, graph semantics, and repository gates.
- `implementation-readiness` — admitted implementation slice and verification obligations.
- `defect-shift-left` — earliest blocking placement for trace checks.
