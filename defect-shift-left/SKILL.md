---
name: defect-shift-left
description: >
    Places every error detection at the earliest stage of the pipeline that is
    technically capable of catching it. Use when designing or auditing a CI/CD
    pipeline, choosing tooling, deciding where a check belongs, or asking "could
    this have been caught earlier?"
---

# Defect Shift-Left

> Pipeline stages have a strict order. Every defect has an earliest stage at
> which it can be caught. Catching it later is always a regression.

> **Directives**
>
> 1. **Prevent over detect.** Make invalid states unrepresentable before adding
>    a check.
> 2. **Earliest possible stage is mandatory.** If a check _can_ run at stage N,
>    running it at N+1 is a regression.
> 3. **Replace, don't layer.** When shifting a check earlier, remove the later
>    one.
> 4. **Fail loud at the origin.** Errors must surface where they originated.

---

## 1. The Ladder

| Stage  | Phase                   | What runs here                                                            |
| ------ | ----------------------- | ------------------------------------------------------------------------- |
| **0**  | Language                | Type system, syntax, language semantics                                   |
| **1**  | Design                  | Spec, ADR, threat model, schema                                           |
| **2**  | Authoring               | LSP, in-editor lint, formatter                                            |
| **3**  | Pre-commit              | Format, fast lint, secret scan, commit-msg hook                           |
| **4**  | Compile                 | Compiler, type-checker, codegen                                           |
| **5**  | Build / Static analysis | Full lint, depcheck, SAST, license, CVE, bundle, IaC, fitness functions   |
| **6**  | Unit test               | Local test runner, property tests                                         |
| **7**  | Integration / Contract  | CI suite, contract tests, container builds                                |
| **8a** | Pre-deploy static       | Migration dry-run, config-vs-env, capacity, IAM diff _(deploy abortable)_ |
| **8b** | Deploy execution        | Smoke, health probes, slot readiness _(rollback on failure)_              |
| **9**  | Canary / Staging        | Partial traffic, real env, perf regression                                |
| **10** | Production runtime      | Live traffic, monitoring                                                  |
| **11** | Post-incident           | Forensics, RCA                                                            |

Cost grows roughly geometrically with stage. The ladder is monotonic — later
detection is never neutral.

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

| Defect class                                    | Stage | Mechanism (fallback)                            |
| ----------------------------------------------- | ----- | ----------------------------------------------- |
| Type mismatch, null deref, semantic-type mixing | 0     | Type system                                     |
| Missing case handling                           | 0     | Exhaustive sum types                            |
| Off-by-one / range                              | 0     | Refinement types (else 6: property test)        |
| Use-after-free, race                            | 0     | Linear / borrow types (else 5: static analysis) |
| Schema / contract mismatch                      | 1     | Shared schema (else 5: codegen check)           |
| Forbidden architectural dependency              | 1     | ADR (else 5: depcheck)                          |
| Authorization model gap                         | 1     | Threat model (else 7: security test)            |
| Style, formatting, unused code, API misuse      | 2     | LSP / editor (else 5: lint)                     |
| Banned API / unsafe pattern                     | 2     | LSP rule (else 5: lint)                         |
| Secret in source                                | 3     | Pre-commit scanner (else 5: SAST)               |
| Symbol resolution / missing import              | 4     | Compiler                                        |
| CVE in dependency                               | 5     | SCA audit                                       |
| License incompatibility                         | 5     | License audit                                   |
| Bundle / artifact regression                    | 5     | Bundle validator                                |
| Logic error in pure function                    | 6     | Unit test                                       |
| Property violation across input space           | 6     | Property test                                   |
| Integration boundary mismatch                   | 7     | Contract test                                   |
| Container / build reproducibility               | 7     | CI image build                                  |
| Performance regression (micro)                  | 7     | Benchmark (else 9: load test)                   |
| Migration vs current schema                     | 8a    | Dry-run against prod DB                         |
| Irreversible migration                          | 8a    | Reversibility check                             |
| Cross-service version skew                      | 8a    | Version-matrix gate                             |
| Backwards-incompatible API change               | 8a    | Contract diff vs deployed                       |
| Missing / expired secret in target env          | 8a    | Secret-store presence check                     |
| Undefined feature flag in target                | 8a    | Flag-store consistency                          |
| Capacity / quota exceeded                       | 8a    | Resource projection                             |
| IAM permission expansion                        | 8a    | IAM diff                                        |
| Cost / budget breach                            | 8a    | Cost projection                                 |
| Missing rollback artifact                       | 8a    | Registry probe                                  |
| Compliance approval missing                     | 8a    | Policy gate                                     |
| Artifact crashes on boot                        | 8b    | Startup smoke                                   |
| Health probe never passes                       | 8b    | Orchestrator readiness gate                     |
| Target env unreachable dependency               | 8b    | Boot connectivity check                         |
| Resource exhaustion under load                  | 9     | Load test                                       |
| Real-world latency / SLO breach                 | 10    | Production monitoring                           |

---

## 4. The Algorithm

1. **Inventory** every check and the stage it runs at (including manual reviews
   and runtime asserts).
2. **Classify** each by defect class (§3).
3. **Compute Δstage** = current − earliest possible.
4. **Prioritize** by Δstage × frequency.
5. **Move the check** to the earlier stage.
6. **Verify and remove** the later check once the earlier one is proven.
   Layering is doubled cost, not doubled safety.
7. **Every escaped defect is a forced audit:** find its earliest possible stage;
   place the check there.

---

## 5. Anti-Patterns

| Pattern                                    | Stage actual / earliest      |
| ------------------------------------------ | ---------------------------- |
| Runtime check for type errors              | 10 / 0                       |
| CI test for formatting                     | 7 / 2                        |
| Linter only in CI                          | 7 / 2 + 5                    |
| Code review as primary defect filter       | 7 / 2–5                      |
| Production monitor for known-bad input     | 10 / 0                       |
| Compile errors hidden behind dynamic types | 6+ / 0                       |
| Manual deployment checklist                | 8 / 5                        |
| Documentation as the contract              | 7+ / 1                       |
| Deploy-and-pray monitoring                 | 10 / 8a                      |
| Migration applied without dry-run          | 8b–10 / 8a                   |
| Secrets / config validated only at runtime | 10 / 8a                      |
| Manual rollback on deploy failure          | 10 / 8b                      |
| No canary, full traffic on new artifact    | 10 carries full blast radius |
| Retry as error handling                    | hides 10 indefinitely        |
| Catch-and-log silent failure               | propagates past origin       |
| Warnings nobody reads                      | detection without action     |

---

## 6. Decision Protocol

1. Identify the defect class (§3).
2. Look up earliest possible stage.
3. Compare to current/proposed stage.

| Situation                                 | Action                                         |
| ----------------------------------------- | ---------------------------------------------- |
| Proposed = earliest possible              | Proceed                                        |
| Proposed > earliest, earlier feasible now | Reject — implement at the earlier stage        |
| Proposed > earliest, requires effort      | Document gap as technical debt; schedule shift |
| No check; defects only in production      | Critical — work backward from Stage 10         |
| Check requires target-env state           | Stage 8a is earliest — do not push to Stage 10 |

If a gap remains, state: _"Detection Gap: defect class catchable at Stage [X],
currently at Stage [Y]. Mechanism: [...]."_

---

## 7. Common Shift Patterns

Recurring moves that shift a defect class from a later stage to an earlier one.
Recognise them; apply them deliberately.

### 7.1 Untyped → strict-typed source

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
typecheck nobody runs is theatre — see §7.4.

### 7.2 ADR → executable architectural rule

|            |                                                                                            |
| ---------- | ------------------------------------------------------------------------------------------ |
| **Shifts** | Forbidden imports, layering violations, banned API usage, accidental cross-module coupling |
| **From**   | Stage 1 (design doc) or Stage 7+ (code review)                                             |
| **To**     | Stage 5 (static analysis)                                                                  |

Architectural rules expressed in prose are advice; rules expressed in lint
config are enforcement. `eslint-plugin-boundaries`,
`import/no-restricted- paths`, `dependency-cruiser`, ArchUnit (JVM), Pyright
import rules — all turn an ADR sentence into a build failure.

The recipe: encode each architectural decision as a rule that fails the build
when violated. The ADR document remains as rationale; the lint config is the
enforcement.

For the in-repo implementation see `architecture-as-code-javascript`,
`architecture-guidelines` (first principles), and `geometric-architecture`
(spatial rationale).

### 7.3 Hand-validated boundary → schema-as-code

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
  validator generated from one declaration. Use at every external- input
  boundary (HTTP body, env vars, message payload).

Catalogue: JSON Schema (configs, `package.json`), OpenAPI (HTTP), gRPC /
Protobuf (service-to-service), GraphQL SDL, AsyncAPI (events), Avro (streaming),
XSD (XML / SOAP).

The win is not _"we validate"_ — it is _"validation comes from a single artifact
that fans out to every appropriate stage."_ Two checks for the same shape from
two hand-written sources is exactly the layering §Directive 3 forbids; one
schema is the antidote.

### 7.4 Optional check → blocking gate

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

### Layering exception: scope-justified defense-in-depth

§Directive 3 says _"replace, don't layer."_ The exception is when two layers run
the same check on different scopes:

- **Pre-commit** — staged files only, fast, narrow, bypassable with
  `--no-verify`.
- **CI** — full repo, slow, complete, un-bypassable behind branch protection.

Both are warranted: different blast radii (single commit vs. branch), different
bypass costs. Layering pays when the earlier layer is faster _and_ bypassable —
the later layer is the un-bypassable backstop, not a duplicate.

---

## 8. Stack-Aware Tooling Survey

The ladder is universal; the tools that staff each rung are not. When auditing
or designing a pipeline, derive the toolset from the project's actual stack — do
not assume one. Names go stale; categories do not.

### 8.1 Detect the stack

Inspect, in order, only what exists:

1. **Language / runtime** — manifest files (`package.json`, `pyproject.toml`,
   `go.mod`, `Cargo.toml`, `pom.xml`, `*.csproj`, `Gemfile`, `composer.json`,
   etc.), lockfiles, and primary source extensions.
2. **Build / package system** — declared scripts, build tool, bundler.
3. **Test frameworks** — already-declared test runners and assertion libs.
4. **CI / CD** — `.github/workflows/`, `.gitlab-ci.yml`, `azure-pipelines.yml`,
   `Jenkinsfile`, etc.
5. **Infra / deploy targets** — IaC files (`*.tf`, `*.bicep`, `serverless.yml`,
   `Dockerfile`, k8s manifests), platform configs (`staticwebapp.config.json`,
   `vercel.json`, `netlify.toml`).
6. **VCS hooks** — `husky`, `pre-commit`, `lefthook`, native `.git/hooks`.
7. **Editor config** — `.editorconfig`, `.vscode/`, declared LSPs.

Record what is present. Record what is absent — absence is the gap.

### 8.2 Map stages to tool categories

For each ladder stage, the survey asks _what category of tool belongs here_,
never _which specific tool_:

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

### 8.3 Find stack-compatible options

For every stage where a category is unstaffed in the detected stack:

1. **Search the ecosystem of the detected stack** for current tools in that
   category. Use a web search; do not rely on training-time recall, which is
   stale.
2. **Filter for compatibility.** Reject candidates that require a runtime,
   package manager, or platform the project does not already use, unless the
   benefit clearly justifies adopting it.
3. **Prefer tools the stack already pulls in.** A linter plugin beats a new
   linter; a built-in compiler flag beats a third-party checker.
4. **Cite each candidate** with its source URL and last-release signal so the
   user can verify currency.

### 8.4 Output

Produce a survey table — one row per stage that has a gap:

| Stage | Defect class at risk | Detected stack signal | Candidate tool category
| Specific options (cited) | Effort |

Do not propose a tool without naming the stage it staffs and the defect class it
catches. A tool that does not map to a rung on §1 has no place in the output.
