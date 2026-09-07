# Functionality pruner — Common Patterns

Reference for [SKILL.md](../SKILL.md) §10. Section numbers below refer to
SKILL.md.

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
| Actor/role condition encoded as a separate right, role, or endpoint           | SIMPLIFY — an attribute or workflow-state gate satisfies the obligation (§1e), unless a second person is explicitly required |
| "We'll need this for feature X"                                               | DEFER — build when X is real, not before                                              |
| Stable feature that still produces bugs                                       | SIMPLIFY (churn × complexity hotspot), then re-evaluate                               |
| Feature with no docs, no tests, no telemetry                                  | QUARANTINE + add all three, or DEPRECATE — but check §1 first; it may be unreachable  |
| Compliance / audit / accessibility path                                       | KEEP when the mapped external requirement applies — §8c floor                         |
| Complex optimization with a benchmark in git                                  | KEEP unless benchmark is restaged (§8e)                                               |
| Assertion that documents an invariant nothing else captures                   | SIMPLIFY — downgrade to comment / ADR / build-time check (§1c), do not OBSOLETE       |
