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
    validation, cargo-culted patterns, phantom requirements, or unused
    generality.
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
| **Already-defended-elsewhere**    | Concern fully owned by a different layer, duplicated here                                   | XSS-escaping atop a templating engine that already escapes; manual rollback inside an outer transaction; CSRF token on an idempotent GET; HTTPS-upgrade logic when the load balancer terminates TLS |
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
| **Layer-responsibility map**     | For each cross-cutting concern (auth, escaping, retry, validation, caching), name the single layer that owns it. Other layers performing the same job are redundant or signal a missing trust boundary.            | Already-defended-elsewhere                         |
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
**Component-kinds Δ, Dependency-edges Δ, Max-chain-depth Δ, Module-count Δ**
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
(see its Reporting Vocabulary: Component-kinds Δ, Dependency-edges Δ,
Max-chain-depth Δ, Module-count Δ).

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
   build decisions.
4. Score `C` axes against a **concrete implementation sketch**: files
   touched, new abstractions or dependencies introduced, tests required,
   failure modes created.
5. Apply the Decision Protocol (§6). Verdicts are prospective (§7a).

### 3b. Retrospective — auditing existing functionality

Applied to code, modules, features, capabilities, or flags that **already
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

Fast signals — not substitutes for measurement. The necessity-gate
heuristics in §1b run first; the table below covers worth-related signals
that apply once necessity has passed.

| Check                        | Signal                                                            | Axis affected |
| ---------------------------- | ----------------------------------------------------------------- | ------------- |
| **Usage silence**            | No telemetry hits over a context-appropriate window → `F × R` approaches 0, unless instrumentation is absent or the path is externally required | `V`           |
| **Workaround in wild**       | Users or code already bypass this path → `I` is small             | `V`           |
| **Single caller**            | Feature referenced from one call site only → `R` is small         | `V`           |
| **Flag defaulted off**       | Feature flag has been `off` in production for months → `V ≈ 0`    | `V`           |
| **Orphan test**              | Tests exist but no one edits the code they cover → inspect whether they guard a stable contract, invariant, or obsolete feature | `V` / `M`     |
| **Churn hotspot**            | High commit frequency on these files → `M + X` are large          | `C`           |
| **Churn × complexity**       | High churn AND high cyclomatic / cognitive score → hotspot        | `C`           |
| **Defect clustering**        | Feature's code dominates recent bug tickets → `X` is large        | `C`           |
| **Bug-fix-to-feature ratio** | Most commits on this code are fixes, not improvements → `C > V`   | `C`           |
| **Blocked PRs**              | Other work routinely waits on or works around this → `E` is large | `C`           |
| **Documentation rot**        | Docs disagree with code → `M` is under-invested, `X` is hidden    | `C`           |

> [!IMPORTANT] **Churn × complexity is a strong empirical signal**
> for "code that costs more than it returns" (Tornhill, _Your Code as a Crime
> Scene_). Files that change often AND score high on cyclomatic or cognitive
> complexity are disproportionately responsible for defects and maintenance
> spend. Run this check before any subjective judgment in retrospective mode.

> [!NOTE] Usage silence and zero-everything signature look identical from
> outside. The difference: usage silence assumes the path is reachable but
> unused (low V); zero-everything signature, combined with an invariant
> audit, suggests the path is *unreachable* (failed necessity). The verdicts
> diverge — DELETE vs. OBSOLETE — and the rationales close the question with
> different durability.

---

## 5. Forcing Questions

Each question exposes a common failure mode. Answers MUST be written, not
implicit.

### Necessity interrogation

Apply BEFORE value interrogation. If any answer is "no" or "we cannot
construct one" after checking the relevant callers and runtime paths, the code
is a candidate for OBSOLETE / DROP-as-non-problem.

- **Can the failure mode this guards against actually occur** given the
  deployment topology, type system, and runtime guarantees of this stack?
- **Construct one concrete real-world sequence** that activates this code
  without violating an architectural invariant. Can you?
- **Is the concern owned by another layer** (framework, middleware, type
  system, deployment topology, network boundary)? Is that layer already
  enforcing it?
- **Do the prerequisites of the pattern this implements hold here**
  (long-lived process, multiple implementations, non-idempotent dependency,
  mutable shared state, etc.)?
- **Does the original rationale still apply**, or has the world it
  described — the dependency, the platform, the client class, the ongoing
  migration — changed?
- **If this is documenting an invariant rather than enforcing one**, is
  there a cheaper place for that documentation (comment, ADR, build-time
  check, test)?

### Value interrogation

- **Who** specifically needs this? Roles, counts, cohorts — not "users".
- **What do they do today** without it? If nothing, the value may be imagined.
- **What is the simplest alternative** that would satisfy 80% of the need?
  (CLI, config, docs, external tool, manual process, nothing at all.)
- **What evidence — not opinion** — supports the `V` estimate?
- **What is the smallest useful slice** we could ship and still claim the
  win?

### Cost interrogation

- What **new vocabulary** — concepts, abstractions, types — does this add?
  (Component-kinds Δ)
- What currently-independent parts does this **link**? (Dependency-edges Δ)
- How long is the **dependency chain** a typical change traverses once this
  exists? (Max-chain-depth Δ)
- How many tests — including error paths, edge cases, and integration —
  will this require? (`M`)
- **If this breaks, what else breaks** with it? What is the blast radius?
  (`X`)
- What future change does this make **harder, slower, or more dangerous**?
  (`E`)

### Counterfactual

- If we **delete** this in 12 months, what is the removal cost?
- If we **never build** it, what is the realistic worst outcome?
- Is there a **non-code** solution (docs, training, config, external tool,
  process change)?

> [!WARNING] If the removal cost in 12 months exceeds the build cost today,
> this is a **one-way door**. Apply §8 asymmetric trade-offs before
> committing. One-way doors demand higher `V` and greater confidence.

---

## 6. Decision Protocol

1. **Run the necessity gate** (§1). Walk the heuristics in §1b. If the code
   addresses a problem that cannot occur in this context, emit **OBSOLETE**
   (retrospective) or **DROP** with a necessity-failure rationale
   (prospective). Skip remaining steps.
2. **Score `V` axes** (`U, F, R, I`) on a 0–3 scale with one-line evidence
   per axis.
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

---

## 7. Verdicts

### 7a. Prospective verdicts

| Verdict           | Meaning                                                                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **BUILD**         | Proceed as specified. Record the worth rationale; it becomes the audit baseline.                                                           |
| **BUILD-minimal** | Build the smallest slice capturing ≥80% of `V`; defer the rest with explicit revisit triggers.                                             |
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

Cases where the Worth Matrix gives the wrong answer on its own.

### 8a. Optionality premium

A low-`V` / low-`C` feature may be worth keeping or building if it preserves
**concrete** future optionality — a known next feature whose path becomes
cheap because of it.

Test: is the next feature **named and probable**, or is the optionality
speculative? Speculative optionality fails YAGNI; the null hypothesis wins.
Note the overlap with **generality without instantiation** (§1a): an
abstraction whose anticipated variation never materialized fails both this
test and the necessity gate.

### 8b. Irreversibility tax

A feature that is hard to remove once shipped — public API, persisted
schema, user-visible behavior, wire format — must clear a higher bar.
**Raise the required `V` by one tier**, or require High confidence.

### 8c. Regulatory / contractual / accessibility floor

Some features deliver `V` that cannot be observed from usage telemetry:
audit logs, accessibility paths, legal holds, compliance records, safety
interlocks. Assign a **fixed-high `U`** regardless of `F × R`; `C` is still
measured normally. These features are kept even when "unused" when the
applicable external requirement, jurisdiction, contract, or safety case is
identified. They pass the necessity gate only after that requirement is mapped
to this code path.

### 8d. Keystone cost

Some features have high local `C` because they are the seam holding a
correct abstraction in place. Removing them would **raise global complexity**
elsewhere. Measure net **Component-kinds Δ, Dependency-edges Δ,
Max-chain-depth Δ, Module-count Δ** across the whole system before
committing to DELETE or SIMPLIFY. A local reduction that increases global
complexity is not a simplification (see `structural-simplification` Core
Directive 5).

### 8e. Hot-path performance or safety

Some complexity exists because the simple version was measured to be too
slow, too unsafe, or too fragile. `C` appears inflated but is structurally
load-bearing. The audit must read the original rationale (commit message,
ADR, benchmark) before voting SIMPLIFY.

> [!IMPORTANT] **§8e is the inverse of the necessity gate.** Necessity
> failures look load-bearing but aren't; §8e cases look cargo-culted but
> are. Origin archaeology is the shared diagnostic — the difference is
> whether the rationale's premises still hold today (necessity passes,
> §8e applies) or have lapsed (necessity fails, OBSOLETE applies). Lost
> history is not permission to remove load-bearing complexity; lapsed
> history supports removing obsolete code after the normal safety checks.

---

## 9. Output Contract

Every application of this skill MUST produce a coder-facing decision record.
Keep fields concrete enough for Codex to choose the next edit, test, telemetry
task, or rejection:

```
Subject:        <feature / module / ticket / path under review>
Mode:           Prospective | Retrospective
Necessity:      Pass | Fail
Necessity note: <if Fail: which §1a category, which invariant violated /
                 prerequisite missing / premise lapsed; one line.
                 If Pass and non-trivial: brief note on what made it pass.>
V scores:       U=<0-3>  F=<0-3>  R=<0-3>  I=<0-3>       (1-line evidence each; OMIT if Necessity=Fail)
C scores:       Component-kinds Δ=<±n>  Dependency-edges Δ=<±n>
                Max-chain-depth Δ=<±n>  Module-count Δ=<±n>      (prospective: deltas; retrospective: measured absolutes; OMIT if Necessity=Fail)
                M=<0-3>  X=<0-3>  E=<0-3>                 (1-line evidence each; OMIT if Necessity=Fail)
Confidence V:   Low | Medium | High                       (OMIT if Necessity=Fail)
Confidence C:   Low | Medium | High                       (OMIT if Necessity=Fail)
Decision:       <BUILD | BUILD-minimal | NEGOTIATE | DEFER | DROP | KEEP | SIMPLIFY | QUARANTINE | DEPRECATE | DELETE | OBSOLETE>
Rationale:      <2–4 sentences tying scores → decision, or necessity finding → OBSOLETE>
Next action:    <build minimal slice, delete path, add telemetry, write test, update lint rule, or stop>
Verification:   <command / telemetry / caller check / Not run + reason>
Minimal alt:    <smallest slice preserving most V, if applicable>
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

| Pattern                                                                       | Typical verdict                                                                       |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **Code guarding against a state ruled out by the architecture**               | **OBSOLETE — §1 impossible-state guard; SIMPLIFY if it is the only executable invariant record** |
| **Defensive check duplicating a guarantee from an upstream layer**            | **OBSOLETE — §1 already-defended-elsewhere; keep only if it covers a different trust boundary** |
| **Pattern transplanted from a stack whose prerequisites do not hold here**    | **OBSOLETE — §1 cargo-culted; or SIMPLIFY if partly load-bearing (§8e)**              |
| **Feature flag for a launch that completed**                                  | **OBSOLETE — §1 phantom requirement (preferred over DELETE for closure)**             |
| **Generic abstraction with one concrete user, no second user proposed**       | **OBSOLETE or SIMPLIFY — §1 generality without instantiation; collapse to concrete**  |
| **Branch unreachable given upstream contracts (e.g. null-guard on non-null)** | **OBSOLETE — §1 logically dead branch**                                               |
| "Just in case" flexibility                                                    | DROP — fails §8a optionality test                                                     |
| Admin-only tool used quarterly                                                | BUILD-minimal — satisfy via script or CLI, not UI                                     |
| "Power user" shortcut                                                         | NEGOTIATE — measure `R` honestly; almost always smaller than claimed                  |
| Dead code behind `off` feature flag                                           | DELETE if the flag was a real toggle that lost; OBSOLETE if the launch completed (§1) |
| Duplicate of library or framework feature                                     | OBSOLETE if the framework already runs it for the same scope; DROP / DELETE if `I` is ~0 by choice |
| Legacy integration, usage unknown                                             | QUARANTINE — instrument first, then decide (unless §1 already returns OBSOLETE)       |
| Extension point with one implementation                                       | OBSOLETE if no second implementation is named and probable; SIMPLIFY otherwise        |
| "We'll need this for feature X"                                               | DEFER — build when X is real, not before                                              |
| Stable feature that still produces bugs                                       | SIMPLIFY (churn × complexity hotspot), then re-evaluate                               |
| Feature with no docs, no tests, no telemetry                                  | QUARANTINE + add all three, or DEPRECATE — but check §1 first; it may be unreachable  |
| Compliance / audit / accessibility path                                       | KEEP when the mapped external requirement applies — §8c floor                         |
| Complex optimization with a benchmark in git                                  | KEEP unless benchmark is restaged (§8e)                                               |
| Assertion that documents an invariant nothing else captures                   | SIMPLIFY — downgrade to comment / ADR / build-time check (§1c), do not OBSOLETE       |

---

## 11. Composition with Sibling Skills

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
