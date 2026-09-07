# Morphogenetic Architecture — Position Legality

Reference for [SKILL.md](../SKILL.md) §1. These clauses are the mechanical,
field-free check every placement runs; SKILL.md §1 summarizes them and §5
names the findings they decide. Section numbers refer to SKILL.md.

### Position Legality

Check the edges of the component being placed, not every edge in the
repository. This is a **design-time check on a proposed or changed
position** — its inbound and outbound edges, a handful at a time. Auditing a
whole codebase from three axes is an explicit non-goal: a derived rule loses
to one that states intent, so turn the result into `architecture-as-code`
rules that name each edge and its reason, and let those carry the standing
check. Positions belong in the repository as a reviewed artefact that fails
the build when a component arrives unpositioned; never re-derive them per
audit.

Each proposed edge satisfies one clause per axis. The clauses need no observed
field and run before §3. Layer and tier read from declared positions and the
static graph; the domain clause needs a third input, the target's declared
inbound interface, and cannot run without it.

| Axis | Kind | Legal edge | Violation |
| --- | --- | --- | --- |
| **Layer** | ordinal | Same layer; one step toward infrastructure; or toward the consumer when it points at an abstraction the target layer owns (dependency inversion) | **layer-skip violation** — more than one step, unless either endpoint is the declared adapter owning that transition. **layer inversion** — toward the consumer with no dependency inversion |
| **Abstraction tier** | ordinal | Same tier, or a higher tier calling a lower tier | **tier inversion** — a lower tier statically orchestrates its caller. A type-only edge is erased before runtime and can never orchestrate, so it cannot violate this clause |
| **Domain** | categorical | The same domain path; a path nested inside it; or the target domain's declared inbound interface | **cross-domain coupling** — a caller bypasses that inbound interface |

Layer and abstraction tier are ordinal, so "one step" is meaningful on them.
Domain is categorical: two paths are the same, one contains the other, or they
are unrelated. Containment is not distance — `commerce/payments` sits inside
`commerce`, but it is no closer to `commerce/shipping` than to `identity`, and
sibling paths never inherit permission from a shared prefix.

Three definitions the clauses stand on:

- **Inbound interface** — the contract a domain publishes for callers: a package
  entry point, an exported public surface, or a declared allowlist. Where it is
  a hand-maintained allowlist, the domain clause is a configuration file rather
  than a derived rule. Say so, and keep the list under review; the clause is
  never better than that list.
- **Re-export module** — a module that only re-exports. It takes no position of
  its own; resolve each edge through it to what it re-exports.
- **External SDK** — a third-party runtime dependency, not a language or runtime
  builtin. The clause is about reaching one at value granularity; importing its
  types is not a bypass.

Two whole-graph clauses complete the check:

- The static dependency projection must be acyclic; report the result in
  **Static cycle**.
- Code reaches an external SDK only inside its owning adapter; an escape is
  an **external SDK bypass**.

None of this is sliceable. Each per-axis clause needs a position for both
endpoints of every edge it judges, and acyclicity needs the whole dependency
closure, so placing one component still means positioning what it touches.

A **composition root** — a module whose whole job is wiring everything together
— is exempt from the domain and tier clauses by declaration. "One cohesive
capability at one primary position" has no answer for a module built to be
incohesive; name it as the composition root and move on rather than forcing a
position it cannot have.

When domain, tier, or layer cannot be stated independently for a component,
the check cannot run: report **placement ambiguity** and resolve the position
before continuing. The domain clause blocks the same way when a target domain
publishes no inbound interface — declare the interface rather than reading
every cross-domain edge as a violation, which is what an undeclared boundary
makes them all look like. When an axis does not apply to the system at hand,
record it as **Not applicable** with the reason; do not invent an ordering to
fill it. Legality is necessary, never sufficient — a legal edge
can still be wrong for reasons only §3's fields expose.
