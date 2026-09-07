# Functionality pruner — Forcing Questions

Reference for [SKILL.md](../SKILL.md) §5. Section numbers below refer to
SKILL.md.

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
