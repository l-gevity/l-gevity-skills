# Rapid Topology Scan

Use this procedure when the mode selector starts in **Rapid**. Keep the scope
bounded and escalate instead of weakening the proof required for a topology
change.

## Scope Contract

Rapid may inspect:

- one new or existing component;
- a small, named set of static imports, calls, or build references;
- the component's Domain / abstraction tier / layer position;
- its inbound and outbound interfaces and allowed caller, callee, and sibling
  relationships;
- one already-identified runtime loop solely to declare its termination bound,
  owner, and observability.

Rapid must not evaluate weighted fields, infer a boundary from history or
telemetry, partition a graph, or accept a restructuring decision.

## Procedure

1. **State the subject.** Name the component or edges and whether the task is
   Design or Audit.
2. **Declare the position.** Record Domain / abstraction tier / layer,
   inbound interface, outbound interface, and allowed static neighbors.
3. **Grade reversibility, but only when a boundary would move.** A Rapid PLACE,
   KEEP, or DECLARE-RUNTIME-CYCLE marks the field **Not required** with a short
   reason. Once a restructuring candidate appears, record high / medium / low
   from consumers, published contracts, data-migration need, and deployment
   coupling, or record **Unknown — Low bar applies** with the missing facts, as
   defined in SKILL.md §5. Carry it into the escalation.
4. **Inspect the bounded evidence.** Check only the proposed or current static
   edges and, when applicable, the named runtime loop.
5. **Apply hard tests.** Check for a forbidden import cycle, layer-skip
   violation, tier inversion, cross-domain interface bypass, external SDK
   bypass, hidden runtime ownership, and placement ambiguity.
6. **Choose or escalate.** Emit one permitted Rapid decision, or continue in
   Full using the escalation rules below.
7. **Report the mode.** Fill `Analysis mode` and `Selection reason` in the main
   skill's summary block. Mark unused Full-only fields, `Reversibility`
   included, **Not required** with a short reason; do not omit them.

A Low grade or Unknown reversibility never lets Rapid accept a restructuring
decision. It raises the evidence bar once the task escalates, and it belongs in
the escalation record.

## Decision Guard

| Rapid decision | Required condition |
| --- | --- |
| **PLACE** | One new component has a clear position, explicit interfaces, and allowed static neighbors |
| **KEEP** | Existing placement and the bounded static evidence agree; no hard test fails |
| **DECLARE-RUNTIME-CYCLE** | One legitimate loop has an explicit bound, owner, termination semantics, and observability |
| **DEFER** | Placement or evidence is insufficient, contradictory, or requires a topology change |

Do not emit MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY as a final Rapid
decision. A hard violation may be reported immediately, but a fix that changes
placement or boundaries is a Full candidate.

## Escalation Rules

Set `Analysis mode: Rapid → Full` and preserve completed checks when:

- MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY becomes a candidate;
- runtime pressure, co-change, shared data, failure propagation, weighting, or
  graph partitioning must influence the decision;
- the scope expands across several domains/components or a material ownership,
  security, compliance, or failure boundary;
- placement remains ambiguous or evidence conflicts;
- the user changes the request to a deep or subsystem/service-graph audit.

Once escalated, remain in Full. Missing evidence produces DEFER plus an
instrumentation or measurement action, or a probationary acceptance when
SKILL.md §5 permits one; it never sends the task back to Rapid.

## Examples

| Request | Path | Reason |
| --- | --- | --- |
| Place a new invoice formatter with three proposed imports | Rapid | Bounded placement and static-edge check |
| Check whether one application-layer import bypasses a domain interface | Rapid | One hard static invariant |
| Decide whether billing should split into invoicing and collections | Rapid → Full | SPLIT candidate requires domain evidence and structural deltas |
| Explain why several services change and fail together | Full | Multi-field change and failure evidence |
