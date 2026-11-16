# Requirements Grounding — Outcome Hypothesis

Reference for [SKILL.md](../SKILL.md). Read before writing an outcome
hypothesis; when to create one, and what it may not invent, stay in the skill.

## Three Artifacts

Keep three artifacts distinct:

| Artifact | Question answered | Evidence that closes it |
| --- | --- | --- |
| Problem outcome | What must become possible for the actor? | Problem and source validation |
| Requirement completion | Does the capability work as specified? | Complete-when verification |
| Outcome hypothesis | Did use of the capability produce the expected downstream impact? | Outcome measurement after representative use |

Completion evidence does not support an outcome hypothesis, and a supported
hypothesis does not prove implementation completeness.

## Record Shape

```text
Outcome hypothesis: <readable-slug>
Applies to requirements: <one or more requirement slugs>
Actor or cohort: <who is expected to experience the impact>
If: <capability is used in the relevant situation>
Then: <measurable downstream change expected>
Because: <causal rationale>
Primary measure: <metric and direction>
Baseline: <known value, unknown, or evidence reference>
Decision threshold: <target or minimum meaningful change>
Evaluation window: <when and for how long to assess>
Guardrails: <measures that must not materially worsen>
Evidence plan: <instrumentation, comparison, or study>
Hypothesis confidence: low | medium | high
Evidence state: unmeasured | supported | rejected | inconclusive | stale
Evidence reference: <requirements-traceability record or none>
Owner: <decision owner>
Revisit when: <event, evidence threshold, or date>
```
