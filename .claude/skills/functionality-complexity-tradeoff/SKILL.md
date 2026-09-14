---
name: functionality-complexity-tradeoff
description: >-
    Decides whether functionality solves a real problem and is worth its
    complexity cost. Use in prospective mode to build, defer, or drop proposed
    capabilities, and in retrospective mode to keep, simplify, deprecate,
    delete, or mark existing code obsolete. Trigger for feature triage,
    backlog grooming, PR scope review, dead-code audits, tech-debt reviews,
    "is this worth it?", "should we remove this?", "is this defensive check
    necessary?", and cases involving impossible-state guards, redundant
    validation, cargo-culted patterns, phantom requirements, requirement-pinned
    mechanism, or unused
    generality, and evidence-driven revisits of outcome hypotheses after release.
---

# Functionality pruner

> This skill governs **decisions about whether functionality justifies its
> existence**. It runs in two stages: a **necessity gate** (does the problem
> this code addresses actually occur in this context?) followed by a **worth
> ledger** (does the value justify the cost?). It applies equally to
> unimplemented features (accept / reject / minimize) and to existing code
> (keep / simplify / delete / remove-as-obsolete). For measuring complexity
> itself, see `structural-simplification`. For the upstream principles
> (YAGNI, scope control, proportional solutions), see `architecture-guidelines`.

> **Core Directives**
>
> 1. **Necessity precedes worth.** Before scoring value and cost, verify the
>    problem the code addresses can actually occur in this context. Code
>    guarding against architecturally impossible states has no product value
>    for that failure mode. Skip the worth ledger and emit OBSOLETE unless the
>    code is serving as the canonical executable invariant (§1c).
> 2. **Separate the ledger.** Value and cost are distinct axes. Score each
>    independently; never collapse into a single number.
> 3. **Cost compounds, value decays.** Value is realized per use; cost accrues
>    on every future change, test run, review, and incident. Always evaluate
>    over the feature's expected lifetime.
> 4. **The default is No.** If worth is not clearly positive, reject or
>    minimize. **YAGNI is the null hypothesis.**
> 5. **Build and audit share a model.** The same axes apply whether deciding
>    what to add or what to remove. A feature that would fail as a proposal
>    today should fail as existing code today.
> 6. **Remove over refactor, refactor over rewrite.** A retrospective audit
>    that finds negative worth — or that fails the necessity gate — prefers
>    safe removal or deprecation to elaborate justification. Removal still
>    follows migration, rollback, and compatibility constraints.
> 7. **Outcome evidence informs worth; it is not the verdict.** Consume current
>    linked outcome evidence when available. Completion, deployment, or adoption
>    alone cannot prove downstream value, and no hypothesis state automatically
>    dictates a worth decision.

---

## 1. The Necessity Gate

The Worth Model (§2) assumes the code under review is solving a real problem.
Before scoring V and C, confirm that the problem itself exists in this stack.
If it does not, the worth ledger does not apply: emit **OBSOLETE** in
retrospective mode, or **DROP** with a necessity-failure rationale in
prospective mode. For retrospective removals, apply the safety constraints in
§7b before changing code.

> [!IMPORTANT] A monorepo single-page application deployed as one artifact
> cannot run client and server at different versions; a "client version check"
> in that stack guards against an impossible state. It has no V for that
> failure mode — not low V — because the failure mode it prevents cannot occur.
> Worth scoring would
> mis-classify this as low-V / low-C "DEFER" or "KEEP." The necessity gate
> catches it.

### 1a. Categories of non-problem-solving code

| Category                          | Definition                                                                                  | Typical example                                                                                                                                                                    |
| --------------------------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Impossible-state guard**        | Defends against a state ruled out by deployment topology, type system, or runtime invariant | Client/server version skew in a single-artifact SWA; null-guard on a non-nullable type; race-condition mutex in a single-threaded executor; retry loop on a deterministic in-process call |
| **Already-defended-elsewhere**    | Aspect fully owned by a different layer, duplicated here                                    | XSS-escaping atop a templating engine that already escapes; manual rollback inside an outer transaction; CSRF token on an idempotent GET; HTTPS-upgrade logic when the load balancer terminates TLS |
| **Cargo-culted pattern**          | Pattern whose prerequisites do not hold in this context                                     | Connection pool in a CLI that exits in 200 ms; singleton in a stateless lambda; client-side request dedupe against an idempotent endpoint; back-compat shim for a client class that no longer exists |
| **Phantom requirement**           | Solves a requirement that was never real or has lapsed                                      | Feature flag for a completed launch; A/B branch after the experiment concluded; migration code that has provably run on every record                                              |
| **Generality without instantiation** | Abstraction whose anticipated variation never materialized                               | Strategy pattern with one strategy; plugin interface with one implementation; config key that has held one value across all environments for the feature's lifetime              |
| **Logically dead branch**         | Branch unreachable given upstream contracts                                                 | `if (!user.id)` after auth middleware that guarantees it; `try/catch` around statically non-throwing code; default values for parameters callers always populate                  |

### 1b. Detection heuristics

Run these BEFORE scoring V or C. A high-confidence positive result routes the
verdict to OBSOLETE (retrospective) or DROP-as-non-problem (prospective),
subject to the invariant-documentation and load-bearing exceptions in §§1c/8e.

| Heuristic                        | Signal                                                                                                                                                                                                              | Catches                                            |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| **Invariant audit**              | List the invariants the architecture, type system, deployment topology, and trust boundary maintain. List the conditions the code branches on. Branches that contradict an invariant are dead.                     | Impossible-state guards, dead branches             |
| **Trigger reachability**         | Construct a concrete real-world sequence that activates the code without violating an architectural invariant. Failure to construct one after checking callers, entry points, tests, and runtime paths is a positive finding. | Impossible-state guards, dead branches             |
| **Origin archaeology**           | Pull the introducing commit / PR / ADR. Verify the rationale's premises still hold (dependency present, platform supported, client class extant, migration incomplete). Lapsed premises mean the code is obsolete. | Phantom requirements                               |
| **Aspect-owner map**             | For each aspect (auth, escaping, retry, validation, caching), name the single owner of its mechanism — a subsystem of this system, or a layer beneath it (framework, middleware, platform, network). Other subsystems performing the same job are redundant or signal a missing trust boundary. An aspect has one obligation and one mechanism; per-subsystem copies of the mechanism are SIMPLIFY candidates in Retrospective mode. | Already-defended-elsewhere                         |
| **Pattern-prerequisite check**   | For each recognizable pattern, list its prerequisites (long-lived process, mutable shared state, non-idempotent dependency, multiple implementations). Prerequisites that do not hold here mean the pattern is cargo-culted. | Cargo-culted patterns                          |
| **One-value config**             | A flag, env var, or config key that has held one value across all environments for the feature's lifetime is a dead-seam candidate. Either inline the value or document the concrete second value, compliance requirement, or pending rollout that keeps it alive. | Generality without instantiation, phantom reqs.    |
| **Zero-everything signature**    | Production code with zero telemetry hits AND zero bug history AND zero recent edits is not necessarily "stable" — it may have never run. Combine with the invariant audit to distinguish load-bearing-but-quiet from guarding-the-impossible. | Impossible-state guards                |

> [!IMPORTANT] **The invariant audit is the highest-yield necessity check.**
> Most non-problem-solving code is defending against violations of invariants
> the surrounding stack already guarantees. Enumerate those invariants
> explicitly before reading the code, then walk the branches with the list in
> hand.

### 1c. Necessity findings that are not deletions

> [!WARNING] Some "impossible-state" code is *documenting* an invariant rather
> than *enforcing* one — an `assert version_match` whose purpose is to fail
> loudly if a future contributor changes the deployment topology. That has
> small but real value as machine-checkable documentation. The fix is usually
> to convert it to a comment, an ADR reference, a build-time check, or a test
> — not silent deletion. If the code is the canonical record of an invariant
> nothing else captures, **SIMPLIFY** (downgrade to documentation) rather
> than **OBSOLETE**.

Inverse failure mode: see §8e. Some complexity that *resembles* cargo-culting
or over-engineering is in fact load-bearing because the simple version was
measured to be too slow, too unsafe, or too fragile. Read the original
rationale before voting OBSOLETE on anything that merely *looks* like a
non-problem.

### 1d. Necessity vs. low worth

The distinction matters for the audit record.

| Verdict      | Rationale                                                            | Future re-litigation risk                                              |
| ------------ | -------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **OBSOLETE** | "The problem this code addresses cannot occur in this stack."        | Low — the rationale is structural; only an architecture change reopens it. |
| **DELETE**   | "The value does not justify the cost."                               | Higher — priorities or cost shift and the case reopens.                |

Record the distinction so a later audit does not reintroduce the same code
under new conditions. "We removed the client version check because it cost
more than it returned" invites debate about thresholds; "we removed it
because client/server version skew cannot occur in a single-artifact deploy"
closes the question.

### 1e. Obligation vs. mechanism

A subject can pass the necessity gate — the problem is real — while its
*grain* is still inflated by mechanism nobody demanded. Before scoring worth,
restate each requirement behind the subject in two parts:

- **Obligation** — the outcome, evidence, or restriction that must exist
  (a record with actor/time, a gate before a step, an actor limitation).
- **Mechanism** — the specific rights, roles, endpoints, record types, or
  protocols the requirement text or the implementation chose to satisfy it.

Mechanism the obligation does not force is a SIMPLIFY candidate even when the
functionality itself is KEEP. Audit in two passes: first within the current
requirements to establish the floor, then treat careful requirement edits as
prospective candidates scored on this same ledger. Flag edits with real
external trade-offs (consent models, public intake, protocol surfaces) as
explicit product decisions rather than deciding them silently, and route
changes of requirement *meaning* through `requirements-grounding`. Three
floors are never negotiable: legal/regulatory obligations, separation-of-duties
(second-person) controls, and external protocol surfaces others depend on.

Typical yields: an actor condition encoded as a dedicated right or role where
a membership attribute or workflow-state gate satisfies the same acceptance
criterion; a person-split where the obligation only demands recorded evidence
before the next step; one endpoint per read projection of an aggregate the
caller already fetches.

---

## 2. The Worth Model

Once the necessity gate (§1) passes, the question becomes: does the value
delivered justify the cost imposed? Worth is the relation between **Value
(V)** delivered and **Cost (C)** imposed over lifetime `L`. Both sides are
multi-dimensional.

### Value axes

| Axis                 | Symbol | What it measures                                                             | Measurability           |
| -------------------- | ------ | ---------------------------------------------------------------------------- | ----------------------- |
| **Utility**          | `U`    | Severity of the user need; what actually breaks without it                   | Judgment, user research |
| **Frequency**        | `F`    | How often the need arises per affected user per unit time                    | Measurable (telemetry)  |
| **Reach**            | `R`    | Proportion of users / flows / environments that encounter the need           | Measurable (analytics)  |
| **Irreplaceability** | `I`    | Cost of the next-best alternative (workaround, external tool, doing without) | Judgment, comparative   |

Aggregate product value ≈ `U × F × R × I`. If any axis is zero, ordinary
product value is zero; external floors, keystone cost, and safety exceptions
are handled separately in §8.

> [!IMPORTANT] A feature loved by 2% of users, used once a year, with a trivial
> workaround, has near-zero total value no matter how elegant it is. Score
> honestly — especially `R` and `F`, which are routinely inflated.

### Cost axes

Structural cost is **delegated** to `structural-simplification`: the
**Subsystem-kinds Δ, Dependency-edges Δ, Max-chain-depth Δ, Subsystem-count Δ**
introduced (prospective) or already present (retrospective). See the
Reporting Vocabulary in `structural-simplification` for the symbol mapping.
This skill adds three ongoing-cost axes that structure alone does not capture:

| Axis              | Symbol | What it measures                                                    | Measurability                          |
| ----------------- | ------ | ------------------------------------------------------------------- | -------------------------------------- |
| **Maintenance**   | `M`    | Tests, docs, reviews, dependency updates the feature demands        | Measurable (test/doc count, churn)     |
| **Risk**          | `X`    | Bug surface × blast radius; security, privacy, performance exposure | Measurable (defect history, incidents) |
| **Evolution tax** | `E`    | Degree to which the feature constrains future change                | Judgment, changelog trace              |

Aggregate cost over lifetime, in axis-symbol form (one-time structural delta
plus ongoing maintenance × lifetime):

`Aggregate cost ≈ (ΔD + ΔK + ΔP + Δn) + (M + X + E) × L`

— where `ΔD, ΔK, ΔP, Δn` are the structural deltas from `structural-simplification`
(see its Reporting Vocabulary: Subsystem-kinds Δ, Dependency-edges Δ,
Max-chain-depth Δ, Subsystem-count Δ).

### The worth inequality

```
Worth > 0   ⇔   V × L   >   C_structural + (M + X + E) × L
```

For short-lived code, the structural footprint dominates. For long-lived code,
`M + X + E` dominates. **Most production features are long-lived; plan for the
ongoing term.**

> [!WARNING] Evolution tax (`E`) is the most-underestimated axis because it is
> invisible in the current code review. It shows up later, as the PR that
> "should have been small but touched twelve files."

---

## 3. Two Modes

The model is the same; the inputs differ. **Both modes run the necessity gate
(§1) before scoring worth.**

### 3a. Prospective — evaluating proposed functionality

Applied to tickets, specs, PRDs, loose ideas, or PR scope **before
implementation**. All inputs are estimates; record confidence explicitly.

1. State the functionality in one sentence: _"This allows [who] to [do what] so
   that [outcome]."_
2. **Run the necessity gate (§1).** Confirm the failure mode addressed is
   reachable in the target stack and is not already owned by another layer.
   A prospective necessity failure is rare but consequential: it stops a
   build that would have produced dead code on day one.
3. Score `V` axes with **evidence**: user interviews, request tickets,
   analytics of the workaround, competitor behavior. Opinions are not
   evidence. Unsupported opinions are not enough evidence for high-confidence
   build decisions. Cite linked outcome hypotheses when present; before release
   they express expected value, not observed impact.
4. Score `C` axes against a **concrete implementation sketch**: files
   touched, new abstractions or dependencies introduced, tests required,
   failure modes created.
5. Apply the Decision Protocol (§6). Verdicts are prospective (§7a).

### 3b. Retrospective — auditing existing functionality

Applied to code, subsystems, features, capabilities, or flags that **already
exist**. Inputs are observable; bias toward measurement over judgment.

1. Define the boundary: files, symbols, entry points, feature flags, routes,
   or callers.
2. **Run the necessity gate (§1).** Walk the heuristics in §1b before any
   worth scoring. A positive finding short-circuits the rest of the audit
   to OBSOLETE.
3. Score `V` from usage data:
    - Telemetry hits per time window, per user cohort.
    - Reach: unique users or flows that enter this code path.
    - Irreplaceability: does an alternative path exist? Do users already use
      it?
    - **If `V` cannot be measured, that itself is a finding** — instrument,
      identify an external floor (§8c), or keep confidence Low.
    - Consume current outcome-evidence records from
      `requirements-traceability`. Preserve the canonical hypothesis version,
      cohort, threshold, window, and guardrails. `stale` or `inconclusive`
      evidence cannot support High value confidence; `rejected` evidence lowers
      the supported value claim but does not by itself prove zero value.
4. Score `C` from current observable state:
    - Structural: measure `D, K, P, n` per `structural-simplification`.
    - `M`: dedicated tests, doc pages, recent commit churn, dependency drift.
    - `X`: bug ticket history, incident postmortems, security/perf hotspot
      reports.
    - `E`: count of PRs / design docs where this feature caused scope
      expansion, workarounds, or delays.
5. Apply the Decision Protocol (§6). Verdicts are retrospective (§7b).

> [!NOTE] A retrospective audit with no telemetry available should first
> return an instrumentation task, not a verdict — **unless** the necessity
> gate has already produced a finding, in which case telemetry is not needed
> (you cannot measure usage of a code path that cannot be triggered).
> Deciding to delete a feature merely because you cannot see it being used
> is survivorship bias in reverse; deciding to remove it because the failure
> mode it guards against cannot occur is structural reasoning.

---

## 4. Heuristic Checks

Fast worth signals — usage silence, workaround in the wild, single caller,
flag defaulted off, orphan test, churn hotspot, churn × complexity, defect
clustering, bug-fix-to-feature ratio, blocked PRs, documentation rot — and the
axis each one moves. The necessity heuristics in §1b run first. Read
[references/worth-signals.md](references/worth-signals.md) when scoring `V`
or `C` in retrospective mode, and run churn × complexity before any
subjective judgment.

---

## 5. Forcing Questions

Four interrogations — necessity, value, cost, counterfactual — each exposing a
common failure mode. Answers MUST be written, not implicit. Read
[references/forcing-questions.md](references/forcing-questions.md) and answer
the necessity questions before any value scoring. A removal cost in 12 months
that exceeds the build cost today is a one-way door: apply §8 before
committing.

---

## 6. Decision Protocol

1. **Run the necessity gate** (§1). Walk the heuristics in §1b. If the code
   addresses a problem that cannot occur in this context, emit **OBSOLETE**
   (retrospective) or **DROP** with a necessity-failure rationale
   (prospective). Skip remaining steps.
2. **Score `V` axes** (`U, F, R, I`) on a 0–3 scale with one-line evidence
   per axis. When outcome evidence exists, cite its hypothesis ID, state,
   freshness, and observation identity; do not replace its threshold or
   guardrails with a more favorable interpretation.
3. **Score `C` axes**:
    - Delegate `D, K, P, n` to `structural-simplification` (deltas for
      prospective; absolute measured values for retrospective).
    - Score `M, X, E` on 0–3 with one-line evidence per axis.
4. **Record confidence** (Low / Medium / High) for each side independently.
5. **Compare across both ledgers** without summing.
6. **Classify** using the Worth Matrix (§6a) and apply the confidence gate
   (§6b).
7. **Emit** the Output Contract (§9).

### 6a. The Worth Matrix

|              | **Low C**            | **Medium C**             | **High C**       |
| ------------ | -------------------- | ------------------------ | ---------------- |
| **High V**   | BUILD / KEEP         | BUILD / KEEP             | NEGOTIATE (§8)   |
| **Medium V** | BUILD-minimal / KEEP | BUILD-minimal / SIMPLIFY | DEFER / SIMPLIFY |
| **Low V**    | DEFER / QUARANTINE   | DROP / SIMPLIFY          | DROP / DELETE    |

Read the matrix identically in both modes. Prospective verdicts are accept /
reject; retrospective verdicts are keep / simplify / delete. The matrix only
applies when the necessity gate (§1) has passed; necessity failures bypass
it entirely.

### 6b. Confidence gate

A verdict carries the confidence of its weakest input. If either `V` or `C`
confidence is **Low**:

- **Prospective** → default to DEFER. Gather evidence before committing to
  high-cost action.
- **Retrospective** → default to QUARANTINE. Add instrumentation, revisit
  after N weeks with measured data.

Do not commit to irreversible verdicts (BUILD, DELETE) on low-confidence
estimates. **OBSOLETE is exempt from the confidence gate** when the
necessity finding is itself High confidence — a structural impossibility
does not become more or less impossible with more data.

An `unmeasured`, `inconclusive`, or `stale` outcome assessment keeps the affected
value claim Low unless independent current evidence supports it. `supported`
may raise confidence only within the measured cohort, window, and guardrails.
Authoritative floors in §8c remain source-driven and do not require an empirical
outcome hypothesis.

---

## 7. Verdicts

### 7a. Prospective verdicts

| Verdict           | Meaning                                                                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **BUILD**         | Proceed as specified. Record the worth rationale; it becomes the audit baseline.                                                           |
| **BUILD-minimal** | Build the smallest increment capturing ≥80% of `V`; defer the rest with explicit revisit triggers.                                         |
| **NEGOTIATE**     | High `V`, high `C`. Reduce scope, conform to an existing pattern (§7a of `structural-simplification`), or accept debt with an expiry date. |
| **DEFER**         | `V` is unclear or evidence is thin. Document trigger conditions; revisit.                                                                  |
| **DROP**          | Does not clear the cost bar, OR fails the necessity gate (rationale: "guards against a state that cannot occur in this stack"). Record the rejection so the idea is not re-proposed without new evidence — or, for necessity failures, without a change in the stack's invariants. |

### 7b. Retrospective verdicts

| Verdict        | Meaning                                                                                                                                                                                       |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **KEEP**       | Worth is positive. Document why — the rationale prevents a future audit from deleting it blindly.                                                                                             |
| **SIMPLIFY**   | Worth is positive but `C` is inflated. Apply operations from `structural-simplification` §4. Re-score after.                                                                                  |
| **QUARANTINE** | `V` is unmeasured. Add telemetry; revisit after N weeks.                                                                                                                                       |
| **DEPRECATE**  | Marginal or negative worth; removal is non-trivial. Announce, migrate callers, remove on schedule.                                                                                            |
| **DELETE**     | Negative worth, removal is feasible. Prefer removal over patching, but migrate callers, preserve compatibility promises, and keep rollback possible. |
| **OBSOLETE**   | Necessity gate (§1) fails: the problem this code addresses cannot occur in this context. Remove or deprecate the code without scoring worth. Rationale is structural, not budgetary, so the verdict resists re-litigation. If the code documents an invariant nothing else captures, downgrade to **SIMPLIFY** instead (§1c). |

> [!WARNING] "Interesting", "clever", and "elegant" are not verdicts.
> Cleverness imposes cost but rarely contributes measurable value. If a
> reviewer's rationale reduces to "it's nice that we have this," require
> value evidence before KEEP. If it reduces to "it's defensive — just in case,"
> apply the necessity gate before defaulting to KEEP.

---

## 8. Asymmetric Trade-offs

Five cases where the Worth Matrix alone gives the wrong answer: **8a
optionality premium** (a named, probable next feature; speculative optionality
fails YAGNI), **8b irreversibility tax** (public API, persisted schema, wire
format: raise the required `V` one tier or require High confidence), **8c
regulatory / contractual / accessibility floor** (fixed-high `U` once the
external requirement is mapped to this code path), **8d keystone cost** (local
`C` that holds global complexity down; measure the whole-system deltas before
DELETE or SIMPLIFY), and **8e hot-path performance or safety** (measured,
load-bearing complexity; the inverse of the necessity gate, told apart by
whether the original rationale's premises still hold). Read
[references/asymmetric-tradeoffs.md](references/asymmetric-tradeoffs.md)
whenever the matrix returns NEGOTIATE, a floor may apply, or complexity looks
load-bearing.

---

## 9. Output Contract

Every application of this skill MUST produce a coder-facing decision record.
Keep fields concrete enough for Codex to choose the next edit, test, telemetry
task, or rejection:

```
Subject:        <feature / subsystem / ticket / path under review>
Mode:           Prospective | Retrospective
Necessity:      Pass | Fail
Necessity note: <if Fail: which §1a category, which invariant violated /
                 prerequisite missing / premise lapsed; one line.
                 If Pass and non-trivial: brief note on what made it pass.>
V scores:       U=<0-3>  F=<0-3>  R=<0-3>  I=<0-3>       (1-line evidence each; OMIT if Necessity=Fail)
C scores:       Subsystem-kinds Δ=<±n>  Dependency-edges Δ=<±n>
                Max-chain-depth Δ=<±n>  Subsystem-count Δ=<±n>   (prospective: deltas; retrospective: measured absolutes; OMIT if Necessity=Fail)
                M=<0-3>  X=<0-3>  E=<0-3>                 (1-line evidence each; OMIT if Necessity=Fail)
Confidence V:   Low | Medium | High                       (OMIT if Necessity=Fail)
Confidence C:   Low | Medium | High                       (OMIT if Necessity=Fail)
Outcome evidence: <hypothesis IDs, states, freshness, observation links, or none / not applicable>
Decision:       <BUILD | BUILD-minimal | NEGOTIATE | DEFER | DROP | KEEP | SIMPLIFY | QUARANTINE | DEPRECATE | DELETE | OBSOLETE>
Rationale:      <2–4 sentences tying scores → decision, or necessity finding → OBSOLETE>
Next action:    <build minimal increment, delete path, add telemetry, write test, update lint rule, or stop>
Verification:   <command / telemetry / caller check / Not run + reason>
Minimal alt:    <smallest increment preserving most V, if applicable>
Revisit when:   <measurable trigger or calendar date>
```

> [!IMPORTANT] `Revisit when` is **non-optional** for DEFER, QUARANTINE,
> BUILD-minimal, and DEPRECATE. Every such decision MUST have a measurable
> trigger (usage threshold, date, dependency version, adjacent feature
> shipping) or it will rot into a permanent maybe.

> [!NOTE] OBSOLETE does not require a `Revisit when`, because the trigger
> for revisiting is implicit: a change in the stack's invariants. If the
> deployment topology ever splits, the type system loosens, the upstream
> layer's guarantee is removed, or the lapsed dependency returns, the
> necessity finding becomes invalid and the case reopens automatically.

---

## 10. Common Patterns

A lookup of recurring subjects — impossible-state guards, duplicated
defenses, transplanted patterns, completed-launch flags, one-user
abstractions, "just in case" flexibility, quarterly admin tools, legacy
integrations of unknown usage, compliance paths, benchmarked optimizations —
with the verdict each typically earns and the section that decides it. Read
[references/common-patterns.md](references/common-patterns.md) to calibrate a
verdict against precedent; the pattern never replaces the ledger.

---

## 11. Composition with Sibling Skills

- **`requirements-grounding`** — owns outcome-hypothesis meaning, thresholds,
  cohorts, guardrails, and revisit intent. This skill consumes that definition;
  it does not rewrite it.
- **`requirements-traceability`** — owns measurement links, evidence state, and
  freshness for the exact hypothesis version. This skill consumes its current
  assessment and alone issues the functionality-worth verdict.
- **`structural-simplification`** — source of the complexity measurement
  (`D, K, P, n`). This skill **consumes** those deltas; it does not redefine
  them.
- **`architecture-guidelines`** — upstream principles (YAGNI, scope control,
  proportionality, deletion over patching). This skill is the applied
  protocol through which those principles bind to individual decisions. The
  necessity gate (§1) is the most direct expression of YAGNI applied to
  existing code: "you ain't gonna need it" generalizes to "you never needed
  it; the problem was never in this context."
- **`continuous-improvement`** — when this skill's verdicts repeatedly
  contradict current practice or sibling skills, that is a signal to update
  the skills themselves, not to override the verdicts case-by-case.
  Repeated OBSOLETE findings in a single area, in particular, are a signal
  to update `architecture-guidelines` with the relevant invariant so future
  contributors do not re-introduce the same non-problem-solving code.

> [!NOTE] This skill deliberately does **not** define its own complexity
> metric. Cyclomatic complexity, cognitive complexity, Halstead volume, and
> maintainability index are all input signals to the `C` side of the ledger,
> surfaced through `structural-simplification` and the churn × complexity
> heuristic. Keeping the measurement in one place preserves the
> single-source-of-truth discipline across the skill library. Likewise,
> the necessity gate (§1) does not redefine architectural invariants — it
> consumes the invariants documented in `architecture-guidelines` and the
> stack's own ADRs, and uses them as the basis for impossibility findings.
