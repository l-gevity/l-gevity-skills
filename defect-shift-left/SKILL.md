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

| Technique                       | Eliminates                       |
| ------------------------------- | -------------------------------- |
| Strong / branded types          | Type confusion, semantic mixing  |
| Sum types + exhaustive matching | Missing case, silent fallthrough |
| Option / Result types           | Null deref, silent failure       |
| Refinement types                | Range, off-by-one                |
| Linear / affine types           | Use-after-free, double-close     |
| Schema-as-code                  | Config drift, contract mismatch  |
| Const / immutable default       | Accidental mutation, race        |

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

## 7. Stack-Aware Tooling Survey

The ladder is universal; the tools that staff each rung are not. When auditing
or designing a pipeline, derive the toolset from the project's actual stack — do
not assume one. Names go stale; categories do not.

### 7.1 Detect the stack

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

### 7.2 Map stages to tool categories

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

### 7.3 Find stack-compatible options

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

### 7.4 Output

Produce a survey table — one row per stage that has a gap:

| Stage | Defect class at risk | Detected stack signal | Candidate tool category
| Specific options (cited) | Effort |

Do not propose a tool without naming the stage it staffs and the defect class it
catches. A tool that does not map to a rung on §1 has no place in the output.
