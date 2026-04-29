---
name: functionality-complexity-tradeoff
description:
    A first-principles framework for deciding whether a piece of functionality
    is worth its complexity cost. Applies to two modes: prospective (should we
    build this?) and retrospective (should we keep this existing code?). Use
    this skill when evaluating whether to build, defer, drop, keep, simplify,
    or delete a capability — weighing value delivered against maintenance,
    bug surface, and evolution tax. Trigger whenever the user asks "is this
    worth building?", "should we remove this code?", "is this complexity
    justified?", or is otherwise weighing scope against engineering cost —
    including feature triage, backlog grooming, tech-debt reviews, PR scope
    pushback, dead-code audits, or retrospective module reviews.
---

# Functionality–Complexity Tradeoff

> This skill governs **decisions about whether functionality justifies its
> cost**. It applies equally to unimplemented features (accept / reject /
> minimize) and to existing code (keep / simplify / delete). For measuring
> complexity itself, see `structural-simplification`. For the upstream
> principles (YAGNI, scope control, proportional solutions), see
> `architectural-guideline`. For changes to code produced by a SIMPLIFY or
> DELETE verdict, see `coding-standard`.

> **Core Directives**
>
> 1. **Separate the ledger.** Value and cost are distinct axes. Score each
>    independently; never collapse into a single number.
> 2. **Cost compounds, value decays.** Value is realized per use; cost accrues
>    on every future change, test run, review, and incident. Always evaluate
>    over the feature's expected lifetime.
> 3. **The default is No.** If worth is not clearly positive, reject or
>    minimize. **YAGNI is the null hypothesis.**
> 4. **Build and audit share a model.** The same axes apply whether deciding
>    what to add or what to remove. A feature that would fail as a proposal
>    today should fail as existing code today.
> 5. **Delete over refactor, refactor over rewrite.** A retrospective audit that
>    finds negative worth prefers removal to elaborate justification.

---

## 1. The Worth Model

Worth is the relation between **Value (V)** delivered and **Cost (C)** imposed
over lifetime `L`. Both sides are multi-dimensional.

### Value axes

| Axis                 | Symbol | What it measures                                                             | Measurability           |
| -------------------- | ------ | ---------------------------------------------------------------------------- | ----------------------- |
| **Utility**          | `U`    | Severity of the user need; what actually breaks without it                   | Judgment, user research |
| **Frequency**        | `F`    | How often the need arises per affected user per unit time                    | Measurable (telemetry)  |
| **Reach**            | `R`    | Proportion of users / flows / environments that encounter the need           | Measurable (analytics)  |
| **Irreplaceability** | `I`    | Cost of the next-best alternative (workaround, external tool, doing without) | Judgment, comparative   |

Aggregate value ≈ `U × F × R × I`. If any axis is zero, total value is zero.

> [!IMPORTANT] A feature loved by 2% of users, used once a year, with a trivial
> workaround, has near-zero total value no matter how elegant it is. Score
> honestly — especially `R` and `F`, which are routinely inflated.

### Cost axes

Structural cost is **delegated** to `structural-simplification`: the
`ΔD, ΔK, ΔP, Δn` introduced (prospective) or already present (retrospective).
This skill adds three ongoing-cost axes that structure alone does not capture:

| Axis              | Symbol | What it measures                                                    | Measurability                          |
| ----------------- | ------ | ------------------------------------------------------------------- | -------------------------------------- |
| **Maintenance**   | `M`    | Tests, docs, reviews, dependency updates the feature demands        | Measurable (test/doc count, churn)     |
| **Risk**          | `X`    | Bug surface × blast radius; security, privacy, performance exposure | Measurable (defect history, incidents) |
| **Evolution tax** | `E`    | Degree to which the feature constrains future change                | Judgment, changelog trace              |

Aggregate cost over lifetime ≈ `(ΔD + ΔK + ΔP + Δn)` (one-time)
`+ (M + X + E) × L` (ongoing).

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

## 2. Two Modes

The model is the same; the inputs differ.

### 2a. Prospective — evaluating proposed functionality

Applied to tickets, specs, PRDs, loose ideas, or PR scope **before
implementation**. All inputs are estimates; record confidence explicitly.

1. State the functionality in one sentence: _"This allows [who] to [do what] so
   that [outcome]."_
2. Score `V` axes with **evidence**: user interviews, request tickets, analytics
   of the workaround, competitor behavior. Opinions are not evidence.
3. Score `C` axes against a **concrete implementation sketch**: files touched,
   new abstractions or dependencies introduced, tests required, failure modes
   created.
4. Apply the Decision Protocol (§5). Verdicts are prospective (§6a).

### 2b. Retrospective — auditing existing functionality

Applied to code, modules, features, capabilities, or flags that **already
exist**. Inputs are observable; bias toward measurement over judgment.

1. Define the boundary: files, symbols, entry points, feature flags, routes, or
   callers.
2. Score `V` from usage data:
    - Telemetry hits per time window, per user cohort.
    - Reach: unique users or flows that enter this code path.
    - Irreplaceability: does an alternative path exist? Do users already use it?
    - **If `V` cannot be measured, that itself is a finding** — unmeasured
      features hide.
3. Score `C` from current observable state:
    - Structural: measure `D, K, P, n` per `structural-simplification`.
    - `M`: dedicated tests, doc pages, recent commit churn, dependency drift.
    - `X`: bug ticket history, incident postmortems, security/perf hotspot
      reports.
    - `E`: count of PRs / design docs where this feature caused scope expansion,
      workarounds, or delays.
4. Apply the Decision Protocol (§5). Verdicts are retrospective (§6b).

> [!NOTE] A retrospective audit with no telemetry available should first return
> an instrumentation task, not a verdict. Deciding to delete a feature because
> you cannot see it being used is survivorship bias in reverse.

---

## 3. Heuristic Checks

Fast signals — not substitutes for measurement.

| Check                        | Signal                                                            | Axis affected |
| ---------------------------- | ----------------------------------------------------------------- | ------------- |
| **Usage silence**            | No telemetry hits in N weeks → `F × R` approaches 0               | `V`           |
| **Workaround in wild**       | Users or code already bypass this path → `I` is small             | `V`           |
| **Single caller**            | Feature referenced from one call site only → `R` is small         | `V`           |
| **Flag defaulted off**       | Feature flag has been `off` in production for months → `V ≈ 0`    | `V`           |
| **Orphan test**              | Tests exist but no one edits the code they cover → `V` likely 0   | `V`           |
| **Churn hotspot**            | High commit frequency on these files → `M + X` are large          | `C`           |
| **Churn × complexity**       | High churn AND high cyclomatic / cognitive score → hotspot        | `C`           |
| **Defect clustering**        | Feature's code dominates recent bug tickets → `X` is large        | `C`           |
| **Bug-fix-to-feature ratio** | Most commits on this code are fixes, not improvements → `C > V`   | `C`           |
| **Blocked PRs**              | Other work routinely waits on or works around this → `E` is large | `C`           |
| **Documentation rot**        | Docs disagree with code → `M` is under-invested, `X` is hidden    | `C`           |

> [!IMPORTANT] **Churn × complexity is the single strongest empirical signal**
> for "code that costs more than it returns" (Tornhill, _Your Code as a Crime
> Scene_). Files that change often AND score high on cyclomatic or cognitive
> complexity are disproportionately responsible for defects and maintenance
> spend. Run this check before any subjective judgment in retrospective mode.

---

## 4. Forcing Questions

Each question exposes a common failure mode. Answers MUST be written, not
implicit.

### Value interrogation

- **Who** specifically needs this? Roles, counts, cohorts — not "users".
- **What do they do today** without it? If nothing, the value may be imagined.
- **What is the simplest alternative** that would satisfy 80% of the need? (CLI,
  config, docs, external tool, manual process, nothing at all.)
- **What evidence — not opinion** — supports the `V` estimate?
- **What is the smallest useful slice** we could ship and still claim the win?

### Cost interrogation

- What **new vocabulary** — concepts, abstractions, types — does this add?
  (`ΔD`)
- What currently-independent parts does this **link**? (`ΔK`)
- How many layers or files will a **typical change** touch once this exists?
  (`ΔP`)
- How many tests — including error paths, edge cases, and integration — will
  this require? (`M`)
- **If this breaks, what else breaks** with it? What is the blast radius? (`X`)
- What future change does this make **harder, slower, or more dangerous**? (`E`)

### Counterfactual

- If we **delete** this in 12 months, what is the removal cost?
- If we **never build** it, what is the realistic worst outcome?
- Is there a **non-code** solution (docs, training, config, external tool,
  process change)?

> [!WARNING] If the removal cost in 12 months exceeds the build cost today, this
> is a **one-way door**. Apply §7 asymmetric trade-offs before committing.
> One-way doors demand higher `V` and greater confidence.

---

## 5. Decision Protocol

1. **Score `V` axes** (`U, F, R, I`) on a 0–3 scale with one-line evidence per
   axis.
2. **Score `C` axes**:
    - Delegate `D, K, P, n` to `structural-simplification` (deltas for
      prospective; absolute measured values for retrospective).
    - Score `M, X, E` on 0–3 with one-line evidence per axis.
3. **Record confidence** (Low / Medium / High) for each side independently.
4. **Compare across both ledgers** without summing.
5. **Classify** using the Worth Matrix (§5a) and apply confidence gate (§5b).
6. **Emit** the Output Contract (§8).

### 5a. The Worth Matrix

|              | **Low C**            | **Medium C**             | **High C**       |
| ------------ | -------------------- | ------------------------ | ---------------- |
| **High V**   | BUILD / KEEP         | BUILD / KEEP             | NEGOTIATE (§7)   |
| **Medium V** | BUILD-minimal / KEEP | BUILD-minimal / SIMPLIFY | DEFER / SIMPLIFY |
| **Low V**    | DEFER / QUARANTINE   | DROP / SIMPLIFY          | DROP / DELETE    |

Read the matrix identically in both modes. Prospective verdicts are accept/
reject; retrospective verdicts are keep/simplify/delete.

### 5b. Confidence gate

A verdict carries the confidence of its weakest input. If either `V` or `C`
confidence is **Low**:

- **Prospective** → default to DEFER. Gather evidence before committing to
  high-cost action.
- **Retrospective** → default to QUARANTINE. Add instrumentation, revisit after
  N weeks with measured data.

Do not commit to irreversible verdicts (BUILD, DELETE) on low-confidence
estimates.

---

## 6. Verdicts

### 6a. Prospective verdicts

| Verdict           | Meaning                                                                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **BUILD**         | Proceed as specified. Record the worth rationale; it becomes the audit baseline.                                                           |
| **BUILD-minimal** | Build the smallest slice capturing ≥80% of `V`; defer the rest with explicit revisit triggers.                                             |
| **NEGOTIATE**     | High `V`, high `C`. Reduce scope, conform to an existing pattern (§7a of `structural-simplification`), or accept debt with an expiry date. |
| **DEFER**         | `V` is unclear or evidence is thin. Document trigger conditions; revisit.                                                                  |
| **DROP**          | Does not clear the cost bar. Record the rejection so the idea is not re-proposed without new evidence.                                     |

### 6b. Retrospective verdicts

| Verdict        | Meaning                                                                                                      |
| -------------- | ------------------------------------------------------------------------------------------------------------ |
| **KEEP**       | Worth is positive. Document why — the rationale prevents a future audit from deleting it blindly.            |
| **SIMPLIFY**   | Worth is positive but `C` is inflated. Apply operations from `structural-simplification` §4. Re-score after. |
| **QUARANTINE** | `V` is unmeasured. Add telemetry; revisit after N weeks.                                                     |
| **DEPRECATE**  | Marginal or negative worth; removal is non-trivial. Announce, migrate callers, remove on schedule.           |
| **DELETE**     | Negative worth, removal is feasible. Delete. Do not patch.                                                   |

> [!WARNING] "Interesting", "clever", and "elegant" are not verdicts. Cleverness
> imposes cost but rarely contributes measurable value. If a reviewer's
> rationale reduces to "it's nice that we have this," default to SIMPLIFY or
> DELETE.

---

## 7. Asymmetric Trade-offs

Cases where the Worth Matrix gives the wrong answer on its own.

### 7a. Optionality premium

A low-`V` / low-`C` feature may be worth keeping or building if it preserves
**concrete** future optionality — a known next feature whose path becomes cheap
because of it.

Test: is the next feature **named and probable**, or is the optionality
speculative? Speculative optionality fails YAGNI; the null hypothesis wins.

### 7b. Irreversibility tax

A feature that is hard to remove once shipped — public API, persisted schema,
user-visible behavior, wire format — must clear a higher bar. **Raise the
required `V` by one tier**, or require High confidence.

### 7c. Regulatory / contractual / accessibility floor

Some features deliver `V` that cannot be observed from usage telemetry: audit
logs, accessibility paths, legal holds, compliance records, safety interlocks.
Assign a **fixed-high `U`** regardless of `F × R`; `C` is still measured
normally. These features are kept even when "unused."

### 7d. Keystone cost

Some features have high local `C` because they are the seam holding a correct
abstraction in place. Removing them would **raise global complexity** elsewhere.
Measure net `ΔD, ΔK, ΔP, Δn` across the whole system before committing to DELETE
or SIMPLIFY. A local reduction that increases global complexity is not a
simplification (see `structural-simplification` Core Directive 5).

### 7e. Hot-path performance or safety

Some complexity exists because the simple version was measured to be too slow,
too unsafe, or too fragile. `C` appears inflated but is structurally
load-bearing. The audit must read the original rationale (commit message, ADR,
benchmark) before voting SIMPLIFY. Lost history is not permission to remove
load-bearing complexity.

---

## 8. Output Contract

Every application of this skill MUST produce a record with these fields:

```
Subject:        <feature / module / ticket / path under review>
Mode:           Prospective | Retrospective
V scores:       U=<0-3>  F=<0-3>  R=<0-3>  I=<0-3>       (1-line evidence each)
C scores:       ΔD=<±n>  ΔK=<±n>  ΔP=<±n>  Δn=<±n>        (prospective: deltas; retrospective: measured absolutes)
                M=<0-3>  X=<0-3>  E=<0-3>                 (1-line evidence each)
Confidence V:   Low | Medium | High
Confidence C:   Low | Medium | High
Verdict:        <from §6a or §6b>
Rationale:      <2–4 sentences tying scores → verdict>
Minimal alt:    <smallest slice preserving most V, if applicable>
Revisit when:   <measurable trigger or calendar date>
```

> [!IMPORTANT] `Revisit when` is **non-optional** for DEFER, QUARANTINE,
> BUILD-minimal, and DEPRECATE. Every such verdict MUST have a measurable
> trigger (usage threshold, date, dependency version, adjacent feature shipping)
> or it will rot into a permanent maybe.

---

## 9. Common Patterns

| Pattern                                      | Typical verdict                                                      |
| -------------------------------------------- | -------------------------------------------------------------------- |
| "Just in case" flexibility                   | DROP — fails §7a optionality test                                    |
| Admin-only tool used quarterly               | BUILD-minimal — satisfy via script or CLI, not UI                    |
| "Power user" shortcut                        | NEGOTIATE — measure `R` honestly; almost always smaller than claimed |
| Dead code behind `off` feature flag          | DELETE — `V` measurably 0, `M + X` still accruing                    |
| Duplicate of library or framework feature    | DROP or DELETE — `I` is ~0                                           |
| Legacy integration, usage unknown            | QUARANTINE — instrument first, then decide                           |
| Extension point with one implementation      | SIMPLIFY — collapse to the concrete use                              |
| "We'll need this for feature X"              | DEFER — build when X is real, not before                             |
| Stable feature that still produces bugs      | SIMPLIFY (churn × complexity hotspot), then re-evaluate              |
| Feature with no docs, no tests, no telemetry | QUARANTINE + add all three, or DEPRECATE                             |
| Compliance / audit / accessibility path      | KEEP — §7c floor applies                                             |
| Complex optimization with a benchmark in git | KEEP unless benchmark is restaged (§7e)                              |

---

## 10. Composition with Sibling Skills

- **`structural-simplification`** — source of the complexity measurement
  (`D, K, P, n`). This skill **consumes** those deltas; it does not redefine
  them.
- **`architectural-guideline`** — upstream principles (YAGNI, scope control,
  proportionality, deletion over patching). This skill is the applied protocol
  through which those principles bind to individual decisions.
- **`coding-standard`** — consulted when a SIMPLIFY or DELETE verdict produces
  code changes.
- **`continuous-improvement-protocol`** — when this skill's verdicts repeatedly
  contradict current practice or sibling skills, that is a signal to update the
  skills themselves, not to override the verdicts case-by-case.

> [!NOTE] This skill deliberately does **not** define its own complexity metric.
> Cyclomatic complexity, cognitive complexity, Halstead volume, and
> maintainability index are all input signals to the `C` side of the ledger,
> surfaced through `structural-simplification` and the churn × complexity
> heuristic. Keeping the measurement in one place preserves the
> single-source-of-truth discipline across the skill library.
