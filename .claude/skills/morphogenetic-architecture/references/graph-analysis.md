# Reproducible Graph Analysis

Use this reference when an audit computes strongly connected components,
spectral/Fiedler cuts, normalized cuts, conductance, or partition sensitivity.
Run one evidence field at a time; never collapse fields into one graph.

## Required Sequence

1. Freeze the graph input and record source, window, coverage, blind spots, and
   confidence.
2. Declare the decision policy before inspecting a preferred candidate.
3. Run `scripts/analyze_evidence_graph.py` or a named equivalent tool.
4. Retain the input, output, input hash, tool version, and configuration.
5. Treat output as a candidate only; apply domain meaning and independent
   evidence before changing a boundary.

If no executable tool is available, report graph analysis **Not measured**.
Never reconstruct SCCs, Fiedler vectors, cuts, or sensitivity results by prose.

## Bundled Analyzer

```text
python scripts/analyze_evidence_graph.py graph.json --pretty
```

The script uses only the Python standard library and is deterministic. It
supports:

- `scc` — find strongly connected components on a graph with `directed: true`
  and fail a directed static cycle;
- `spectral-bisection` — generate a normalized-Laplacian/Fiedler candidate cut,
  selecting the sweep cut that minimizes the declared policy metric;
- `evaluate-partition` — score a supplied two-group candidate.

For directed partitioning, set `symmetrize_directed` explicitly. The original
directed graph remains available for SCC analysis.

## Input Shape

```json
{
  "schema_version": 1,
  "field": "change",
  "directed": false,
  "dataset": {
    "source": "git co-change extraction",
    "window": "2026-01-01/2026-06-30",
    "coverage": "src/**; 94% of commits",
    "blind_spots": ["squash-merge attribution"],
    "confidence": "medium"
  },
  "nodes": ["pricing", "promotions", "catalog", "checkout"],
  "edges": [
    {"source": "pricing", "target": "promotions", "weight": 0.82},
    {"source": "catalog", "target": "checkout", "weight": 0.15},
    {"source": "pricing", "target": "catalog", "weight": 0.12},
    {"source": "promotions", "target": "checkout", "weight": 0.11}
  ],
  "analysis": {
    "algorithm": "spectral-bisection",
    "decision_policy": {
      "metric": "normalized_cut",
      "operator": "<=",
      "threshold": 0.25,
      "baseline": "last accepted architecture audit",
      "basis": "declared before candidate generation",
      "minimum_evidence": "at least 90 days and 30 relevant commits",
      "minimum_group_fraction": 0.25,
      "sensitivity_fraction": 0.05,
      "minimum_partition_stability": 0.90
    }
  }
}
```

Supply each relationship once. Aggregate repeated observations into one
weighted edge before analysis. For directed graphs, uniqueness is by ordered
`source`/`target`; for undirected graphs, reversing the endpoints is still a
duplicate.

For `evaluate-partition`, add `analysis.groups` assigning every node to exactly
two named groups. Perturbation retains those supplied memberships, so reported
partition stability is structurally `1.0` with basis
`fixed-supplied-membership`; only metric/threshold stability can cause
`DEFER`. Use `spectral-bisection` when the audit must test whether memberships
remain stable under perturbation. For `scc`, omit the decision policy.

## Output Boundary

The output includes:

- `input_sha256`, `result_sha256`, and `algorithm_version`;
- connected and strongly connected components, plus the field-independent
  `directed_cycle_present` signal;
- candidate groups, normalized cut, conductance, and group volumes;
- deterministic perturbation sensitivity;
- `MEETS_POLICY`, `DOES_NOT_MEET_POLICY`, or `DEFER`.

`architecture_decision` is always `NOT_EVALUATED`. A passing cut policy does not
mean MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY; it only makes the cut eligible
for semantic review.

`hard_invariants.static_cycle` is evaluated only when `field` is exactly
`static`; use `graph.directed_cycle_present` to retain the cycle signal for
other directed field labels.

An equivalent external tool is acceptable only when the report records its
name, version, exact command, input identity, configuration/seed, candidate
metrics, and sensitivity result. Otherwise report **Not measured**.
