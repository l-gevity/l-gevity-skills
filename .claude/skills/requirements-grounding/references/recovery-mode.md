# Requirements Grounding — Recovery Mode

Reference for [SKILL.md](../SKILL.md). Read before recovering requirements
from an existing project; grounding a new request needs only SKILL.md.

## Recovery Mode

Use recovery mode when requirements are missing, stale, incomplete, or detached
from the implementation. Recover candidates from multiple evidence classes; do
not translate files or symbols directly into requirements.

Inspect in this order, stopping when the evidence is sufficient for the requested
scope:

1. Read project instructions, existing specifications, ADRs, domain glossaries,
   and public documentation for stated intent.
2. Inventory externally observable surfaces: APIs, routes, commands, events,
   imports/exports, UI workflows, reports, and integration contracts.
3. Inspect executable contracts: acceptance and integration tests, schemas,
   protocol definitions, public types, and database constraints.
4. Inspect enforced behavior: validation, authorization, business rules,
   calculations, state transitions, audit behavior, and error handling.
5. Inspect variability and lifecycle evidence: configuration, feature flags,
   migrations, deprecations, compatibility shims, and version history.
6. Trace representative end-to-end paths across entry point, domain behavior,
   persistence or integration, and observable output. Deepen only where evidence
   conflicts or a high-impact behavior lacks support.

Classify each evidence reference:

| Evidence class | What it supports | What it does not prove |
| --- | --- | --- |
| `documented-intent` | A stated purpose or decision | That implementation still matches or the decision is current |
| `executable-contract` | Behavior asserted by a test, schema, or public contract | The actor's underlying need, business value, or outcome hypothesis |
| `enforced-behavior` | A rule or invariant actively imposed by code or storage | That the behavior is intentional rather than legacy or defect |
| `observed-surface` | A capability exposed through UI, API, CLI, event, report, or integration | Internal rationale or completeness |
| `inferred` | A plausible requirement reconstructed from structure, names, or history | Confirmed intent; keep confidence low without corroboration |

Evidence strength is contextual, not a universal ranking. Prefer multiple
independent references and boundary-level behavior over implementation detail. A
test can preserve a bug; dead code proves no live capability; a disabled flag may
describe an obsolete experiment; history explains an earlier decision but not
necessarily current intent.

Use this recovery record before converting a candidate to the normal requirement
shape:

```text
Recovered candidate: <provisional-readable-slug>
Observed behavior: <what the inspected project does>
Probable actor and outcome: <explicitly mark inference>
Evidence:
- <file:line or artifact reference> — <evidence class>
Recovery status: intended | observed-only | contradicted | obsolete | unknown
Confidence: low | medium | high
Contradictions: <docs/code, test/code, version, flag, or duplicate behavior>
Confirmation needed: <question and decision owner>
```

Default code-only candidates and recovered outcome hypotheses to `PROVISIONAL`
and `unmeasured`, respectively. Promote requirements to `GROUNDED` only
when authoritative project policy explicitly treats the artifact as the
specification, or when the actor, problem, outcome, basis, and completion
conditions are independently confirmed. Keep accidental behavior, defects,
internal mechanisms, and obsolete paths out of the requirement set; record them
as findings instead.
