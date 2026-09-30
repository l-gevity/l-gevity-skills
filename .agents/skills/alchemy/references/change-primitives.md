# Change Primitives — Named Specializations

Which sibling term specializes which primitive. `SKILL.md` §1 defines the four
primitives; this table is lookup material for a stage that must name its own
term, and adds no rule of its own.

| Primitive | Named specializations |
|:--|:--|
| **Subsystem** | L places it at a position; E governs it per directory; C counts subsystems (n) and their kinds (D); `bring-down` ranks the capability it can be replaced by. Requirements skills group requirements into *capabilities*; A decides when a capability becomes a subsystem boundary, and L places it. |
| **Aspect** | Grounding: a requirement with `Holds across`; Topology: a `constraint` node with `holds_across` and the `Aspect coverage` check; Readiness: a row of the aspect matrix; M: the aspect-owner map; A: extracted, never interleaved; L: the mechanism's position plus `Holds across`; C: the aspect-extraction delta; E: the mechanism's exclusivity edges; H: placement of the coverage check; Test Strategy: its oracle; Traceability: the `aspect-uncovered` gap. |
| **Increment** | Readiness admits it — a *vertical increment* realizes one outcome end to end through every layer it crosses; `evolutionary-database-design`: a *migration increment* per stage; `system-optimization`: a *batch* is the set of increments moved together; CI/CD: the *candidate artifact* is its built form. |
| **Iteration** | Completion evidence closes an iteration (`requirements-traceability`); outcome evidence does not. Y optimizes only a stable, measured baseline, so it *runs in the iteration after the increment ships*. A PDCA or DMAIC turn in `system-optimization` is an iteration whose Check or Control step is the measurement. |
