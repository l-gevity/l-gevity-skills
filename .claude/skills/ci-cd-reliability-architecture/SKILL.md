---
name: ci-cd-reliability-architecture
description: >-
    Establishes idempotency, self-containment, immutable artifacts,
    self-healing, zero-downtime, and zero-knowledge security for CI/CD
    pipelines, including evidence-gated release and production promotion. Use
    this skill when designing, auditing, or debugging any workflow, release, or
    deployment pipeline.
---

# CI/CD Reliability Architecture

> **Out of scope**: Business logic (`architecture-guidelines`), value-stream
> optimization (`system-optimization`), release planning/versioning, and ongoing
> production operations. This skill owns technical promotion from a verified
> artifact through a bounded production-verification window and owner handoff.

> **Core Directives**
>
> 1. **Idempotent** — converges to the same desired state when run or retried (§1).
> 2. **Self-Contained** — explicit inputs, outputs, failure mode (§2).
> 3. **Immutable Artifacts** — build once, promote; config at deploy time (§3).
> 4. **Self-Healing** — retry transient, fail-fast permanent (§4).
> 5. **Zero-Downtime** — preview environment, atomic promotion (§5).
> 6. **Zero-Knowledge** — OIDC / federated identity, no standing cloud secrets (§6).
> 7. **Evidence-Gated** — every merge and promotion is blocked by the earliest
>    applicable verification gate (§9).

---

## 1. Idempotency

| Anti-Pattern                   | Fix                                    | Why                      |
| ------------------------------ | -------------------------------------- | ------------------------ |
| `npm install`                  | `npm ci`                               | Lock-file exact match    |
| `mkdir build`                  | `mkdir -p`                             | No-op if exists          |
| Delete live resource first     | Create replacement; switch; delete old | Gap causes downtime      |
| `git commit --amend` published | Create new commit                      | Never amend pushed work  |
| Assume upstream state          | Explicit `needs:` + download artifacts | Prevents race conditions |

**Checklist:**

- [ ] Converges to the same desired state if skipped, run once, or retried
- [ ] File operations use scoped idempotent flags and precondition checks
- [ ] Secrets: create new first, apply everywhere, then delete old
- [ ] DB updates use conditional writes (`WHERE version = X`)

---

## 2. Self-Contained Jobs

Each job declares **inputs**, **steps**, **outputs**, **failure mode**.
The YAML below is platform-neutral pseudocode; translate the keys to the target
CI system instead of copying it verbatim:

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
- Namespace all artifacts uniquely with commit SHA or run ID; branch or PR
  number is metadata, not the uniqueness key
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
- **Never delegate the build to the deploy platform's implicit builder** (Oryx,
  Cloud Native Buildpacks, Vercel/Netlify auto-build, etc.). Platform builders
  frequently report `success` even when a sub-build (TS compile, webpack, native
  module) fails, silently shipping stale or incomplete artifacts. Run every
  build in a dedicated CI step with `continue-on-error: false`, and pass the
  pre-built output to the deploy action (`skip_app_build: true`,
  `skip_api_build: true`, or equivalent)

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

**Post-deploy health check (mandatory, platform-neutral pseudocode):**

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
| **API versioning** | Additive changes for tolerant readers; version and deprecate breaking changes            | Clients remain backwards-compatible                   |
| **PR concurrency** | Cancel in-progress runs for the same branch; only latest commit deploys                  | Prevent old commits overwriting newer deployments     |

**Rules:**

- Never force-stop running instances (drops in-flight connections)
- Always test in a staging/preview environment before promoting to production
- Adding fields is compatible only when clients are tolerant readers; removing
  or renaming fields breaks clients
- If E2E tests fail on a preview environment: block the merge; preview
  auto-cleaned on PR close
- For multi-tenant data layers, apply the Expand/Contract pattern for schema
  changes

---

## 6. Zero-Knowledge Secrets

**Principle**: Minimize permanent credentials. For cloud auth, prove identity
via challenge/signature (OIDC) instead of exchanging a stored password or token.
Store unavoidable application secrets only in a managed secrets store with
audit logging and rotation.

| Credential Type        | Store as long-lived CI secret? | How to obtain at runtime                     | Notes                                      |
| ---------------------- | ------------------------------ | -------------------------------------------- | ------------------------------------------ |
| Cloud provider auth    | No                             | OIDC federated credential                    | Short-lived token; no password             |
| API keys               | Only if no OAuth/OIDC exists   | OAuth, STS, or managed secrets store         | Prefer auto-expiring credentials           |
| Encryption / HMAC keys | No CI copy; store in KMS/vault | KMS/vault lookup or managed key reference    | Rotate with create, apply, verify, delete  |
| DB connection strings  | Avoid                          | Managed Identity / service binding           | Prefer no secret in CI                     |
| OAuth client secrets   | Avoid                          | Certificate/private-key auth where supported | If required, store only in secrets manager |

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
                  client-id: $CLOUD_CLIENT_ID
```

**Secret rotation (zero-downtime):**

1. Create new credential
2. Apply new credential everywhere it is used
3. Verify all consumers are using the new credential
4. Delete the old credential

**Audit logging (mandatory):**

- Log secret access where the secrets manager supports it: timestamp, actor,
  resource, purpose
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

### Replacement Pattern (Immutable Resources)

Some resources cannot be updated in-place (e.g., AWS security groups, Azure
Entra policies, some Kubernetes resources). For these, use definition-based
comparison to detect changes and replace safely. Prefer create-before-delete
or provider-native atomic replacement. If the provider requires deleting before
creating because a unique name cannot coexist, preflight the replacement, keep
rollback input ready, and fail loud if the create step does not succeed:

```bash
# 1. Compute hash of desired state
DESIRED_HASH=$(echo "${DEFINITION}" | sha256sum | cut -d' ' -f1)

# 2. Fetch existing resource and hash its definition
EXISTING=$(curl -s https://api/resource/current)
EXISTING_HASH=$(echo "${EXISTING}" | sha256sum | cut -d' ' -f1)

# 3. If unchanged, skip (idempotent)
if [ "${DESIRED_HASH}" = "${EXISTING_HASH}" ]; then
  echo "Resource up-to-date, skipping"
  exit 0
fi

# 4. Preflight replacement before touching the live resource
curl -f -X POST https://api/resource/validate -d "${DEFINITION}"

# 5. Replace with the provider's atomic operation when available.
# If delete-before-create is the only supported path, this is an explicit
# exception that must have rollback input and failure handling.
curl -f -X DELETE https://api/resource/current
curl -f -X POST https://api/resource -d "${DEFINITION}"
```

**Rules:**

- Always hash/checksum the definition, not just presence checks
- Use provider-native atomic replacement or create-before-delete when available
- Delete-before-create is an exception for provider constraints, not the default
- Wrap creation in idempotent guard and failure handling
- Log state transitions: "definition changed, updating"

---

## 8. Release and Production Promotion

Promotion is an evidence-gated state machine, not a successful deploy command:

```text
BUILD-VERIFIED → RELEASE-READY → DEPLOYING
→ PRODUCTION-VERIFYING → DEPLOYED-HEALTHY
Any failed gate → BLOCKED or ROLLBACK
```

| Gate | Required evidence |
| --- | --- |
| Artifact | Commit, immutable digest, provenance; signing/SBOM when policy requires |
| Test evidence | Applicable Stage 5–9 gates from §9 passed against the named commit or artifact digest |
| Preflight | Config/schema, contract compatibility, migration reversibility, secrets, IAM and capacity checked before mutation |
| Promotion | Same digest as verified; protected approval when required; one deployment owns the target environment |
| Rollout | Atomic, blue/green, or canary strategy with explicit health thresholds |
| Verification | Bounded window checks health, error rate, latency and availability; breach triggers automatic rollback |
| Record and handoff | Immutable release record names artifact, checks, outcome, rollback result and operational owner |

The skill's boundary ends at `DEPLOYED-HEALTHY`, when the verification window
passes and the named operational owner accepts the handoff.

---

## 9. Verification Gates

Verification is a staged evidence system, not a single `test` job. Place each
check at the earliest stage capable of detecting its defect, following
`defect-shift-left`. Every applicable check is blocking. A pipeline may mark a
check not applicable only when it records the component or risk evidence that
justifies the omission.

| Stage / trigger | Required verification | Gate behavior |
| --- | --- | --- |
| **Build / every PR** | Format and lint; strict type-check; build/package; secret scan; SAST; dependency/CVE and license audit; IaC scan when IaC exists; bundle/artifact budget | Block merge; branch protection requires the full-repository CI backstop |
| **Unit / every PR** | Unit and property tests; project-owned coverage policy with no unexplained regression | Block merge; publish machine-readable results and coverage evidence |
| **Integration / every PR** | Component/integration tests; API/schema contract and backward-compatibility tests; authorization negative-path tests; container/artifact reproducibility | Block merge; test the same output that becomes the immutable artifact |
| **Preview / every deployable PR** | Startup smoke; critical-journey E2E; supported-browser compatibility; visual regression where rendered UI is material; broken-link validation for navigable content | Block merge and promotion; run against the isolated preview using the candidate artifact |
| **Frontend preview / applicable routes** | Bundle/resource budgets; Lighthouse performance, accessibility, best-practices, and SEO assertions as applicable; dedicated automated accessibility rules | Block merge on breached budgets or new violations; test representative public and authenticated routes under declared mobile/desktop profiles |
| **Pre-deploy / every target environment** | Config/schema and feature-flag consistency; secret presence/expiry; migration dry-run and reversibility; deployed-contract diff; IAM/capacity/quota/cost projection; rollback-artifact availability | Abort before mutation; attach results to the release record |
| **Deploy execution / every deployment** | Startup, readiness, dependency-connectivity, health, and rollback-trigger verification | Withhold traffic or roll back automatically on failure |
| **Canary/staging / promotion and scheduled** | Performance regression, load/stress/soak as risk requires; resilience/fault-injection; rollback drill; backup-restore verification for stateful systems | Block promotion on threshold breach; expensive suites may be scheduled, but their evidence must be fresh enough for the release policy |
| **Production / bounded verification window** | Health, availability, latency, error rate, saturation, and critical synthetic journeys | Roll back automatically on threshold breach; otherwise advance to `DEPLOYED-HEALTHY` |

### Frontend Quality Rules

- Run Lighthouse against the deployed preview, never only against a local dev
  server; record the URL, profile, thresholds, report, commit, and artifact
  digest
- Select representative route classes instead of auditing only the home page:
  public landing/content, authenticated application, and the most important
  user journey where present
- Treat Lighthouse accessibility as a fast automated gate, not proof of
  accessibility conformance; keep a dedicated automated ruleset and a recorded
  manual/semi-automated review policy for checks automation cannot decide
- Calibrate performance budgets to stable CI runners and declared profiles;
  do not turn a real regression into a non-blocking warning to avoid flakiness
- Run SEO assertions only for pages intended for indexing; authenticated and
  explicitly non-indexed routes must record that exclusion

### Gate Evidence Contract

Each gate declares and records:

```
Check:          <category and command/tool>
Stage/trigger:  <PR | preview | pre-deploy | deploy | canary | production>
Scope:          <components, routes, contracts, or environment>
Artifact:       <commit and immutable digest>
Policy:         <threshold, baseline, compatibility rule, or expected result>
Result:         <pass | fail | not-applicable + evidence>
Report:         <durable artifact or log reference>
Failure action: <block merge | abort deploy | withhold traffic | rollback>
Owner:          <team or operational owner>
```

Do not run every expensive test on every commit. Fast deterministic checks
block the PR; environment-dependent checks block preview or promotion; costly
load, soak, resilience, and restore suites run on a risk-based schedule and
must satisfy the release's evidence-freshness policy.

---

## 10. Delivery Checklist

### CRITICAL (Must-Have)

- [ ] **Idempotency**: converges to the same desired state if skipped, run once,
      or retried
- [ ] **Timeouts**: All long-running steps have explicit timeout values
- [ ] **Immutable artifacts**: Build once, promote same artifact; config
      injected at deploy time
- [ ] **Build in CI, not in the deploy platform**: every build runs as a
      dedicated fail-fast CI step; deploy action receives a pre-built artifact
      (no reliance on Oryx/Buildpacks/Vercel auto-build)
- [ ] **Secrets**: OIDC/federated identity for cloud auth; no standing cloud
      credentials
- [ ] **Static quality gates**: format/lint, strict type-check, build, secret
      scan, SAST, dependency/CVE, license, and applicable IaC checks block merge
- [ ] **Unit and property tests**: results and coverage policy block merge
- [ ] **Integration and contract tests**: boundaries, compatibility,
      authorization negative paths, and candidate artifact verified
- [ ] **Health check**: Post-deploy validation present; rollback on failure
- [ ] **Preview verification**: smoke, critical E2E, supported browsers, and
      applicable visual/link checks block merge via branch protection
- [ ] **Frontend quality**: applicable representative routes have bundle,
      Lighthouse, and dedicated automated accessibility gates
- [ ] **Pre-deploy tests**: config, migration, contract, secret, feature-flag,
      IAM/capacity, and rollback-artifact checks abort before mutation
- [ ] **Scheduled risk tests**: applicable load/soak, resilience, rollback, and
      restore evidence satisfies the release's freshness policy
- [ ] **Preview environments**: All deployments use isolated preview; production
      promoted atomically
- [ ] **PR concurrency**: Cancel-in-progress enabled; only the latest commit
      deploys
- [ ] **Release evidence**: Artifact digest/provenance and preflight results recorded
- [ ] **Test evidence**: Every gate records scope, policy, artifact, result,
      report, failure action, and owner; exclusions include evidence
- [ ] **Production verification**: Bounded signal window with automatic rollback
- [ ] **Owner handoff**: Operational owner named before `DEPLOYED-HEALTHY`

### ADVANCED (Nice-to-Have)

- [ ] API backward-compatibility: additive changes only for tolerant readers;
      version breaking changes; deprecation
      documented
- [ ] IaC migration: declarative infrastructure for resources managed at scale
- [ ] DB migrations: Expand/Contract pattern for schema changes (multi-tenant)
- [ ] Secret rotation audit: quarterly seed secret rotation logged

## 11. Output Contract

When applying this skill, emit a coder-facing pipeline decision record:

```
Scope:          <workflow / job / environment / deploy path>
Decision:       Proceed | Block | Add gate | Split job | Make idempotent | Promote | Rollback | Remove secret
Risk:           <idempotency | timeout | mutable artifact | deploy-build | secret | static-quality | unit | integration | contract | authorization | frontend-quality | accessibility | performance | migration | health-check | e2e | resilience | restore | concurrency | IaC | provenance | preflight | rollout | production-verification | handoff>
Artifact:       <commit, digest, provenance>
Release state:  <BUILD-VERIFIED | RELEASE-READY | DEPLOYING | PRODUCTION-VERIFYING | DEPLOYED-HEALTHY | BLOCKED | ROLLBACK>
Test evidence:  <applicable gates, reports, exclusions, and results>
Preflight:      <checks and results>
Rollout:        <strategy and health thresholds>
Rollback:       <trigger, known-good artifact, result>
Owner handoff:  <operational owner or missing>
Evidence:       <workflow file, command, log, branch rule, secret path, or deployment behavior checked>
Verification:   <window, signals, outcome / local command / dry run / Not run + reason>
Next action:    <specific workflow edit, test, policy, or owner question>
```

## 12. See also

- **`defect-shift-left`** — where each pipeline check belongs on the stage ladder.
- **`system-optimization`** — value-stream optimization built on top of a reliable pipeline.
- **`architecture-guidelines`** — first-principles rules out of scope here (idempotency etc. as system-level concerns).
