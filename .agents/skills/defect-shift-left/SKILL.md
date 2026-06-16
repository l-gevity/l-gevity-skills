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
4. **Compute stage distance** = current rank − earliest rank.
5. **Prioritize** by stage distance × frequency × blast radius.
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

| Defect class | Current stage | Earliest stage | Stage distance | Mechanism | Decision | Owner/check | Verification | Next action |
| ------------ | ------------- | -------------- | -------------- | --------- | -------- | ----------- | ------------ | ----------- |

If a gap remains, state: _"Detection Gap: defect class catchable at Stage [X],
currently at Stage [Y]. Mechanism: [...]."_

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
| No canary, full traffic on new artifact    | Stage 10 carries full blast radius |
| Retry as error handling                    | Hides Stage 10 indefinitely   |
| Catch-and-log silent failure               | Propagates past origin        |
| Warnings nobody reads                      | Detection without action      |

---

## 6. Common Shift Patterns

Recurring moves that shift a defect class from a later stage to an earlier one.
Recognise them; apply them deliberately.

### 6.1 Untyped → strict-typed source

|            |                                                                                       |
| ---------- | ------------------------------------------------------------------------------------- |
| **Shifts** | Type errors, null deref, registry-shape drift, silent `undefined` from bracket access |
| **From**   | Stage 6+ (unit test) or Stage 10 (production)                                         |
| **To**     | Stage 0 (type system)                                                                 |

Convert source to a language with a checking compiler (JS → TS, Python → typed
Python under `mypy`/`pyright`, Ruby → RBS/Sorbet). Then progressively enable the
strictest flags — `strict`, `noUncheckedIndexedAccess`, `strictNullChecks` — and
retire every `@ts-nocheck` / `# type: ignore` escape hatch. Each flag flip is
its own shift: the compiler enumerates the defects, you fix them in batches.

The shift completes only when the strict typecheck is a **blocking gate** at
both pre-commit (fast feedback on staged files) and CI (full-repo backstop). A
typecheck nobody runs is theatre — see §6.4.

### 6.2 ADR → executable architectural rule

|            |                                                                                            |
| ---------- | ------------------------------------------------------------------------------------------ |
| **Shifts** | Forbidden imports, layering violations, banned API usage, accidental cross-module coupling |
| **From**   | Stage 1 (design doc) or Stage 7+ (code review)                                             |
| **To**     | Stage 2 (editor rule) + Stage 5 (blocking static analysis)                                 |

Architectural rules expressed in prose are advice; rules expressed in lint
config are enforcement. `eslint-plugin-boundaries`,
`import/no-restricted-paths`, `dependency-cruiser`, ArchUnit (JVM), Pyright
import rules — all turn an ADR sentence into editor feedback and a build
failure.

The recipe: encode each architectural decision as a rule that fails the build
when violated. The ADR document remains as rationale; the lint config is the
enforcement.

For the encoding pattern see `architecture-as-code`, with concrete
implementations in `architecture-as-code-javascript` or
`architecture-as-code-python`. For first principles see
`architecture-guidelines`; for the spatial rationale this enforces, see
`geometric-architecture`.

### 6.3 Hand-validated boundary → schema-as-code

|            |                                                                                                            |
| ---------- | ---------------------------------------------------------------------------------------------------------- |
| **Shifts** | Config drift, API contract mismatch, malformed input, doc-vs-reality skew                                  |
| **From**   | Stage 6+ (hand-rolled `if`-chain validators) or Stage 10 (runtime parse errors, prose-as-contract)         |
| **To**     | Stage 0 (codegen), Stage 2 (editor), Stage 5 (build), Stage 8a (deploy) — **one artifact, multiple rungs** |

Schemas are the highest-leverage shift in this catalogue because the same
artifact powers checks at every stage that can read it:

- **Stage 0** — codegen produces static types: JSON Schema →
  `json-schema-to-typescript`; OpenAPI → server / client stubs; Protobuf → typed
  clients; XSD → C# / Java classes.
- **Stage 2** — editor schemas drive autocomplete and inline validation for
  hand-edited files (`$schema` in JSON, `xsi:schemaLocation` in XML, YAML
  language server hints).
- **Stage 5** — CI validates committed files against the schema (`ajv`,
  `xmllint`, `spectral` for OpenAPI, `buf lint` for Protobuf).
- **Stage 8a** — pre-deploy gate rejects config that does not match the schema
  before it reaches a running service.
- **Boundary runtime** — schema-bridged TS libraries (`zod`, `typebox`, `io-ts`,
  `valibot`) make the schema the single source: static type plus runtime
  validator generated from one declaration. Use at every external input
  boundary (HTTP body, env vars, message payload).

Catalogue: JSON Schema (configs, `package.json`), OpenAPI (HTTP), gRPC /
Protobuf (service-to-service), GraphQL SDL, AsyncAPI (events), Avro (streaming),
XSD (XML / SOAP).

The win is not _"we validate"_ — it is _"validation comes from a single artifact
that fans out to every appropriate stage."_ Two hand-written sources checking
the same shape are the same-scope duplication §Directive 3 forbids; one schema
is the antidote.

### 6.4 Optional check → blocking gate

|            |                                                 |
| ---------- | ----------------------------------------------- |
| **Shifts** | The check itself, from advisory to enforced     |
| **From**   | Stage where the check exists but does not block |
| **To**     | Same stage, now a gate                          |

The most common shift-left failure is having the right check at the right stage
and not making it block. A typecheck run as a manual `npm run` command has zero
shift-left value relative to no typecheck at all. Audit:

- Pre-commit hook fails → does it block the commit, or just print?
- CI job fails → does branch protection require it before merge?
- Lint warning → is the rule severity `error` or `warn`?
- Coverage drop → does it fail the build, or land in a report nobody opens?

### 6.5 Scope-justified backstops

§Directive 3 allows later backstops when two layers run the same check on
different scopes:

- **Pre-commit** — staged files only, fast, narrow, bypassable with
  `--no-verify`.
- **CI** — full repo, slow, complete, un-bypassable behind branch protection.

Both are warranted: different blast radii (single commit vs. branch), different
bypass costs. Layering pays when the earlier layer is faster _and_ bypassable —
the later layer is the un-bypassable backstop, not a duplicate.

---

## 7. Stack-Aware Tooling Survey

Use this only when the user asks for tooling recommendations or implementation
options. A plain shift-left audit stops at the missing category.

1. **Detect the stack:** manifests, lockfiles, scripts, test runners, CI/CD
   files, IaC/deploy config, hook runners, and editor config. Record present and
   absent signals.
2. **Map gaps to categories:** name the stage, defect class, and missing tool
   category. Do not jump straight to products.

| Stage  | Tool category to look for                                         |
| ------ | ----------------------------------------------------------------- |
| **0**  | Type system / compiler strictness flags / schema-as-code library  |
| **1**  | ADR template, schema registry, threat-model artifact              |
| **2**  | LSP, editor lint integration, formatter-on-save                   |
| **3**  | Hook runner, secret scanner, commit-message linter                |
| **4**  | Compiler / type-checker invoked in build                          |
| **5**  | Linter, dependency auditor, SAST, license checker, IaC scanner    |
| **6**  | Unit test runner, property-test library, coverage gate            |
| **7**  | Integration / contract test harness, container build verifier     |
| **8a** | Migration dry-run, config validator, IAM diff, cost projector     |
| **8b** | Smoke-test runner, health-probe spec, orchestrator readiness gate |
| **9**  | Canary controller, load generator, perf-regression gate           |
| **10** | Runtime monitoring, error tracker, SLO alerting                   |
| **11** | Incident-record system, RCA template                              |

3. **Find specific options only on request:** search the detected ecosystem,
   filter for stack compatibility, prefer tools already present in the stack,
   and cite each option with a source URL and release/currency signal.

Produce one row per gap:

| Stage | Defect class at risk | Detected stack signal | Candidate tool category | Specific options (cited) | Effort |
| ----- | -------------------- | --------------------- | ----------------------- | ------------------------ | ------ |

Do not propose a tool without naming the stage it staffs and the defect class it
catches. A tool that does not map to a rung on §1 has no place in the output.

## 8. See also

- **`architecture-as-code`** — the codified-architecture pattern this skill names in §6.2.
- **`architecture-guidelines`** — first-principles rules whose violations this skill places on the ladder.
- **`ci-cd-reliability-architecture`** — pipeline rules that staff Stages 5–10.
- **`push-out`** — move recurring operational work out of human/manual execution into durable systems.
- **`bring-down`** — move bespoke or duplicated code down into reusable capability.
- **`continuous-improvement`** — how to promote a recurring escaped-defect into a permanent gate (Directive 1).
