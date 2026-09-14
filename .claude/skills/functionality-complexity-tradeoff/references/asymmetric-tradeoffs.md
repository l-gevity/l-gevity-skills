# Functionality pruner — Asymmetric Trade-offs

Reference for [SKILL.md](../SKILL.md) §8. Section numbers below refer to
SKILL.md.

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
elsewhere. Measure net **Subsystem-kinds Δ, Dependency-edges Δ,
Max-chain-depth Δ, Subsystem-count Δ** across the whole system before
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
