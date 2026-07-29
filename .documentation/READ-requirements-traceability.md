# Requirements Traceability

Requirements Traceability keeps a requirement connected to implementation and
executed evidence after readiness has admitted work into architecture and build.
It prevents two common false claims: that a code anchor means the behavior was
tested, and that a test definition means the test passed for this revision.
It also follows decision-relevant outcome hypotheses into representative use
without confusing capability completion with downstream impact.

## Why use this

- Check requirement-to-evidence and artifact-to-requirement coverage.
- Preserve canonical requirement meaning while implementation evolves.
- Distinguish `implemented` from `verified` per acceptance criterion.
- Catch unknown IDs, removed criteria, ambiguous aliases, and stale anchors.
- Classify legitimate non-requirement work without hiding orphaned product work.
- Make operational evidence reproducible through revision and run identity.
- Link hypothesis versions to measurements, classify freshness, and distinguish
  `supported`, `rejected`, `inconclusive`, `unmeasured`, and `stale` outcomes.

## Fundamental principle

Trace links are evidence, not authority. Canonical requirements define what is
needed; implementation and executed checks show how much of that need is covered
and proven now.

Grounding owns outcome-hypothesis meaning. Traceability owns measurement links
and evidence state for the exact hypothesis version. M
(`functionality-complexity-tradeoff`) alone turns current outcome evidence into
a functionality-worth decision.

The skill uses five evidence states:

| State | Meaning |
| --- | --- |
| `unmapped` | No accepted implementation or verification anchor |
| `implemented` | Code/contract anchor or executable test definition exists |
| `verified` | Implementation exists and accepted evidence passed for this revision |
| `blocked` | A named dependency, decision, environment, or evidence owner blocks proof |
| `not-applicable` | A scoped, owner-approved rationale excludes this slice |

Outcome evidence uses a separate state model:

| State | Meaning |
| --- | --- |
| `unmeasured` | No accepted representative observation exists yet |
| `supported` | Current evidence meets the declared threshold and guardrails for the defined cohort and window |
| `rejected` | Current evidence misses the declared threshold or violates a required guardrail |
| `inconclusive` | Exposure, attribution, power, quality, or guardrail gaps prevent a decision |
| `stale` | A freshness rule or material change invalidated the earlier assessment |

Acceptance, deployment, adoption, and telemetry presence are not outcome proof.
An evidence record preserves the hypothesis version, cohort and exposure,
measurement window, baseline, observed result, threshold evaluation, guardrails,
attribution limits, freshness, confidence, owner, and revisit trigger.
When Grounding records an authoritative obligation as `not applicable`, carry
the reason into the trace summary without creating an outcome-evidence record;
completion evidence remains required.

## How to use

Apply it after a passing `implementation-readiness` decision:

> “Trace this implementation slice bidirectionally. Separate implementation
> anchors from executed verification, reject stale IDs, and classify every gap.”

> “Review this change for reverse-trace gaps: which changed artifacts have no
> canonical requirement or accepted platform/operations rationale?”

> “Trace the current measurements for these outcome hypotheses. Preserve their
> thresholds and guardrails, classify freshness, and hand the evidence to M
> without issuing a worth verdict.”

The project's requirements profile supplies repository paths, ID syntax,
evidence stores, commands, and local classifications. The generic skill supplies
the trace method.

## CI enforcement

Use editor validation where possible and a blocking full-repository CI backstop.
Static checks reject unknown requirements, criteria, aliases, and stale
references. Test result ingestion may promote an implemented criterion to
verified only when a matching executable test definition exists and passed.
Operational evidence must include revision, environment, run, and outcome.
Outcome assessments must cite the exact hypothesis version and observation,
window, threshold evaluation, guardrails, and freshness. Static checks can
validate those links and fields; they cannot manufacture causal validity.

Coverage percentages are diagnostic; they do not invent missing requirement
meaning or silently waive intentionally deferred work.

## Output

Every use returns `TRACEABLE`, `PARTIAL`, or `BLOCKED`, along with canonical
source/version, requirement IDs, implemented and verified counts, reverse-trace
gaps, stale references, outcome-hypothesis states and evidence links, owners, the
next action, and checks performed.

## When to skip

Use `requirements-grounding` when meaning or source authority is unresolved,
`requirements-topology` when IDs/lineage/relationships are unstable, and
`implementation-readiness` when no slice has been admitted into build yet.

## Next steps

- Read the operational [`requirements-traceability` SKILL.md](../.claude/skills/requirements-traceability/SKILL.md).
- Repair unstable IDs and graph lineage with [`requirements-topology`](../.claude/skills/requirements-topology/SKILL.md).
- Place deterministic trace checks with [`defect-shift-left`](../.claude/skills/defect-shift-left/SKILL.md).
- Revisit functionality worth with [`functionality-complexity-tradeoff`](../.claude/skills/functionality-complexity-tradeoff/SKILL.md) once current outcome evidence is available.
