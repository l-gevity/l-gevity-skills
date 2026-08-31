# Sample reports — verification artifact

Five reports produced using the rewritten emit templates. Each must be
readable without consulting the internal structural axis symbols or
morphogenetic mechanism-transfer model. Used to satisfy Verification gate 1
from the reporting-vocabulary translation plan.

---

## (a) Prospective complexity report — new abstraction

**Scenario.** A `billing/rate-limiter` component is being introduced. Three
existing components (`billing/gateway`, `billing/cache-front`, `billing/config-loader`)
currently each implement ad-hoc throttling. The refactor extracts a shared
rate-limiter all three will use.

```
Subject:              billing/rate-limiter — extract shared throttling
Decision:             Proceed
Component-kinds Δ:    +1     (RateLimiter is a new component type; 3 concrete callers identified)
Dependency-edges Δ:   +3     (RateLimiter ↔ Gateway, Cache-Front, Config-Loader; replaces 3 ad-hoc paths)
Max-chain-depth Δ:    +1     (callers now route through one extra hop)
Module-count Δ:       +2     (rate-limiter/ and rate-limiter-tests/)
Cycle:                Pass
Non-structural gates: Pass
Trade-off:            §6 row "Add abstraction tier — ≥3 concrete instances" — Proceed (§7a Conformance)
Rationale:            Three named concrete callers satisfy the Rule of Three.
                      The +1 chain-hop is the cost of the shared abstraction;
                      the dependency-edge net is unchanged (3 ad-hoc edges
                      collapse into 3 shared edges).
Next action:          Extract shared component and wire the three callers.
Verification:         Run unit tests for the three callers and architecture lint.
```

---

## (b) Retrospective audit report — module under review for removal

**Scenario.** Audit of `core/plugin-registry/` — a generic registry built six
months ago "to support future plugin types." The single current registration
is the email-template plugin, which is loaded statically at boot.

```
Subject:              core/plugin-registry — retrospective audit
Decision:             DELETE
Component-kinds Δ:    -1     (PluginRegistry type removed; no second concrete plugin ever landed)
Dependency-edges Δ:   -4     (registry ↔ boot, email-template, type-registry, manifest-loader)
Max-chain-depth Δ:    -2     (boot → registry → manifest-loader → plugin collapses to boot → plugin)
Module-count Δ:       -3     (plugin-registry/, plugin-registry-tests/, manifest-loader/)
Cycle:                Pass
Non-structural gates: Pass
Trade-off:            §1 (necessity) — generality without instantiation; Rule of Three not met after 6 months
Rationale:            One registered plugin in six months; no second instance
                      named or probable. Inlining the email-template
                      registration removes one component-type and three
                      modules with no caller-visible behavior change.
Next action:          Inline the email-template registration and delete registry files/tests after callers pass.
Verification:         Run caller tests and architecture lint after deletion.
```

---

## (c) Placement report — new component, morphogenetic topology

**Scenario.** A new `auth-token-validator` component is being introduced.
It verifies signed bearer tokens for inbound HTTP requests in the
`identity` domain.

```
Subject:             identity/auth-token-validator
Mode:                Design
Analysis mode:       Rapid
Selection reason:    One bounded component placement with proposed static
                     edges and no restructuring candidate.
Decision:            PLACE
Declared topology:   identity / primitive / infrastructure
                     Inbound: identity/request-middleware, identity/admin-gateway
                     Outbound: identity/key-store, identity/clock
Position legality:   Pass — every edge stays inside the identity domain;
                     layer and tier steps are within one.
Static cycle:        Pass — all static edges point toward declared callees
Runtime cycles:      none
Observed fields:     Static = proposed edges checked
                     Runtime / change / data / failure = Not measured
Boundary evidence:   Token verification belongs to identity; proposed callers
                     and callees remain within the identity boundary.
Enforcement:         add architecture rule: forbid auth-token-validator ->
                     billing/*, orders/*, and undeclared infrastructure
Next action:         Add the component and its inbound interface at
                     identity / primitive / infrastructure.
Verification:        Run architecture lint and focused identity tests.
```

---

## (d) Escalated topology report — boundary restructuring

**Scenario.** A Rapid audit of `checkout-orchestrator` finds two named
responsibilities and separate static edge clusters. SPLIT becomes a candidate,
so the analysis escalates to Full; Full then evaluates domain ownership,
co-change, and the measured Gate 4 deltas before acceptance.

```
Subject:             commerce/checkout-orchestrator
Mode:                Audit
Analysis mode:       Rapid → Full
Selection reason:    SPLIT became a candidate after the bounded scan exposed
                     separate payment and shipment responsibilities and edges.
Decision:            SPLIT
Declared topology:   commerce/checkout / orchestrator / application
                     Inbound: checkout/submit-order
                     Outbound: payments/authorize, shipping/reserve
Position legality:   Pass — both outbound edges use the target domains'
                     declared inbound interfaces; no layer or tier step
                     exceeds one.
Observed fields:     Static = two edge clusters through separate domain APIs
                     Change = held-out 20-merge window inspected after the
                     second-candidate record; 18/20 edits touched one cluster
                     Runtime / data / failure = Not measured
Decision policy:     Change affinity — baseline = 20 merged changes;
                     accept independent cluster when >= 80% of edits remain
                     cluster-local; sensitivity = threshold ± 10%.
Graph analysis:      Not required — no algorithmic cut generated the candidate.
Candidate baseline:  Split the orchestrator into payment and shipment
                     coordinators along the declared domain responsibilities.
Second candidate:    Exposed risk (natural lens — segmentation): a split
                     without one symmetric checkout entry contract permits
                     direct payment-to-shipment peer crossings. Rejection
                     condition, named before the held-out window was opened:
                     more than 20% of the 20-merge window needing both
                     clusters. Observed 2/20, so the contribution is retained
                     and shapes the enforcement rule. A manual layer cut was
                     also attempted and produced nothing distinct: edits
                     inside each cluster cross the application/infrastructure
                     line, so it leaves both change reasons in one component.
Static cycle:        Pass
Runtime cycles:      none observed
Boundary evidence:   Payment authorization and shipment reservation have
                     separate domain owners; 90% cluster-local change exceeds
                     the predeclared 80% threshold.
Reversibility:       medium — several internal callers share the checkout
                     contract; the retained facade is the reversal path.
Prediction:          Cluster-local change stays >= 80% over the next 20
                     merges after the split; window close re-enters Audit on
                     commerce/checkout.
Enforcement:         add architecture rule: checkout entry may depend on the
                     two new inbound interfaces, not their internals
Measurement:         Proceed — Component-kinds Δ=0; Dependency-edges Δ=-2;
                     Max-chain-depth Δ=0; Module-count Δ=+1; non-structural
                     gates pass.
Next action:         Split the orchestrator along the two accepted
                     responsibilities and retain one checkout entry facade.
Verification:        Run architecture lint, checkout contract tests, and
                     recompute the static graph after the split.
```

---

## (e) Probationary acceptance report — evidence-poor young service

**Scenario.** A six-week-old `notifications` service routes dispatch directly
at its schedule store. INTRODUCE-BOUNDARY becomes a candidate, so the analysis
escalates to Full. The service has not yet accumulated the declared 20-merge
window and carries no tracing, so the deciding change-affinity field cannot be
measured within the decision window.

```
Subject:             notifications/scheduling-contract
Mode:                Design
Analysis mode:       Rapid → Full
Selection reason:    INTRODUCE-BOUNDARY became a candidate, which Rapid may
                     not finalize.
Decision:            INTRODUCE-BOUNDARY
Declared topology:   notifications / capability / application
                     Inbound: notifications/dispatcher
                     Outbound: notifications/schedule-store, platform/clock
Position legality:   Fail: cross-domain coupling — notifications/dispatcher
                     reaches notifications/schedule-store outside any
                     declared contract. The proposed boundary resolves it.
Observed fields:     Static = full import graph checked; dispatcher reaches
                     the schedule store directly
                     Change = Not measured — the service has 7 merges
                     against a declared 20-merge window, and no earlier
                     history exists to derive one from
                     Runtime / data / failure = Not measured — no tracing
                     and no schema telemetry are deployed
Decision policy:     Hard invariant — dispatcher must reach the schedule
                     store only through a declared contract. Change affinity —
                     baseline = 20 merged changes; accept independent clusters
                     when >= 80% of edits remain cluster-local; window = 20
                     merges; sensitivity = threshold ± 10%.
Graph analysis:      Not required — no algorithmic cut generated the candidate.
Candidate baseline:  Put one scheduling contract between dispatcher and
                     schedule-store and keep both behind it.
Second candidate:    none — algorithmic cut: attempted, no weighted graph
                     exists at this history depth and the analyzer returns
                     NOT_EVALUATED; natural lens: attempted, the Operational
                     Lens Index returns no mechanism for a two-node contract
                     placement; manual alternative decomposition: attempted,
                     a layer cut falls on the same edge as the baseline, so
                     it is not distinct.
Static cycle:        Pass — dispatcher → scheduling contract → schedule-store
Runtime cycles:      none
Boundary evidence:   probationary — scheduling and dispatch have separate
                     owners and separate retry semantics; change affinity
                     cannot be measured because the service has 7 of the
                     declared 20 merges and no earlier history exists to
                     derive; expiry at merge 20; instrumentation: enable the
                     co-change report on notifications/*; reversal path: the
                     contract is internal to notifications and collapses
                     back into the dispatcher.
Reversibility:       medium — three internal dispatcher call sites share the
                     new contract; collapsing it is the named reversal path.
Prediction:          Cluster-local change reaches >= 80% over merges 1–20 after
                     the contract lands; window close re-enters Audit on
                     notifications/*.
Enforcement:         add architecture rule: forbid notifications/dispatcher ->
                     notifications/schedule-store
Measurement:         Proceed — Component-kinds Δ=+1; Dependency-edges Δ=0;
                     Max-chain-depth Δ=+1; Module-count Δ=0; non-structural
                     gates pass.
Next action:         Add the scheduling contract, enable the co-change report,
                     and promote the new architecture rule from warn to error
                     once its violations clear.
Verification:        Run architecture lint, dispatcher contract tests, and the
                     scheduled declared-vs-observed comparison at expiry.
```

---

## Coder read — pass criterion

A reader who has never opened the internal model (`structural-simplification`
§§1–7 or `morphogenetic-architecture` §§1–3) should be able to, for each of
the five reports:

1. State what each labelled field means (e.g. "Component-kinds Δ = how
   many new component types were added; positive means more diversity").
2. Decide whether the decision follows from the deltas.

If any field requires consulting §1 of either skill to interpret, that
field name fails and gets rewritten. The five reports above are the
canonical artifacts for that test — any future edit to the emit
templates should produce the same five reports and re-pass the test.
