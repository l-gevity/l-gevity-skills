# Stack-Aware Tooling Survey

Use this only when the user asks for tooling recommendations or implementation
options; a plain shift-left audit stops at the missing category. `SKILL.md` §7
points here.

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
| **5**  | Linter, dependency auditor, SAST, license checker, IaC scanner, fitness-function runner |
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
