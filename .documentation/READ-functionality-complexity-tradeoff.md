# Functionality Pruner

A first-principles SKILL for deciding whether a piece of functionality is worth keeping or building. Two stages: a **necessity gate** ("does the problem this code addresses actually occur in this stack?") followed by a **worth ledger** ("does the value justify the cost?").

## Why use this

- **"Just in case" code stops being inarguable.** Defensive checks against impossible states get a name (OBSOLETE) and a structural reason for removal — not a budget debate.
- **Speculative features die before implementation.** YAGNI becomes the null hypothesis; high-cost work needs evidence, not enthusiasm.
- **Build and audit share a model.** A feature that would fail as a proposal today fails as existing code today.
- **Verdicts resist re-litigation.** "Removed because the problem cannot occur in this stack" closes the question; "removed because cost > value" reopens it whenever priorities shift.
- **Necessity findings beat usage data.** You don't need telemetry to delete a code path that's structurally unreachable.

## Fundamental principles

Most code review collapses value and cost into a vibe ("this seems useful", "this seems heavy"). This skill separates them, and adds a gate before scoring even starts: **does the problem this code addresses actually exist in this stack?**

- **Necessity precedes worth.** Code guarding against architecturally impossible states has zero value — not low value. Skip the worth ledger; emit OBSOLETE.
- **Separate the ledger.** Value and cost are distinct axes. Score independently; never collapse into one number.
- **Cost compounds, value decays.** Value is realized per use; cost accrues on every future change, test run, review, and incident.
- **The default is No.** If worth isn't clearly positive, reject or minimize. **YAGNI is the null hypothesis.**
- **Delete over refactor, refactor over rewrite.** A retrospective audit with negative or failing-necessity worth prefers removal to elaborate justification.

## How to use

The skill has two modes: **prospective** (should we build this?) or **retrospective** (should we keep this?).

1. **Identify the subject.** A proposed feature, a defensive check that looks redundant, a feature flag that may have outlived its launch, an abstraction with one user.
2. **Prompt the AI.**

   > *Prospective:* "Apply functionality-pruner to this PRD: 'Add a client-version-check that warns users their tab is stale.' We deploy as a single SPA artifact."
   >
   > *Retrospective:* "Audit `src/auth/legacyTokenShim.ts` against functionality-pruner. We migrated to OAuth six months ago."

3. **Read the verdict.** The skill names the verdict (BUILD / BUILD-minimal / NEGOTIATE / DEFER / DROP for prospective; KEEP / SIMPLIFY / QUARANTINE / DEPRECATE / DELETE / OBSOLETE for retrospective) and the rationale.
4. **Apply the verdict.** Delete the OBSOLETE check; ship the BUILD-minimal slice; instrument the QUARANTINE candidate; document the structural reason so a later audit doesn't reintroduce the same code.

## The necessity gate

Before scoring value or cost, walk the categories. A single positive finding routes the verdict to OBSOLETE (retrospective) or DROP-as-non-problem (prospective).

| Category                              | Definition                                                              | Typical example                                                       |
|---------------------------------------|-------------------------------------------------------------------------|-----------------------------------------------------------------------|
| **Impossible-state guard**            | Defends against a state ruled out by topology, types, or runtime        | Client/server skew check in a single-artifact SPA                     |
| **Already-defended-elsewhere**        | Concern fully owned by another layer                                    | XSS-escape on top of an auto-escaping templating engine               |
| **Cargo-culted pattern**              | Pattern's prerequisites don't hold here                                 | Connection pool in a 200ms CLI; singleton in a stateless lambda       |
| **Phantom requirement**               | Solves a requirement that lapsed or never existed                       | Feature flag for a launch that completed                              |
| **Generality without instantiation**  | Abstraction whose anticipated variation never materialized              | Strategy pattern with one strategy                                    |
| **Logically dead branch**             | Unreachable given upstream contracts                                    | `if (!user.id)` after auth middleware that guarantees it              |

> The invariant audit is the highest-yield necessity check. List the invariants the architecture, type system, deployment topology, and trust boundary maintain. Then walk the branches with the list in hand.

## The worth ledger

Once necessity passes, score both sides independently. **Don't collapse to one number.**

- **Value (V):** `U × F × R × I` — utility, frequency, reach, irreplaceability. Any axis at zero ⇒ total value is zero.
- **Cost (C):** structural deltas (`ΔD, ΔK, ΔP, Δn` — delegated to `structural-simplification`) plus ongoing axes — maintenance (`M`), risk (`X`), evolution tax (`E`).
- **Worth > 0 ⇔ V × L > C_structural + (M + X + E) × L.** Most production features are long-lived; plan for the ongoing term.

Score 0–3 on each axis with one-line evidence. Record confidence (Low / Medium / High) per side. Low confidence → DEFER (prospective) or QUARANTINE (retrospective). OBSOLETE is exempt — a structural impossibility doesn't become more or less impossible with more data.

## When to skip

Routine bug fixes inside a working module, content/copy edits, dependency bumps. The framework earns its keep on triage decisions, dead-code audits, "is this defensive check necessary?" reviews, and PR scope pushback.

## Next steps

- See [SKILL.md](./SKILL.md) for the full reference (necessity-gate detection heuristics, worth axes, decision protocol, asymmetric trade-offs, output contract).
- For the structural complexity measurement (`D, K, P, n`) consumed on the cost side, see [`structural-simplification`](../structural-simplification/).
- For the upstream principles (YAGNI, scope control, proportionality), see [`architecture-guidelines`](../architecture-guidelines/).
- Run a retrospective audit on the next "just in case" check that lands in code review — the necessity gate often closes the question on the first pass.
