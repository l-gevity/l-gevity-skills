# Defect Shift-Left

A pipeline-design SKILL that places every defect-detection check at the earliest stage it can technically run. The cost of catching a defect grows geometrically with stage; catching it later is always a regression.

## Why use this

- **Defects are caught at the earliest stage they technically can be.** Cost of detection grows geometrically with stage; earlier is always cheaper.
- **Late detection is recognized as a regression.** "We caught it in production" stops sounding like a win.
- **Existing pipelines can be audited.** Each escaped defect points to the stage it *should* have been caught at — and isn't.
- **New checks know where they belong.** No more debating whether a rule is a lint, a unit test, or a CI gate.
- **The pipeline becomes self-documenting.** Each stage has a defined responsibility — you can see what catches what.

## Fundamental principles

Pipeline stages have a strict order. Cost grows roughly geometrically with stage — a typecheck error costs a keystroke; a production incident costs sleep, customer trust, and engineering hours.

- **Prevent over detect.** A type or schema that makes a defect *unrepresentable* beats any check that *catches* it.
- **Earliest possible stage is mandatory.** If a check can run at stage N, running it at N+1 is a regression — full stop.
- **Replace, don't layer.** When you shift a check earlier, remove the later one. (Exception: a fast, bypassable check plus an un-bypassable backstop — different scopes warrant both.)
- **Fail loud at the origin.** Errors must surface where they originated, not three layers downstream where the cause is invisible.

The ladder is monotonic — later detection is never neutral, only worse.

## How to use

The skill has two modes: **audit** an existing pipeline, or **design** a new check.

1. **Identify the defect class or escaped bug.** A production incident, a lint rule you're considering, a check that lives at the wrong stage.
2. **Prompt the AI.**

   > *Audit:* "Audit our pipeline for shift-left opportunities. We run typecheck in CI, unit tests in CI, and have no pre-commit hooks."
   >
   > *Design:* "Where should a check for missing IAM permissions before deploy go?"

3. **Read the verdict.** The skill names the earliest possible stage and the mechanism — type system, schema, lint, dry-run, etc. For audits, it reports Δstage (current minus earliest possible).
4. **Move the check.** Implement at the earliest stage; remove the later one once the earlier one is proven.

## The ladder

| Stage   | Phase                            | Cost if a defect escapes here       |
|---------|----------------------------------|-------------------------------------|
| **0**   | Language (types, compiler)       | Keystrokes                          |
| **1–3** | Design, authoring, pre-commit    | Minutes                             |
| **4–5** | Compile, build, static analysis  | Minutes to hours                    |
| **6–7** | Unit, integration, contract test | Hours                               |
| **8**   | Pre-deploy & deploy execution    | Hours; may require rollback         |
| **9**   | Canary / staging                 | Hours; partial blast radius         |
| **10**  | Production runtime               | Customers affected; on-call pages   |
| **11**  | Post-incident                    | Trust, retrospectives, RCAs         |

The cost ratio between Stage 0 and Stage 10 routinely exceeds 1000×. "Earliest possible stage" is not stylistic — it is economic.

## Common shifts

Recurring high-leverage moves. Recognize them; apply them deliberately.

- **Untyped → typed source.** Convert dynamic source to a typed language with strict flags. "Value may be undefined" defects move from production (Stage 10) or unit tests (Stage 6) to the compiler (Stage 0).
- **ADR → executable architectural rule.** Turn prose architectural decisions into lint config. "We agreed not to import services from components" becomes a build failure instead of code-review folklore.
- **Hand-validated → schema-as-code.** A single schema (JSON Schema, OpenAPI, Protobuf, Zod) drives codegen, editor autocomplete, build-time validation, and pre-deploy gates from one source. The highest-leverage shift in the catalogue.
- **Optional → blocking gate.** The most common shift-left failure is having the right check at the right stage and not making it block. A typecheck nobody runs is theatre.

## When to skip

Greenfield exploration, throwaway scripts, scratch repos. The framework earns its keep when the pipeline is non-trivial, when defects have escaped to late stages, or when a new check needs a home.

## Next steps

- See [SKILL.md](./SKILL.md) for the operational reference (full 12-stage ladder, defect taxonomy → earliest stage table, decision protocol, anti-patterns, stack-aware tooling survey).
- For executable architectural rules (the "ADR → rule" shift in practice), see [`architecture-as-code-javascript`](../architecture-as-code-javascript/).
- Run an audit on your last three production incidents — each escaped defect names the stage it should have been caught at.
