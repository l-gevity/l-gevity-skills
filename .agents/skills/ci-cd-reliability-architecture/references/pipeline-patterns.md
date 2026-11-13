# CI/CD Reliability Architecture — Pipeline Patterns

Platform-neutral pseudocode for the shapes [SKILL.md](../SKILL.md)
requires. Translate keys to the target CI system; never copy verbatim.
Section numbers refer to SKILL.md.

## Self-contained job (SKILL.md §2)

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

## Self-healing steps (SKILL.md §4)

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

## Zero-knowledge secrets (SKILL.md §6)

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

## Replacement pattern (SKILL.md §7)

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

## Destructive-change gate (SKILL.md §7)

Run the same gate twice: in the pull request, where its output is posted for
the reviewer, and in the deploy job immediately before mutation, against the
live environment. Mark state-holding resources by a tag or label the gate
reads (for example `state=holds-data`); a hardcoded type list goes stale when
a new resource type arrives.

| Tool | Effect preview | Deletion or replacement | Orphan signal | Deletion protection |
| --- | --- | --- | --- | --- |
| Terraform / OpenTofu | `plan -out=tfplan`, then `show -json tfplan` | `resource_changes[].change.actions` contains `delete` | a `create` of a state-holding type in the same plan as its `delete` | `lifecycle { prevent_destroy = true }`; provider flags such as `deletion_protection` |
| Bicep / ARM | `az deployment group what-if --no-pretty-print` | `changeType` is `Delete` | a `Create` of a state-holding type while one of that type shows `Ignore` (left out of the template, kept by incremental mode) | `CanNotDelete` resource lock; the deploy identity lacks `Microsoft.Authorization/locks/delete` |
| Pulumi | `pulumi preview --json` | `steps[].op` is `delete`, `replace`, or `delete-replaced` | a `create` of a state-holding type beside a resource the program dropped | `protect: true` resource option |
| CloudFormation | change set, `describe-change-set` | `Action: Remove`, or `Replacement: True` | a new logical ID for a state-holding type | `DeletionPolicy: Retain`; stack termination protection |

`prevent_destroy` guards only while its block stays in the configuration:
deleting the resource and the block in one change removes the guard with it.
That is why the plan gate reads the effect rather than trusting the guard.

```bash
# Pseudocode: fail the job on an unreleased destructive change.
preview_json > effect.json                      # tool-specific command above
destructive=$(select_state_holding_deletions_replacements_and_orphans effect.json)
released=$(cat infra/released-deletions.txt 2>/dev/null)   # same change, one resource ID per line
unreleased=$(comm -23 <(echo "$destructive" | sort) <(echo "$released" | sort))
if [ -n "$unreleased" ]; then
  echo "Unreleased destructive change to a state-holding resource:"
  echo "$unreleased"
  exit 1
fi
```

**Rules:**

- The deploy-job run is not optional when a review-time run exists: approval
  covers the environment as it was then, not as it is now
- Where the tool saves a plan, apply that plan file, and fail when it is
  stale; where it cannot (what-if), the deploy-time run is the only guard
- A release lists resource identities, never a wildcard or a type
- Fail too when the release names a resource the preview does not delete,
  replace, or orphan: a stale release is a standing exception
