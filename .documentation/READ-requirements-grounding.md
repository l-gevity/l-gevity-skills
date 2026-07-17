# Requirements Grounding

Requirements fail early when they are detached from the problem, actor, source,
or evidence that justifies them. Requirements Grounding forces those foundations
to become explicit before a backlog or specification hardens around an assumed
solution. It can also recover provisional requirements from an existing project
without confusing as-built behavior with intended behavior.

## Why use this

- Separate authoritative obligations from interpretations, evidence, and
  hypotheses.
- Frame one actor-bound, situation-bound problem before deriving requirements.
- Keep adjacent ideas visible without silently expanding scope.
- Give every requirement a readable stable ID and observable completion
  conditions.
- Make weak evidence and expensive-to-reverse assumptions visible before build
  planning.
- Recover evidence-linked candidates from code, tests, schemas, configuration,
  public interfaces, documentation, and history.

## Fundamental principle

A requirement is grounded only when another reader can answer:

1. Who needs or is obliged to achieve the outcome?
2. In what situation?
3. What outcome must become possible?
4. What prevents it today?
5. Which source, evidence, interpretation, or hypothesis supports it?
6. How will we know it is complete?

Priority does not answer those questions. A must-have can still be weakly
grounded, and that mismatch is itself a risk finding.

## How to use

Ask the agent to frame or review requirements before graphing or implementation:

> “Ground these stakeholder requests. Separate the real problem, adjacent scope,
> evidence, assumptions, and requirement candidates.”

> “Review this specification for solution-shaped problems, compound requirements,
> actor ambiguity, and missing complete-when conditions.”

Choose conversational mode for exploration, batch mode for an existing source
set, and interactive deepening when the cost of a wrong assumption is high.

For an undocumented or drifted project, use recovery mode:

> “Reverse-engineer provisional requirement candidates from this project. Treat
> implementation as evidence, not authoritative intent. Cite file and line
> evidence, classify each reference, surface contradictions and obsolete
> behavior, and list the confirmations needed before grounding.”

## Recovery evidence

Recovery mode distinguishes documented intent, executable contracts, enforced
behavior, observed public surfaces, and uncorroborated inference. It inspects
public boundaries and representative end-to-end paths before internal structure.
Code-only candidates remain `PROVISIONAL` unless project policy makes an artifact
authoritative or the actor, problem, outcome, basis, and completion conditions are
independently confirmed.

Dead code, defects, disabled experiments, and compatibility shims become findings,
not requirements. Documentation/code and test/code disagreements remain explicit
contradictions for a decision owner.

## Basis model

The default model distinguishes four kinds of grounding:

| Basis | Meaning |
| --- | --- |
| Authoritative | An applicable law, contract, standard, policy, or accepted decision requires it |
| Interpreted | It follows from a defensible reading that still admits alternatives |
| Evidenced | User, customer, operational, or market evidence supports it |
| Hypothesized | The need or value remains to be tested |

Projects may supply a different taxonomy. The skill preserves project policy
instead of pretending one domain's categories are universal.

## Project profiles and canonical source

Compose generic grounding with a project profile instead of forking the method.
The profile owns source hierarchy, repository paths, schemas, roles, taxonomies,
commands, and domain conventions. Grounding owns the reusable problem, evidence,
and validation method.

Before authoring, identify the canonical editable source and distinguish it from
generated registers, diagrams, code constants, reports, and implementation
evidence. Derived views may expose drift but never become a second authority.

## Output

The core result is a confirmed problem boundary plus atomic requirement candidates
with readable slugs, actors, complete-when conditions, basis, priority, validation
decision, confidence, and traceability. Standalone artifacts also carry source
currency, a decision log, and watch items. Every use starts with a compact
`GROUNDED`, `PROVISIONAL`, or `NOT-GROUNDED` decision record naming blockers,
the next action, and verification performed. Recovery output additionally includes
an implementation evidence map, contradictions, obsolete-behavior findings, and a
confirmation queue.

This validation decision is not a feature-worth verdict. Use
`functionality-complexity-tradeoff` when deciding whether functionality should be
built, minimized, deferred, or dropped.

## When to skip

Skip when requirements are already grounded and the task is only dependency
modeling; use `requirements-topology`. Skip when a stable topology already exists
and the task is implementation preparation; use `implementation-readiness`.

## Next steps

- Read the operational [`requirements-grounding` SKILL.md](../.claude/skills/requirements-grounding/SKILL.md).
- Structure validated requirements with [`requirements-topology`](../.claude/skills/requirements-topology/SKILL.md).
- Trace post-readiness implementation and executed evidence with [`requirements-traceability`](../.claude/skills/requirements-traceability/SKILL.md).
- Apply [`functionality-complexity-tradeoff`](../.claude/skills/functionality-complexity-tradeoff/SKILL.md) when a proposed capability still needs a worth decision.
