# Change Primitives — Definitions and Named Specializations

The four primitives every stage uses to describe change, and which sibling
term specializes which. `SKILL.md` §1 names them; this file is vocabulary for
a stage that must name its own term, not a gate rule, and adds no rule of its
own.

| Primitive | Definition |
|:--|:--|
| **Subsystem** | A part produced by decomposition: the thing a position is assigned to and a rule file governs. *Where change lands.* |
| **Aspect** | A property that holds across a declared set of the units the stage knows — problem scopes at Grounding and Topology, capabilities at Readiness, subsystems from L onward; the scope → subsystem mapping is L's placement decision, never inferred upstream. One obligation (the rule) and one mechanism (the subsystem that implements it). *Which dimension is touched.* |
| **Increment** | The bounded unit of change admitted to implementation; it adds, changes, or removes cells of the subsystem × aspect matrix. *What changes.* |
| **Iteration** | One cycle that admits an increment, realizes it, and measures the resulting baseline: completion evidence plus the structural and flow measurements later windows compare against. Prediction windows, outcome-evidence windows, and revisit triggers are carried across iterations and close on their own trigger, re-entering L or M as a new bounded decision. "Iteration 2" is the next iteration on the same subject, *starting from that measured baseline*. |

| Primitive | Named specializations |
|:--|:--|
| **Subsystem** | L places it at a position; E governs it per directory; C counts subsystems (n) and their kinds (D); `bring-down` ranks the capability it can be replaced by. Requirements skills group requirements into *capabilities*; A decides when a capability becomes a subsystem boundary, and L places it. |
| **Aspect** | Grounding: a requirement with `Holds across`; Topology: a `constraint` node with `holds_across` and the `Aspect coverage` check; Readiness: a row of the aspect matrix; M: the aspect-owner map; A: extracted, never interleaved; L: the mechanism's position plus `Holds across`; C: the aspect-extraction delta; E: the mechanism's exclusivity edges; H: placement of the coverage check; Test Strategy: its oracle; Traceability: the `aspect-uncovered` gap. |
| **Increment** | Readiness admits it — a *vertical increment* realizes one outcome end to end through every layer it crosses; `evolutionary-database-design`: a *migration increment* per stage; `system-optimization`: a *batch* is the set of increments moved together; CI/CD: the *candidate artifact* is its built form. |
| **Iteration** | Completion evidence closes an iteration (`requirements-traceability`); outcome evidence does not. Y optimizes only a stable, measured baseline, so it *runs in the iteration after the increment ships*. A PDCA or DMAIC turn in `system-optimization` is an iteration whose Check or Control step is the measurement. |
