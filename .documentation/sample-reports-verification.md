# Sample reports — verification artifact

Three reports produced using the rewritten emit templates. Each must be
readable without consulting the internal D/K/P/n or (X, Y, Z) model. Used
to satisfy Verification gate 1 from the reporting-vocabulary translation
plan.

---

## (a) Prospective complexity report — new abstraction

**Scenario.** A `billing/rate-limiter` component is being introduced. Three
existing components (`billing/gateway`, `billing/cache-front`, `billing/config-loader`)
currently each implement ad-hoc throttling. The refactor extracts a shared
rate-limiter all three will use.

```
Subject:              billing/rate-limiter — extract shared throttling
Component-kinds Δ:    +1     (RateLimiter is a new component type; 3 concrete callers identified)
Dependency-edges Δ:   +3     (RateLimiter ↔ Gateway, Cache-Front, Config-Loader; replaces 3 ad-hoc paths)
Max-chain-depth Δ:    +1     (callers now route through one extra hop)
Module-count Δ:       +2     (rate-limiter/ and rate-limiter-tests/)
Cycle:                Pass
Trade-off:            §6 row "Add abstraction tier — ≥3 concrete instances" — Proceed (§7a Conformance)
Verdict:              Proceed
Rationale:            Three named concrete callers satisfy the Rule of Three.
                      The +1 chain-hop is the cost of the shared abstraction;
                      the dependency-edge net is unchanged (3 ad-hoc edges
                      collapse into 3 shared edges).
Alternative:          —
```

---

## (b) Retrospective audit report — module under review for removal

**Scenario.** Audit of `core/plugin-registry/` — a generic registry built six
months ago "to support future plugin types." The single current registration
is the email-template plugin, which is loaded statically at boot.

```
Subject:              core/plugin-registry — retrospective audit
Component-kinds Δ:    -1     (PluginRegistry type removed; no second concrete plugin ever landed)
Dependency-edges Δ:   -4     (registry ↔ boot, email-template, type-registry, manifest-loader)
Max-chain-depth Δ:    -2     (boot → registry → manifest-loader → plugin collapses to boot → plugin)
Module-count Δ:       -3     (plugin-registry/, plugin-registry-tests/, manifest-loader/)
Cycle:                Pass
Trade-off:            §1 (necessity) — generality without instantiation; Rule of Three not met after 6 months
Verdict:              DELETE
Rationale:            One registered plugin in six months; no second instance
                      named or probable. Inlining the email-template
                      registration removes one component-type and three
                      modules with no caller-visible behavior change.
Alternative:          —
```

---

## (c) Placement report — new component, geometric placement

**Scenario.** A new `auth-token-validator` component is being introduced.
It verifies signed bearer tokens for inbound HTTP requests in the
`identity` domain.

```
Subject:              identity/auth-token-validator — placement
Position:             Domain = identity
                      Abstraction tier = primitive (no orchestration; pure verification)
                      Layer = infrastructure (consumed by request-middleware one layer above)
Inbound interface:    Called by identity/request-middleware (caller, one tier up)
                      Called by identity/admin-gateway (peer; same tier, same domain)
Outbound interface:   identity/key-store (callee, one tier down)
                      identity/clock (callee, one tier down)
Forbidden edges:      No cross-domain imports (must not reach billing/, orders/, etc.)
                      No layer-skip from request-middleware directly to key-store
                      (must traverse auth-token-validator)
Cycle risk:           None — placement is strictly below request-middleware
                      and strictly above key-store; no back-edges possible.
Verdict:              Placement valid.
Rationale:            Three callers identified (request-middleware,
                      admin-gateway, batch-job-runner — last two are peers);
                      two callees (key-store, clock) — both already exist at
                      the infrastructure layer. Component fills an existing
                      Domain/Tier/Layer slot rather than creating a new one.
```

---

## Stranger-architect read — pass criterion

A reader who has never opened the internal model (`structural-simplification`
§§1–7 or `geometric-architecture` §§1–2) should be able to, for each of
the three reports:

1. State what each labelled field means (e.g. "Component-kinds Δ = how
   many new component types were added; positive means more diversity").
2. Decide whether the verdict follows from the deltas.

If any field requires consulting §1 of either skill to interpret, that
field name fails and gets rewritten. The three reports above are the
canonical artifacts for that test — any future edit to the emit
templates should produce the same three reports and re-pass the test.
