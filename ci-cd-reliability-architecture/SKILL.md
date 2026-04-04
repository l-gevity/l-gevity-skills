---
name: ci-cd-reliability-architecture
description:
    Establishes idempotency, self-containment, immutable artifacts,
    self-healing, zero-downtime, and zero-knowledge security for CI/CD
    pipelines. Use this skill when designing, auditing, or debugging any
    workflow or deployment pipeline.
---

# CI/CD Reliability Architecture

> **Out of scope**: Business logic (`architecture-guidelines`), code standards
> (`coding-standard`), optimization (`system-optimization`), release procedures
> (`release-management`).

> **TL;DR**
>
> 1. **Idempotent**: Safe to run 0, 1, or N times. Same result every time.
> 2. **Self-Contained**: Each job declares inputs/outputs. No implicit state.
> 3. **Immutable Artifacts**: Build once, promote everywhere. Config at deploy
>    time.
> 4. **Self-Healing**: Transient failures auto-retry. Permanent failures fail
>    fast.
> 5. **Zero-Downtime**: Preview environments, atomic promotion. Never touch
>    production directly.
> 6. **Zero-Knowledge**: Minimal seed secrets. Dynamic tokens via OIDC/STS. No
>    credential exchange.

---

## 1. Idempotency

| Anti-Pattern                   | Fix                                    | Why                      |
| ------------------------------ | -------------------------------------- | ------------------------ |
| `npm install`                  | `npm ci`                               | Lock-file exact match    |
| `mkdir build`                  | `mkdir -p`                             | No-op if exists          |
| Delete then create             | Create then delete                     | Gap causes downtime      |
| `git commit --amend` published | Create new commit                      | Never amend pushed work  |
| Assume upstream state          | Explicit `needs:` + download artifacts | Prevents race conditions |

**Checklist:**

- [ ] Produces same output if run 1x, 3x, or 0x
- [ ] File operations use safe defaults (`-p`, `-f`, `--force`)
- [ ] Secrets: create new first, apply everywhere, then delete old
- [ ] DB updates use conditional writes (`WHERE version = X`)

---

## 2. Self-Contained Jobs

Each job declares **inputs**, **steps**, **outputs**, **failure mode**:

```yaml
jobs:
    build:
        needs: [lint, test] # Explicit upstream dependencies
        outputs:
            artifact: BUILD_PATH # Named output; consumers reference by name
        steps:
            - name: Download artifacts
              download: test-results # Explicit artifact fetch; never assume presence
            - name: Setup runtime
              tool: node@20
              cache: npm # Caching is NOT implicit state — it is a performance hint
            - name: Build
              id: build
              run: npm run build
        continue-on-error: false # Fail-fast
        timeout: 15m # Prevent stuck jobs
```

**Rules:**

- Never assume upstream state; always download artifacts explicitly
- Caching (dependencies, browsers, etc.) does not violate self-containment — it
  is scoped performance optimization within job isolation
- Namespace all artifacts uniquely (e.g., include branch name or PR number)
- Never write to shared paths without explicit scoping
- Declare failure mode explicitly (`continue-on-error` or default fail-fast)

---

## 3. Immutable Artifacts

**Principle**: Build once, promote the same artifact across environments. Never
rebuild to change target environment.

| Anti-Pattern                        | Fix                                                   | Why                                           |
| ----------------------------------- | ----------------------------------------------------- | --------------------------------------------- |
| Rebuild per environment             | Build once; promote the same output                   | Eliminates "works in staging" divergence      |
| Bake URLs/secrets into build output | Inject config at deploy time (env vars, config files) | Same artifact, different config               |
| Tag artifacts with branch name only | Tag with commit SHA (+ optional semver)               | SHA is immutable; branch names move           |
| Store artifacts only in CI cache    | Publish to an artifact registry                       | Decouples build from deploy; enables rollback |

**Rules:**

- The build step produces a **versioned, immutable artifact** (archive, image,
  bundle) tagged with the commit SHA
- Environment-specific values (API URLs, feature flags, secrets) are injected at
  **deploy time**, never at build time
- Promoting to production means deploying the **same artifact** that passed
  staging — not triggering a new build
- Rollback means redeploying a **previous known-good artifact**, not reverting
  code and rebuilding

---

## 4. Self-Healing

| Failure Type                         | Retry? | Example                           |
| ------------------------------------ | ------ | --------------------------------- |
| HTTP 5xx, timeout, ECONNREFUSED      | Yes    | Retry 3x with 5s, 10s, 20s delays |
| HTTP 4xx, missing file, syntax error | No     | Fail immediately; fix code        |
| Disk full, out of memory             | No     | Escalate to ops                   |

**Exponential backoff (sufficient for single-step retry):**

```bash
for attempt in 1 2 3; do
  command && exit 0
  delay=$((5 * 2 ** (attempt - 1)))  # 5s, 10s, 20s
  sleep "$delay"
done
exit 1
```

**Post-deploy health check (mandatory):**

```yaml
- name: Deploy
  run: ./deploy.sh
  timeout: 15m # Prevent stuck jobs

- name: Health Check
  run: curl -f https://deployed-url/health || exit 1
  timeout: 5m

- name: Rollback on Failure
  on_failure: true
  run: ./rollback.sh
```

**Rules:**

- Always set an explicit timeout on every long-running step (prevents default
  hangs)
- Transient failures: retry 3x with exponential backoff + jitter
- Permanent failures: fail fast, no retry
- All deployments must emit a health signal; rollback on failure
- Never apply partial state

---

## 5. Zero-Downtime

| Layer              | Pattern                                                                                  | Why                                                   |
| ------------------ | ---------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| **Frontend**       | Deploy to isolated preview environment per PR; atomically promote to production on merge | Production untouched during validation; safe to retry |
| **Backend**        | Deploy to staging slot; health-check; swap (platform handles connection draining)        | Graceful shutdown; in-flight requests complete        |
| **API versioning** | New endpoints `/v2/...` alongside `/v1/...`; deprecate, never delete                     | Clients remain backwards-compatible                   |
| **PR concurrency** | Cancel in-progress runs for the same branch; only latest commit deploys                  | Prevent old commits overwriting newer deployments     |

**Rules:**

- Never force-stop running instances (drops in-flight connections)
- Always test in a staging/preview environment before promoting to production
- Adding fields to API payloads is safe; removing or renaming fields breaks
  clients
- If E2E tests fail on a preview environment: block the merge; preview
  auto-cleaned on PR close
- For multi-tenant data layers, apply the Expand/Contract pattern for schema
  changes

---

## 6. Zero-Knowledge Secrets

**Principle**: Minimize permanent credentials. Prove identity via
challenge/signature (OIDC), not secret exchange.

| Credential Type        | Store as long-lived secret? | How to obtain at runtime              | Notes                          |
| ---------------------- | --------------------------- | ------------------------------------- | ------------------------------ |
| Cloud provider auth    | 1 federated identity only   | OIDC federated credential             | Rotate quarterly; no password  |
| API keys               | Only if no OAuth available  | STS / service principal exchange      | Auto-expire; never store value |
| Encryption / HMAC keys | 1 per environment           | Generate once; rotate via dual-deploy | Create new, apply, delete old  |
| DB connection strings  | Never                       | Managed Identity / service binding    | No secret needed               |
| OAuth client secrets   | Never                       | Client credentials + certificate      | Certificate-based auth         |

**OIDC pattern (pseudocode):**

```yaml
permissions:
    id-token: write # Pipeline requests a short-lived identity token
    contents: read

jobs:
    deploy:
        steps:
            - name: Authenticate to cloud (OIDC)
              # CI platform presents signed JWT to cloud provider's STS.
              # Cloud issues short-lived access token — no stored credential exchanged.
              cloud-login:
                  method: oidc
                  client-id: $SECRET_CLIENT_ID
```

**Secret rotation (zero-downtime):**

1. Create new credential
2. Apply new credential everywhere it is used
3. Verify all consumers are using the new credential
4. Delete the old credential

**Audit logging (mandatory):**

- Log all secret reads: timestamp, actor, resource, purpose
- Never log secret values
- Enable audit logging on your secrets manager

**Secret hygiene:**

- Enable secret scanning in your SCM (passive, on every push)
- Block accidental commits of `.env`, keys, credentials via `.gitignore` +
  pre-commit hooks
- If a secret leaks: rotate immediately, revoke old credential, audit access
  logs

---

## 7. Infrastructure Idempotency

For ad-hoc environment config, imperative CLI commands are acceptable when they
are **idempotent** (create-or-update semantics, `--no-fail-on-existing` guards).
They become fragile at scale.

When managing infrastructure at scale (multi-tenant, scaling policies, resource
groups), use **declarative IaC** (Bicep, Terraform, Pulumi). Declarative tools
enforce idempotency by design; imperative scripts require manual guards.

---

## Pre-Merge Checklist

### CRITICAL (Must-Have)

- [ ] **Idempotency**: Safe to run 0x, 1x, or Nx; same result every time
- [ ] **Timeouts**: All long-running steps have explicit timeout values
- [ ] **Immutable artifacts**: Build once, promote same artifact; config
      injected at deploy time
- [ ] **Secrets**: OIDC/federated identity for cloud auth; no stored cloud
      credentials
- [ ] **Health check**: Post-deploy validation present; rollback on failure
- [ ] **E2E tests**: Failure blocks merge via branch protection rule
- [ ] **Preview environments**: All deployments use isolated preview; production
      promoted atomically
- [ ] **PR concurrency**: Cancel-in-progress enabled; only the latest commit
      deploys

### ADVANCED (Nice-to-Have)

- [ ] API backward-compatibility: add fields, never remove; deprecation
      documented
- [ ] IaC migration: declarative infrastructure for resources managed at scale
- [ ] DB migrations: Expand/Contract pattern for schema changes (multi-tenant)
- [ ] Secret rotation audit: quarterly seed secret rotation logged
