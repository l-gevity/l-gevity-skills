# Functionality pruner — Worth Signals

Reference for [SKILL.md](../SKILL.md) §4. Section numbers below refer to
SKILL.md.

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
