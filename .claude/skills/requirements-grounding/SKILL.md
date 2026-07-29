---
name: requirements-grounding
description: >-
    Grounds proposed requirements in a real actor-bound problem, explicit scope,
    authoritative sources, evidence, assumptions, priority, and validation
    confidence. Use when defining or sharpening a problem, extracting obligations
    or stakeholder needs, separating facts from interpretations and hypotheses,
    writing solution-free requirement candidates, defining measurable expected
    outcomes without turning them into acceptance criteria, deciding what belongs
    in scope,
    reverse-engineering provisional requirements from existing code, tests,
    schemas, configuration, public interfaces, documentation, or history, or
    determining whether requirements are ready for dependency modeling. Do not use
    for graph construction or implementation planning except to prepare their
    inputs.
---

# Requirements Grounding

Turn raw legal, contractual, commercial, operational, customer, or product input
into requirement candidates that are traceable, solution-free, and honest about
uncertainty.

> **Core Directives**
>
> 1. **Problem before requirement.** Do not derive a solution from an unconfirmed
>    problem statement.
> 2. **Separate authority, evidence, interpretation, and hypothesis.** They imply
>    different confidence and validation work.
> 3. **One actor, one outcome, one decision.** Split material differences instead
>    of hiding them in compound requirements.
> 4. **Observable completion.** Every requirement states how a reviewer can know
>    the capability is complete without prescribing implementation or substituting
>    a downstream impact metric for completion.
> 5. **Domain policy is input, not universal truth.** Honor project-specific
>    terminology, source hierarchies, roles, and classifications without embedding
>    them in this skill.
> 6. **Implementation is evidence, not intent.** Code proves what can happen in
>    the inspected version; it does not by itself prove what should happen, why it
>    exists, or whether it remains wanted.
> 7. **Compose; do not fork.** Generic method stays in this skill. A project
>    profile owns repository paths, source policy, schemas, taxonomies, roles,
>    commands, and other domain conventions.
> 8. **Completion is not impact.** Passing a requirement's completion conditions
>    proves the capability works as specified; it does not prove the capability
>    changed the actor's or organization's outcome.

## Boundary

Use this skill for problem framing, scope, sources, actors, requirement wording,
priority, evidence, assumptions, validation confidence, and linked outcome
hypotheses when expected downstream impact is decision-relevant.

Use `requirements-topology` after grounding when stable IDs, typed relationships,
dependency order, duplicate/conflict checks, or a graph package are needed. Use
`implementation-readiness` after topology when developers and architects need a
build-preparation package.

When a project provides a requirements profile or overlay, apply it alongside
this skill. Do not copy generic workflow into the profile and do not move project
facts into this skill.

Do not introduce graph edges, domain entities, APIs, services, ADRs, or
implementation slices here. Record them only as questions for later stages.

## Operating Modes

Choose the lightest mode that preserves the decisions at risk:

- **Conversational**: lead with the problem, scope, and a compact candidate table.
- **Batch**: process an existing source set while keeping ambiguity and confidence
  visible; do not invent confirmation.
- **Interactive deepening**: confirm one decisive item or one requirement at a
  time when mistakes are costly or difficult to reverse.
- **Recovery**: inspect an existing codebase or project to produce provisional,
  evidence-linked requirement candidates and a confirmation queue.
- **Standalone artifact**: save a durable document with source context, decision
  log, completion date, and unresolved watch items.

## Source Discipline

Before relying on a project-specific source:

1. Identify its authority: law, regulation, contract, standard, policy, approved
   decision, user evidence, operational evidence, or hypothesis.
2. Check applicability, version, date, and status when the source is volatile or
   normative.
3. Preserve source wording and provenance; interpret it separately.
4. Surface conflicting sources or interpretations instead of silently choosing.
5. Read project instructions, domain glossaries, role catalogs, and policy files
   when present. Treat them as the domain overlay for this run.
6. Identify the canonical editable requirement source and distinguish it from
   generated registers, diagrams, code constants, reports, and implementation
   evidence. Never author meaning in a derived view.

If source currency cannot be verified, mark the affected requirements provisional.
Do not imply legal, compliance, security, or contractual certainty that the source
set does not support.

If the canonical source or project profile is missing or contradictory, name the
ownership gap instead of choosing the most polished artifact.

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

## Workflow

1. **Orient**: inventory the input, source classes, existing decisions, and domain
   overlay.
2. **Frame the problem**: state actor, situation, desired outcome, and current
   obstacle without naming a feature or technical design.
3. **Confirm decisive assumptions**: confirm the problem, done state, and
   not-problem boundary before deriving a large requirement set. Also confirm
   source versions, actor splits, or high-impact hypotheses when they materially
   change the result. Do not re-ask what the user has already established.
4. **Explore adjacent scope**: inspect before/after workflows, other actors,
   adjacent obligations, variants, reused data, and paid or operational layers.
   Place each item in this scope, another scope, or outside scope.
5. **Choose the boundary**: classify the subject as a problem scope or a shared
   foundation capability. Split when owner, lifecycle, outcome, or test surface
   materially differs. Do not call a requirements scope a module unless the
   project explicitly uses that domain term.
6. **Identify actors**: name the actor served by each requirement. Split role
   differences that change the need or completion conditions.
7. **Draft atomic candidates**: assign readable slug IDs and write one outcome per
   requirement.
8. **Describe completion**: add actor, capability, purpose when useful, and two to
   four observable complete-when conditions.
9. **State outcome hypotheses when relevant**: link a measurable downstream
   impact hypothesis to the affected requirements without turning it into a
   completion condition. For authoritative obligations whose validity does not
   depend on product-value evidence, record `not applicable` plus the reason
   instead of creating a hypothesis record.
10. **Classify independently**: assign basis, priority, validation decision, and
   confidence without letting one label imply another.
11. **Record decisions**: capture source, assumption, owner, date, watch item, and
    revisit trigger for every consequential choice.

## Problem Check

A grounded problem is:

- **solution-free** — describes a need or obligation, not a screen, service, or
  algorithm;
- **actor-bound** — identifies who experiences the problem;
- **situation-bound** — identifies the trigger or context;
- **outcome-bound** — states the result that must become possible;
- **obstacle-bound** — states why that result is not already achievable;
- **singular** — contains no hidden second problem;
- **role-consistent** — materially different actors are split;
- **bounded** — includes both done-when and not-problem statements.

## Requirement Shape

Give each requirement a stable, readable, kebab-case slug of one to four words.
Prefer `report-approval` over `R7` or `validation`. Reuse the slug downstream.
Mint a new slug only when a requirement genuinely splits or merges, and record the
transformation.

Use this shape:

```text
Requirement: <readable-slug>
Actor: <one actor>
Must be able to: <one solution-free capability or outcome>
So that: <purpose, when it adds information>
Complete when:
- <observable condition>
- <observable condition>
Basis: authoritative | interpreted | evidenced | hypothesized
Source or evidence: <reference>
Evidence class: <recovery mode only>
Recovery status: <recovery mode only>
Priority: must | should | could | won't-now
Validation decision: accept | test | watch | reject
Confidence: low | medium | high
```

If a project defines its own basis or priority taxonomy, use it and include a
legend. Never silently translate away a domain distinction.

`So that` records purpose. It is neither evidence that the outcome will occur nor
a substitute for a testable outcome hypothesis.

## Outcome Hypothesis Shape

Keep three artifacts distinct:

| Artifact | Question answered | Evidence that closes it |
| --- | --- | --- |
| Problem outcome | What must become possible for the actor? | Problem and source validation |
| Requirement completion | Does the capability work as specified? | Complete-when verification |
| Outcome hypothesis | Did use of the capability produce the expected downstream impact? | Outcome measurement after representative use |

Create an outcome hypothesis when an expected customer, product, commercial, or
operational impact could change the decision to build, retain, simplify, expand,
or stop the capability. Link it to one or more requirement slugs; do not embed it
inside each requirement.

Use this shape:

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

Do not invent a baseline or target. Record `unknown` plus the measurement needed.
At creation, set `Evidence state` to `unmeasured`. Later states and references are
projections from `requirements-traceability`, not edits to hypothesis meaning.
For an applicable law, contract, policy, or safety obligation, record outcome
hypotheses as `not applicable` rather than creating a hypothesis record; lack of a
product-value experiment must not delay the obligation. Completion evidence does
not support an outcome hypothesis, and a supported hypothesis does not prove
implementation completeness.

After representative use, use `requirements-traceability` to link measurements,
assess evidence state and freshness for the exact hypothesis version, and feed
current evidence to `functionality-complexity-tradeoff`. M alone owns BUILD,
DEFER, DROP, KEEP, SIMPLIFY, and removal decisions; grounding records hypothesis
meaning without issuing that worth verdict.

## Validation Gate

Gate strictness equals the cost of being wrong multiplied by the difficulty of
reversal.

| Basis | Validate | Safe movement before certainty | Hedge |
| --- | --- | --- | --- |
| Authoritative | Correct source, applicability, and reading | Proceed when applicable | Preserve source/version and watch changes |
| Interpreted | Defensibility and competing readings | Proceed only when reversible | Make the decision explicit and revisitable |
| Evidenced | Strength, reach, and recency of evidence | Prefer the smallest useful commitment | Measure the outcome |
| Hypothesized | Whether the need occurs at all | Test before material commitment | Define the smallest experiment and trigger |

Validate authoritative requirements against their controlling source. Validate
empirical outcome hypotheses against their measure, threshold, window, guardrails,
and evidence plan. Do not force an authoritative obligation to pass an empirical
value test.

A must-have with weak basis or evidence is a risk finding, not a reason to hide
the uncertainty. Strengthen the source, reduce the commitment, or define a
reversible test.

This gate decides whether a requirement is grounded enough to move forward. It
does not decide whether proposed functionality earns its complexity. Use
`functionality-complexity-tradeoff` for BUILD / DEFER / DROP decisions and consume
its verdict rather than recreating its value and cost ledger here.

## Output Contract

Every application emits a decision record before any longer artifact:

```text
Subject:        <problem scope or requirement set>
Mode:           conversational | batch | interactive | recovery | standalone
Decision:       GROUNDED | PROVISIONAL | NOT-GROUNDED
Problem:        <confirmed or explicitly inferred actor / situation / outcome / obstacle>
Basis profile:  <authoritative / interpreted / evidenced / hypothesized mix>
Confidence:     low | medium | high
Blocking gaps:  <missing source, confirmation, evidence, actor, or completion>
Outcome hypotheses: <linked IDs + decisions, or not applicable + reason>
Next action:    <confirm, source, split, test, reject, or run requirements-topology>
Verification:   <sources and decisions checked, or Not run + reason>
Revisit when:   <required for PROVISIONAL; measurable trigger or date>
```

Return only the additional weight needed for the current decision. A complete
grounding artifact contains:

```text
Requirements grounding:
- Meta-context:              # standalone artifacts only
- Problem statement:
- Done when:
- Not-problem:
- Scope placements:
- Actors and role splits:
- Requirement candidates:   # readable slug IDs + requirement shape
- Outcome hypotheses:       # linked records or not applicable + reason
- Implementation evidence map: # recovery mode only
- Contradictions and obsolete behavior: # recovery mode only
- Confirmation queue:       # recovery mode only
- Basis and priority legend:
- Validation decisions:
- Assumptions and experiments:
- Input and decision log:
- Watch items and revisit triggers:
- Topology handoff note:
```

For a standalone file, include audience, purpose, completion date, source files,
source currency, and caveats once near the top. For a conversational answer, put
the problem statement first and omit ceremony that no reader needs.

If downstream topology or readiness artifacts already exist and grounding changes
materially, either update them when they are in scope or name exactly what is now
stale. Never leave silent divergence.

## Guardrails

- Do not convert stakeholder requests directly into implementation commitments.
- Do not convert code structure, class names, database tables, or tests directly
  into intended requirements.
- Do not promote observed behavior above `PROVISIONAL` without the confirmation
  or authoritative artifact required by recovery mode.
- Do not turn defects, dead paths, disabled experiments, or compatibility shims
  into requirements merely because they exist.
- Do not make an authoritative source say more than it says.
- Do not use priority as a proxy for certainty or source authority.
- Do not place outcome hypotheses inside requirement completion conditions.
- Do not mark an outcome hypothesis `supported` from acceptance, integration, or
  implementation evidence alone.
- Do not invent baselines, thresholds, or causal claims to make a hypothesis look
  complete.
- Do not delay an authoritative obligation merely because its product-value
  outcome hypothesis is absent or untested.
- Do not bury unresolved decisions inside polished requirement prose.
- Do not create broken links to prerequisites; name missing artifacts explicitly.
- Do not optimize this output for developers at the expense of product, domain,
  legal, compliance, or stakeholder readability.
