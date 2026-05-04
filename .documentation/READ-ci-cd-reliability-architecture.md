# CI/CD Reliability Architecture

A pipeline-design SKILL for builds and deployments that are safe to run any number of times, build artifacts once, deploy without downtime, and authenticate without storing secrets.

## Why use this

- **Pipelines become safe to retry.** Idempotent jobs produce the same result whether run zero, one, or three times — no partial state, no clean-up rituals.
- **"Works in staging, broken in prod" stops happening.** One immutable artifact moves through environments; config is injected at deploy time, not baked at build time.
- **Deploys don't drop traffic.** Preview environments per PR, atomic promotion, post-deploy health checks, automatic rollback.
- **Stored cloud credentials disappear.** OIDC federation issues short-lived tokens; the pipeline proves identity instead of presenting a secret.
- **Platform-builder surprises stop shipping stale code.** Every build runs in a dedicated fail-fast CI step; the deploy action receives a pre-built artifact.

## Fundamental principles

CI/CD reliability is mostly the application of six rules. When pipelines fail in surprising ways — duplicated work, environment skew, dropped requests, leaked credentials — it is almost always because one of these six was assumed instead of designed.

- **Idempotent.** Safe to run 0, 1, or N times. Same result every time.
- **Self-contained.** Each job declares its inputs, outputs, and failure mode; never assumes upstream state.
- **Immutable artifacts.** Build once, promote everywhere. Tag with the commit SHA; inject config at deploy time.
- **Self-healing.** Transient failures auto-retry with backoff; permanent failures fail fast.
- **Zero-downtime.** Preview environments, atomic promotion, never touch production directly.
- **Zero-knowledge.** Minimal seed secrets; dynamic tokens via OIDC/STS; no credential exchange.

## How to use

The skill has two modes: **design** a new pipeline, or **audit** an existing one.

1. **Identify the workflow or deploy target.** A new GitHub Actions pipeline, an existing flaky deploy, or a single job that keeps producing partial state.
2. **Prompt the AI.**

   > *Design:* "Design the CI/CD pipeline for a Node service deploying to Azure App Service with preview environments per PR."
   >
   > *Audit:* "Audit `.github/workflows/deploy.yml` against ci-cd-reliability-architecture. Flag idempotency gaps, missing health checks, and any stored cloud credentials."

3. **Read the verdict.** The skill names the violated rule (idempotency / self-containment / immutability / self-healing / zero-downtime / zero-knowledge) and gives the standard fix.
4. **Apply the fix.** Replace `npm install` with `npm ci`; tag artifacts by SHA; switch from stored secrets to OIDC; add the post-deploy health check and rollback step.

## Common anti-patterns and their fixes

| Anti-pattern                                      | Fix                                                          | Rule violated      |
|---------------------------------------------------|--------------------------------------------------------------|--------------------|
| `npm install` in CI                               | `npm ci` (lock-file exact match)                             | Idempotency        |
| Rebuild per environment                           | Build once; promote the same artifact                        | Immutable artifacts|
| URLs/secrets baked into build output              | Inject config at deploy time                                 | Immutable artifacts|
| Delegate build to platform (Oryx, Buildpacks, …)  | Build in dedicated CI step; deploy receives pre-built output | Immutable artifacts|
| Stored cloud password / long-lived API key        | OIDC federated identity → short-lived token                  | Zero-knowledge     |
| Deploy without post-deploy validation             | Health check + automatic rollback on failure                 | Self-healing       |
| No timeout on long-running steps                  | Explicit `timeout:` on every step                            | Self-healing       |
| Stomping on shared paths between jobs             | Namespace artifacts by branch/PR; explicit `download:`       | Self-contained     |
| Leaving in-progress runs to fight each other      | `cancel-in-progress: true` on the same branch                | Zero-downtime      |

## Pre-merge checklist (critical items)

- [ ] Idempotent: safe to run 0×, 1×, or N×; same result every time.
- [ ] Timeouts on every long-running step.
- [ ] Build once in a dedicated fail-fast CI step; deploy receives the pre-built artifact.
- [ ] OIDC / federated identity for cloud auth; no stored cloud credentials.
- [ ] Post-deploy health check present; rollback on failure.
- [ ] Preview environment per PR; atomic promotion to production on merge.
- [ ] `cancel-in-progress` enabled; only the latest commit deploys.

## When to skip

One-off scripts, throwaway prototypes, scratch repos with no deploy target. The framework earns its keep the first time a flaky deploy drops traffic — which is to say, immediately.

## Next steps

- See [SKILL.md](./SKILL.md) for the full reference (per-section anti-pattern tables, OIDC pseudocode, secret rotation procedure, IaC delete-and-recreate pattern, full pre-merge checklist).
- For shifting reliability checks earlier in the pipeline, see [`defect-shift-left`](../defect-shift-left/).
- For build-time architectural enforcement (the dependency graph itself), see [`architecture-as-code-javascript`](../architecture-as-code-javascript/) or [`architecture-as-code-python`](../architecture-as-code-python/).
