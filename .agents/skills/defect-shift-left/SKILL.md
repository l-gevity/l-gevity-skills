---
name: defect-shift-left
description: >-
    Places every error detection at the earliest stage of the pipeline that is
    technically capable of catching it. Use when designing or auditing a CI/CD
    pipeline, choosing tooling, deciding where a check belongs, or asking "could
    this have been caught earlier?"
---

# Defect Shift-Left

> Pipeline stages have a strict order. Every defect has an earliest stage at
> which it can be caught. Catching it later is always a regression.

> **Core Directives**
>
> 1. **Prevent over detect.** Make invalid states unrepresentable before adding
>    a check.
> 2. **Earliest possible stage is mandatory.** If a check _can_ run at stage N,
>    running it at N+1 is a regression.
> 3. **Replace same-scope duplicates.** When shifting a check earlier, remove
>    any later check that covers the same scope. Keep a later backstop only
>    when it covers a broader or less-bypassable scope.
> 4. **Fail loud at the origin.** Errors must surface where they originated.

> **Improvement Trio**
>
> - `defect-shift-left`: move defect detection earlier.
> - `push-out`: move recurring operational work outward.
> - `bring-down`: move bespoke code down into reusable capability.

---

## 1. The Ladder

| Stage  | Rank | Phase                   | What runs here                                                            |
| ------ | ---- | ----------------------- | ------------------------------------------------------------------------- |
| **0**  | 0    | Language                | Type system, syntax, language semantics                                   |
| **1**  | 1    | Design                  | Spec, ADR, threat model, schema                                           |
| **2**  | 2    | Authoring               | LSP, in-editor lint, formatter                                            |
| **3**  | 3    | Pre-commit              | Format, fast lint, secret scan, commit-msg hook                           |
| **4**  | 4    | Compile                 | Compiler, type-checker, codegen                                           |
| **5**  | 5    | Build / Static analysis | Full lint, depcheck, SAST, license, CVE, bundle, IaC, fitness functions   |
| **6**  | 6    | Unit test               | Local test runner, property tests                                         |
| **7**  | 7    | Integration / Contract  | CI suite, contract tests, container builds                                |
| **8a** | 8    | Pre-deploy static       | Migration dry-run, config-vs-env, capacity, IAM diff _(deploy abortable)_ |
| **8b** | 9    | Deploy execution        | Smoke, health probes, slot readiness _(rollback on failure)_              |
| **9**  | 10   | Canary / Staging        | Partial traffic, real env, perf regression                                |
| **10** | 11   | Production runtime      | Live traffic, monitoring                                                  |
| **11** | 12   | Post-incident           | Forensics, RCA                                                            |

Cost grows roughly geometrically with rank. The ladder is monotonic — later
detection is never neutral. Use `Rank` for distance math; stage labels like
`8a` and `8b` are names, not numbers.

Stages **8a** and **8b** are split because some defects only become detectable
when target-environment state is available; pre-deploy can abort cheaply, deploy
execution requires rollback.

---

## 2. Stage 0 — Make Invalid States Unrepresentable

Before adding any check at Stage ≥1, ask: _can a type or schema make this defect
unrepresentable?_ If yes, the check belongs at Stage 0.

| Technique                                                                                    | Eliminates                                                                                     |
| -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Strong / branded types                                                                       | Type confusion, semantic mixing                                                                |
| Sum types + exhaustive matching                                                              | Missing case, silent fallthrough                                                               |
| Option / Result types                                                                        | Null deref, silent failure                                                                     |
| Refinement types                                                                             | Range, off-by-one                                                                              |
| Linear / affine types                                                                        | Use-after-free, double-close                                                                   |
| Schema-as-code                                                                               | Config drift, contract mismatch                                                                |
| Const / immutable default                                                                    | Accidental mutation, race                                                                      |
| Strict compiler flags (`strict`, `noUncheckedIndexedAccess`, `strictNullChecks`, `--strict`) | Whole defect classes without writing new types — flip a flag, the compiler enumerates the gaps |

---

## 3. Defect Taxonomy → Earliest Stage

> **Stage vs rank.** The `Stage` column is the label from §1; for distance
> math use the **rank**. Labels `0`–`7` equal their rank, then `8a`→8, `8b`→9,
> `9`→10, `10`→11, `11`→12 — never subtract stage labels.

| Defect class                                    | Stage | Mechanism (fallback)                             |
| ----------------------------------------------- | ----- | ------------------------------------------------ |
| Type mismatch, null deref, semantic-type mixing | 0     | Type system                                      |
| Missing case handling                           | 0     | Exhaustive sum types                             |
| Off-by-one / range                              | 0     | Refinement types (else 6: property test)         |
| Use-after-free, race                            | 0     | Linear / borrow types (else 5: static analysis)  |
| Generated code drift from schema                | 0     | Codegen types (else 5: codegen drift check)      |
| Contract / schema absent or ambiguous           | 1     | Shared schema / spec                             |
| Authorization model gap                         | 1     | Threat model (else 7: security test)             |
| Style, formatting, unused code, API misuse      | 2     | LSP / editor (else 5: lint)                      |
| Banned API / unsafe pattern                     | 2     | LSP rule (else 5: lint)                          |
| Forbidden architectural dependency              | 2     | Editor import rule (else 5: depcheck / lint)     |
| Aspect coverage gap — a governed subsystem lacks the aspect's mechanism | 5 | Fitness function over the subsystem registry (else 7: policy test) |
| Committed config violates schema                | 2     | Editor schema hint (else 5: schema validation)   |
| Secret in source                                | 3     | Pre-commit scanner (else 5: SAST)                |
| Symbol resolution / missing import              | 4     | Compiler                                         |
| CVE in dependency                               | 5     | SCA audit                                        |
| License incompatibility                         | 5     | License audit                                    |
| Bundle / artifact regression                    | 5     | Bundle validator                                 |
| Logic error in pure function                    | 6     | Unit test                                        |
| Property violation across input space           | 6     | Property test                                    |
| Integration boundary mismatch                   | 7     | Contract test                                    |
| Container / build reproducibility               | 7     | CI image build                                   |
| Performance regression (micro)                  | 7     | Benchmark (else 9: load test)                    |
| Migration vs current schema                     | 8a    | Dry-run against prod DB                          |
| Irreversible migration                          | 8a    | Reversibility check                              |
| Cross-service version skew                      | 8a    | Version-matrix gate                              |
| Backwards-incompatible API change               | 8a    | Contract diff vs deployed                        |
| Missing / expired secret in target env          | 8a    | Secret-store presence check                      |
| Undefined feature flag in target                | 8a    | Flag-store consistency                           |
| Target-env config violates schema               | 8a    | Pre-deploy config / env validation               |
| Capacity / quota exceeded                       | 8a    | Resource projection                              |
| IAM permission expansion                        | 8a    | IAM diff                                         |
| Cost / budget breach                            | 8a    | Cost projection                                  |
| Missing rollback artifact                       | 8a    | Registry probe                                   |
| Compliance approval missing                     | 8a    | Policy gate                                      |
| Artifact crashes on boot                        | 8b    | Startup smoke                                    |
| Health probe never passes                       | 8b    | Orchestrator readiness gate                      |
| Target env unreachable dependency               | 8b    | Boot connectivity check                          |
| Resource exhaustion under load                  | 9     | Load test                                        |
| Real-world latency / SLO breach                 | 10    | Production monitoring                            |

---

## 4. Audit Protocol

1. **Inventory** every check and the stage it runs at, including manual reviews,
   advisory warnings, and runtime asserts.
2. **Classify** each by defect class (§3).
3. **Look up** the earliest possible stage and its rank (§1).
4. **Compute rank distance** = current rank − earliest rank.
5. **Prioritize** by rank distance × frequency × blast radius.
6. **Move the check** to the earliest feasible stage.
7. **Gate it.** A correct-stage check that does not block is still a detection
   gap.
8. **Remove later same-scope duplicates** once the earlier gate is proven. Keep
   only broader or less-bypassable backstops.
9. **Audit every escaped defect:** find its earliest possible stage and place a
   gate there.

| Situation                                      | Action                                         |
| ---------------------------------------------- | ---------------------------------------------- |
| Proposed = earliest possible                   | Proceed                                        |
| Proposed > earliest, earlier feasible now      | Reject — implement at the earlier stage        |
| Proposed > earliest, earlier requires effort   | Document gap as technical debt; schedule shift |
| No check; defects only found in production     | Critical — work backward from Stage 10         |
| Check requires target-env state                | Stage 8a is earliest — do not push to Stage 10 |
| Check exists but does not block                | Promote to blocking gate or remove as theatre  |
| Later check covers same scope as earlier check | Remove later duplicate after proof             |
| Later check covers broader / unbypassable scope | Keep as backstop; record distinct scope        |

Emit one coder-facing row per gap:

| Defect class | Current stage (rank) | Earliest stage (rank) | Rank distance | Mechanism | Decision | Owner/check | Verification | Next action |
| ------------ | ------------- | -------------- | -------------- | --------- | -------- | ----------- | ------------ | ----------- |

If a gap remains, state: _"Detection Gap: defect class catchable at Stage [X] (rank [Xr]),
currently at Stage [Y] (rank [Yr]). Mechanism: [...]."_

---

## 5. Anti-Patterns

| Pattern                                    | Actual / earliest             |
| ------------------------------------------ | ----------------------------- |
| Runtime check for type errors              | Stage 10 / Stage 0            |
| CI formatting check with no editor support | Stage 5 / Stage 2             |
| Linter only in CI                          | Stage 5 / Stage 2 + Stage 5   |
| Code review as primary defect filter       | Manual / Stage 2–5            |
| Production monitor for known-bad input     | Stage 10 / Stage 0            |
| Compile errors hidden behind dynamic types | Stage 6+ / Stage 0            |
| Manual deployment checklist                | Manual / Stage 5 or 8a        |
| Documentation as the contract              | Stage 7+ / Stage 1            |
| Deploy-and-pray monitoring                 | Stage 10 / Stage 8a           |
| Migration applied without dry-run          | Stage 8b–10 / Stage 8a        |
| Secrets / config validated only at runtime | Stage 10 / Stage 8a           |
| Manual rollback on deploy failure          | Stage 10 / Stage 8b           |
| No canary, full traffic on new artifact    | Stage 10 / Stage 9            |

These three do not detect late — they **suppress** a defect rather than move it
earlier, so they have no "earliest stage":

- **Retry as error handling** — masks a Stage 10 failure indefinitely instead of surfacing it.
- **Catch-and-log silent failure** — swallows the error, violating "fail loud at the origin" (Directive 4).
- **Warnings nobody reads** — detection with no gate; see §6.4.

---

## 6. Common Shift Patterns

Recurring moves that shift a defect class from a later stage to an earlier
one; recognise them and apply them deliberately. Read
[references/shift-patterns.md](references/shift-patterns.md) for the recipe,
tooling, and completion condition of each.

- **6.1 Untyped → strict-typed source** — type errors and null derefs from
  Stage 6+ to Stage 0; complete only when the strict typecheck blocks at
  pre-commit and in CI.
- **6.2 ADR → executable architectural rule** — prose rules become lint
  config at Stages 2 and 5; the encoding pattern is `architecture-as-code`.
- **6.3 Hand-validated boundary → schema-as-code** — one schema artifact
  fanned out to the codegen, editor, build, and pre-deploy rungs.
- **6.4 Optional check → blocking gate** — the most common shift-left failure
  is the right check at the right stage that does not block; a check nobody
  runs has zero shift-left value.
- **6.5 Scope-justified backstops** — a later duplicate stays only when it is
  broader or less bypassable than the earlier, faster layer (Directive 3).
- **6.6 Hand-checked aspect coverage → fitness function** — a coverage gap
  moves from review to Stage 5; the subsystem registry is the population and
  the `test-strategy` oracle is the assertion.

---

## 7. Stack-Aware Tooling Survey

Use this only when the user asks for tooling recommendations or implementation
options; a plain shift-left audit stops at the missing category. Detect the
stack, map each gap to a stage, defect class, and tool category, and name
specific products only on request, each cited with a source and a currency
signal. Read [references/tooling-survey.md](references/tooling-survey.md) for
the stage-to-category table and the output row. A tool that does not map to a
rung on the ladder has no place in the output.

## 8. See also

- **`architecture-as-code`** — the codified-architecture pattern this skill names in §6.2.
- **`architecture-guidelines`** — first-principles rules whose violations this skill places on the ladder.
- **`ci-cd-reliability-architecture`** — pipeline rules that staff Stages 5–10.
- **`push-out`** — move recurring operational work out of human/manual execution into durable systems.
- **`bring-down`** — move bespoke or duplicated code down into reusable capability.
- **`continuous-improvement`** — how to promote a recurring escaped-defect into a permanent gate (Directive 1).
