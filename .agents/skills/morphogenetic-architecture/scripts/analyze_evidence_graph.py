#!/usr/bin/env python3
"""Deterministically analyze one morphogenetic-architecture evidence graph."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ALGORITHM_VERSION = 2
SENSITIVITY_SCENARIOS = 8
VALID_ALGORITHMS = {"scc", "spectral-bisection", "evaluate-partition"}
VALID_METRICS = {"normalized_cut", "conductance"}
VALID_OPERATORS = {"<", "<=", ">", ">="}
VALID_CONFIDENCE = {"low", "medium", "high"}


class InputError(ValueError):
    """Raised when an analysis input violates the deterministic contract."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(f"{label} must be an object")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{label} must be a non-empty string")
    return value.strip()


def _require_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{label} must be a number")
    result = float(value)
    if not math.isfinite(result):
        raise InputError(f"{label} must be finite")
    return result


def _rounded(value: float) -> float:
    return round(value, 12)


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_dataset(value: Any) -> dict[str, Any]:
    dataset = _require_mapping(value, "dataset")
    confidence = _require_string(dataset.get("confidence"), "dataset.confidence").lower()
    if confidence not in VALID_CONFIDENCE:
        raise InputError("dataset.confidence must be low, medium, or high")
    blind_spots = dataset.get("blind_spots")
    if not isinstance(blind_spots, list) or not all(
        isinstance(item, str) for item in blind_spots
    ):
        raise InputError("dataset.blind_spots must be an array of strings")
    return {
        "source": _require_string(dataset.get("source"), "dataset.source"),
        "window": _require_string(dataset.get("window"), "dataset.window"),
        "coverage": _require_string(dataset.get("coverage"), "dataset.coverage"),
        "blind_spots": blind_spots,
        "confidence": confidence,
    }


def _validate_policy(value: Any) -> dict[str, Any]:
    policy = _require_mapping(value, "analysis.decision_policy")
    metric = _require_string(policy.get("metric"), "decision_policy.metric")
    operator = _require_string(policy.get("operator"), "decision_policy.operator")
    if metric not in VALID_METRICS:
        raise InputError(
            "decision_policy.metric must be normalized_cut or conductance"
        )
    if operator not in VALID_OPERATORS:
        raise InputError("decision_policy.operator must be <, <=, >, or >=")

    threshold = _require_number(policy.get("threshold"), "decision_policy.threshold")
    minimum_group_fraction = _require_number(
        policy.get("minimum_group_fraction"),
        "decision_policy.minimum_group_fraction",
    )
    sensitivity_fraction = _require_number(
        policy.get("sensitivity_fraction"),
        "decision_policy.sensitivity_fraction",
    )
    minimum_partition_stability = _require_number(
        policy.get("minimum_partition_stability"),
        "decision_policy.minimum_partition_stability",
    )
    if not 0 < minimum_group_fraction <= 0.5:
        raise InputError("minimum_group_fraction must be in (0, 0.5]")
    if not 0 < sensitivity_fraction <= 0.25:
        raise InputError("sensitivity_fraction must be in (0, 0.25]")
    if not 0 <= minimum_partition_stability <= 1:
        raise InputError("minimum_partition_stability must be in [0, 1]")

    return {
        "metric": metric,
        "operator": operator,
        "threshold": threshold,
        "baseline": _require_string(
            policy.get("baseline"), "decision_policy.baseline"
        ),
        "basis": _require_string(policy.get("basis"), "decision_policy.basis"),
        "minimum_evidence": _require_string(
            policy.get("minimum_evidence"),
            "decision_policy.minimum_evidence",
        ),
        "minimum_group_fraction": minimum_group_fraction,
        "sensitivity_fraction": sensitivity_fraction,
        "minimum_partition_stability": minimum_partition_stability,
    }


def _validate_payload(payload: Any) -> dict[str, Any]:
    root = _require_mapping(payload, "input")
    if root.get("schema_version") != 1:
        raise InputError("schema_version must be 1")

    field = _require_string(root.get("field"), "field")
    directed = root.get("directed")
    if not isinstance(directed, bool):
        raise InputError("directed must be a boolean")
    dataset = _validate_dataset(root.get("dataset"))

    raw_nodes = root.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise InputError("nodes must be a non-empty array of unique strings")
    nodes = [_require_string(node, "nodes[]") for node in raw_nodes]
    if len(nodes) != len(set(nodes)):
        raise InputError("nodes must be unique")
    node_set = set(nodes)

    raw_edges = root.get("edges")
    if not isinstance(raw_edges, list):
        raise InputError("edges must be an array")
    edges: list[dict[str, Any]] = []
    edge_keys: set[tuple[str, str]] = set()
    for index, raw_edge in enumerate(raw_edges):
        edge = _require_mapping(raw_edge, f"edges[{index}]")
        source = _require_string(edge.get("source"), f"edges[{index}].source")
        target = _require_string(edge.get("target"), f"edges[{index}].target")
        weight = _require_number(edge.get("weight"), f"edges[{index}].weight")
        if source not in node_set or target not in node_set:
            raise InputError(f"edges[{index}] references an unknown node")
        if source == target:
            raise InputError(f"edges[{index}] must not be a self-loop")
        if weight <= 0:
            raise InputError(f"edges[{index}].weight must be greater than zero")
        edge_key = (source, target) if directed else tuple(sorted((source, target)))
        if edge_key in edge_keys:
            edge_kind = "directed" if directed else "undirected"
            raise InputError(
                f"edges[{index}] duplicates an existing {edge_kind} edge"
            )
        edge_keys.add(edge_key)
        edges.append({"source": source, "target": target, "weight": weight})

    analysis = _require_mapping(root.get("analysis"), "analysis")
    algorithm = _require_string(analysis.get("algorithm"), "analysis.algorithm")
    if algorithm not in VALID_ALGORITHMS:
        raise InputError(
            "analysis.algorithm must be scc, spectral-bisection, "
            "or evaluate-partition"
        )
    if algorithm == "scc" and not directed:
        raise InputError("scc requires directed=true")

    validated_analysis: dict[str, Any] = {"algorithm": algorithm}
    if algorithm != "scc":
        validated_analysis["decision_policy"] = _validate_policy(
            analysis.get("decision_policy")
        )
        symmetrize = analysis.get("symmetrize_directed", False)
        if not isinstance(symmetrize, bool):
            raise InputError("analysis.symmetrize_directed must be a boolean")
        if directed and not symmetrize:
            raise InputError(
                "directed partitioning requires analysis.symmetrize_directed=true"
            )
        validated_analysis["symmetrize_directed"] = symmetrize

    if algorithm == "evaluate-partition":
        groups = _require_mapping(analysis.get("groups"), "analysis.groups")
        if set(groups) != node_set:
            raise InputError("analysis.groups must assign every node exactly once")
        labels = {
            node: _require_string(group, f"analysis.groups.{node}")
            for node, group in groups.items()
        }
        if len(set(labels.values())) != 2:
            raise InputError("analysis.groups must contain exactly two groups")
        validated_analysis["groups"] = labels

    return {
        "schema_version": 1,
        "field": field,
        "directed": directed,
        "dataset": dataset,
        "nodes": sorted(nodes),
        "edges": edges,
        "analysis": validated_analysis,
    }


def _directed_adjacency(
    nodes: list[str], edges: list[dict[str, Any]]
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    outgoing = {node: [] for node in nodes}
    incoming = {node: [] for node in nodes}
    for edge in edges:
        outgoing[edge["source"]].append(edge["target"])
        incoming[edge["target"]].append(edge["source"])
    for adjacency in (outgoing, incoming):
        for node in nodes:
            adjacency[node] = sorted(set(adjacency[node]))
    return outgoing, incoming


def _strongly_connected_components(
    nodes: list[str], edges: list[dict[str, Any]]
) -> list[list[str]]:
    outgoing, incoming = _directed_adjacency(nodes, edges)
    seen: set[str] = set()
    order: list[str] = []

    for start in nodes:
        if start in seen:
            continue
        stack: list[tuple[str, bool]] = [(start, False)]
        while stack:
            node, expanded = stack.pop()
            if expanded:
                order.append(node)
                continue
            if node in seen:
                continue
            seen.add(node)
            stack.append((node, True))
            for neighbor in reversed(outgoing[node]):
                if neighbor not in seen:
                    stack.append((neighbor, False))

    seen.clear()
    components: list[list[str]] = []
    for start in reversed(order):
        if start in seen:
            continue
        component: list[str] = []
        stack = [start]
        seen.add(start)
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in reversed(incoming[node]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        if len(component) > 1:
            components.append(sorted(component))
    return sorted(components, key=lambda item: (item[0], len(item), item))


def _undirected_edges(
    edges: list[dict[str, Any]],
) -> dict[tuple[str, str], float]:
    result: dict[tuple[str, str], float] = {}
    for edge in edges:
        pair = tuple(sorted((edge["source"], edge["target"])))
        result[pair] = result.get(pair, 0.0) + float(edge["weight"])
    return result


def _connected_components(
    nodes: list[str], edges: dict[tuple[str, str], float]
) -> list[list[str]]:
    adjacency = {node: [] for node in nodes}
    for source, target in edges:
        adjacency[source].append(target)
        adjacency[target].append(source)
    seen: set[str] = set()
    components: list[list[str]] = []
    for start in nodes:
        if start in seen:
            continue
        component: list[str] = []
        stack = [start]
        seen.add(start)
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in sorted(adjacency[node], reverse=True):
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    return sorted(components, key=lambda item: (item[0], len(item), item))


def _degrees(
    nodes: list[str], edges: dict[tuple[str, str], float]
) -> dict[str, float]:
    result = {node: 0.0 for node in nodes}
    for (source, target), weight in edges.items():
        result[source] += weight
        result[target] += weight
    return result


def _project_and_normalize(vector: list[float], principal: list[float]) -> list[float]:
    projection = sum(a * b for a, b in zip(vector, principal))
    projected = [
        value - projection * basis for value, basis in zip(vector, principal)
    ]
    norm = math.sqrt(sum(value * value for value in projected))
    if norm <= 1e-15:
        return []
    normalized = [value / norm for value in projected]
    for value in normalized:
        if abs(value) > 1e-14:
            if value < 0:
                normalized = [-item for item in normalized]
            break
    return normalized


def _fiedler_vector(
    nodes: list[str],
    edges: dict[tuple[str, str], float],
    *,
    iterations: int = 400,
    tolerance: float = 1e-12,
) -> list[float]:
    index = {node: position for position, node in enumerate(nodes)}
    degrees = _degrees(nodes, edges)
    if any(degrees[node] <= 0 for node in nodes):
        raise InputError("spectral-bisection requires a connected graph")

    degree_root = [math.sqrt(degrees[node]) for node in nodes]
    root_norm = math.sqrt(sum(value * value for value in degree_root))
    principal = [value / root_norm for value in degree_root]
    normalized_edges = [
        (
            index[source],
            index[target],
            weight / math.sqrt(degrees[source] * degrees[target]),
        )
        for (source, target), weight in sorted(edges.items())
    ]

    def shifted_matvec(vector: list[float]) -> list[float]:
        result = list(vector)
        for source, target, weight in normalized_edges:
            result[source] += weight * vector[target]
            result[target] += weight * vector[source]
        return result

    candidates: list[tuple[float, list[float]]] = []
    for seed in range(1, 7):
        initial = [
            math.sin((position + 1) * (seed + 0.375))
            + math.cos((position + 1) * (seed + 1.125))
            for position in range(len(nodes))
        ]
        vector = _project_and_normalize(initial, principal)
        if not vector:
            continue
        for _ in range(iterations):
            updated = _project_and_normalize(shifted_matvec(vector), principal)
            if not updated:
                break
            delta = max(abs(a - b) for a, b in zip(vector, updated))
            vector = updated
            if delta <= tolerance:
                break
        shifted = shifted_matvec(vector)
        rayleigh = sum(a * b for a, b in zip(vector, shifted))
        candidates.append((rayleigh, vector))

    if not candidates:
        raise InputError("spectral-bisection could not derive a stable vector")
    candidates.sort(key=lambda item: (-item[0], tuple(_rounded(v) for v in item[1])))
    return candidates[0][1]


def _partition_metrics(
    nodes: list[str],
    edges: dict[tuple[str, str], float],
    labels: dict[str, str],
) -> dict[str, Any]:
    groups = sorted(set(labels.values()))
    if len(groups) != 2:
        raise InputError("partition must contain exactly two groups")
    degrees = _degrees(nodes, edges)
    volumes = {group: 0.0 for group in groups}
    internal = {group: 0.0 for group in groups}
    cross_weight = 0.0
    for node in nodes:
        volumes[labels[node]] += degrees[node]
    for (source, target), weight in edges.items():
        if labels[source] == labels[target]:
            internal[labels[source]] += weight
        else:
            cross_weight += weight
    if any(volume <= 0 for volume in volumes.values()):
        raise InputError("partition contains a zero-volume group")

    normalized_cut = sum(cross_weight / volumes[group] for group in groups)
    conductance = cross_weight / min(volumes.values())
    group_nodes = {
        group: sorted(node for node in nodes if labels[node] == group)
        for group in groups
    }
    return {
        "groups": group_nodes,
        "group_sizes": {group: len(group_nodes[group]) for group in groups},
        "cross_weight": _rounded(cross_weight),
        "internal_weight": {
            group: _rounded(internal[group]) for group in groups
        },
        "volume": {group: _rounded(volumes[group]) for group in groups},
        "normalized_cut": _rounded(normalized_cut),
        "conductance": _rounded(conductance),
    }


def _spectral_partition(
    nodes: list[str],
    edges: dict[tuple[str, str], float],
    minimum_group_fraction: float,
    selection_metric: str,
) -> tuple[dict[str, str], dict[str, Any]]:
    components = _connected_components(nodes, edges)
    if len(components) != 1:
        raise InputError(
            "spectral-bisection requires one connected component; "
            "analyze disconnected components separately"
        )
    if len(nodes) < 2:
        raise InputError("spectral-bisection requires at least two nodes")

    vector = _fiedler_vector(nodes, edges)
    ordered = sorted(zip(vector, nodes), key=lambda item: (item[0], item[1]))
    minimum_size = max(1, math.ceil(len(nodes) * minimum_group_fraction))
    maximum_size = len(nodes) - minimum_size
    if minimum_size > maximum_size:
        raise InputError("minimum_group_fraction leaves no valid bisection")

    candidates: list[
        tuple[float, float, tuple[str, ...], dict[str, str], dict[str, Any]]
    ] = []
    for cut_index in range(minimum_size, maximum_size + 1):
        left = {node for _, node in ordered[:cut_index]}
        labels = {
            node: ("A" if node in left else "B")
            for node in nodes
        }
        metrics = _partition_metrics(nodes, edges, labels)
        candidates.append(
            (
                metrics["normalized_cut"],
                metrics["conductance"],
                tuple(metrics["groups"]["A"]),
                labels,
                metrics,
            )
        )
    if selection_metric == "conductance":
        candidates.sort(key=lambda item: (item[1], item[0], item[2]))
    else:
        candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    _, _, _, labels, metrics = candidates[0]
    metrics["fiedler_vector"] = {
        node: _rounded(vector[position]) for position, node in enumerate(nodes)
    }
    return labels, metrics


def _compare(value: float, operator: str, threshold: float) -> bool:
    if operator == "<":
        return value < threshold
    if operator == "<=":
        return value <= threshold
    if operator == ">":
        return value > threshold
    if operator == ">=":
        return value >= threshold
    raise AssertionError(f"unsupported operator: {operator}")


def _perturb_edges(
    edges: dict[tuple[str, str], float],
    fraction: float,
    scenario: int,
) -> dict[tuple[str, str], float]:
    result: dict[tuple[str, str], float] = {}
    for pair, weight in sorted(edges.items()):
        token = f"{scenario}\0{pair[0]}\0{pair[1]}".encode("utf-8")
        direction = 1 if hashlib.sha256(token).digest()[0] % 2 else -1
        result[pair] = weight * (1 + direction * fraction)
    return result


def _partition_agreement(
    nodes: list[str], baseline: dict[str, str], candidate: dict[str, str]
) -> float:
    direct = sum(baseline[node] == candidate[node] for node in nodes) / len(nodes)
    flipped = 1.0 - direct
    return max(direct, flipped)


def _analyze_partition(
    nodes: list[str],
    edges: dict[tuple[str, str], float],
    algorithm: str,
    policy: dict[str, Any],
    supplied_groups: dict[str, str] | None,
) -> dict[str, Any]:
    if algorithm == "spectral-bisection":
        labels, metrics = _spectral_partition(
            nodes,
            edges,
            policy["minimum_group_fraction"],
            policy["metric"],
        )
    else:
        assert supplied_groups is not None
        original_groups = sorted(set(supplied_groups.values()))
        group_alias = {original_groups[0]: "A", original_groups[1]: "B"}
        labels = {
            node: group_alias[supplied_groups[node]]
            for node in nodes
        }
        metrics = _partition_metrics(nodes, edges, labels)

    metric = policy["metric"]
    baseline_pass = _compare(metrics[metric], policy["operator"], policy["threshold"])
    scenario_values: list[float] = []
    agreements: list[float] = []
    scenario_passes: list[bool] = []

    for scenario in range(SENSITIVITY_SCENARIOS):
        perturbed = _perturb_edges(
            edges, policy["sensitivity_fraction"], scenario
        )
        if algorithm == "spectral-bisection":
            scenario_labels, scenario_metrics = _spectral_partition(
                nodes,
                perturbed,
                policy["minimum_group_fraction"],
                policy["metric"],
            )
            agreements.append(_partition_agreement(nodes, labels, scenario_labels))
        else:
            scenario_metrics = _partition_metrics(nodes, perturbed, labels)
            agreements.append(1.0)
        scenario_value = scenario_metrics[metric]
        scenario_values.append(scenario_value)
        scenario_passes.append(
            _compare(scenario_value, policy["operator"], policy["threshold"])
        )

    minimum_stability = min(agreements)
    policy_consistent = all(result == baseline_pass for result in scenario_passes)
    if (
        minimum_stability < policy["minimum_partition_stability"]
        or not policy_consistent
    ):
        policy_result = "DEFER"
    elif baseline_pass:
        policy_result = "MEETS_POLICY"
    else:
        policy_result = "DOES_NOT_MEET_POLICY"

    return {
        "candidate": metrics,
        "decision_policy": {
            **policy,
            "threshold": _rounded(policy["threshold"]),
            "minimum_group_fraction": _rounded(
                policy["minimum_group_fraction"]
            ),
            "sensitivity_fraction": _rounded(policy["sensitivity_fraction"]),
            "minimum_partition_stability": _rounded(
                policy["minimum_partition_stability"]
            ),
        },
        "sensitivity": {
            "scenarios": SENSITIVITY_SCENARIOS,
            "metric_min": _rounded(min(scenario_values)),
            "metric_max": _rounded(max(scenario_values)),
            "minimum_partition_stability": _rounded(minimum_stability),
            "partition_stability_basis": (
                "recomputed-spectral-membership"
                if algorithm == "spectral-bisection"
                else "fixed-supplied-membership"
            ),
            "policy_consistent": policy_consistent,
        },
        "policy_result": policy_result,
        "architecture_decision": "NOT_EVALUATED",
    }


def analyze(payload: Any, input_sha256: str) -> dict[str, Any]:
    data = _validate_payload(payload)
    nodes = data["nodes"]
    edges = data["edges"]
    algorithm = data["analysis"]["algorithm"]
    undirected = _undirected_edges(edges)
    components = _connected_components(nodes, undirected)
    sccs = (
        _strongly_connected_components(nodes, edges)
        if data["directed"]
        else []
    )

    result: dict[str, Any] = {
        "schema_version": 1,
        "algorithm_version": ALGORITHM_VERSION,
        "input_sha256": input_sha256,
        "field": data["field"],
        "dataset": data["dataset"],
        "algorithm": algorithm,
        "analysis_config": {
            "symmetrize_directed": data["analysis"].get(
                "symmetrize_directed", False
            ),
            "sensitivity_scenarios": (
                SENSITIVITY_SCENARIOS if algorithm != "scc" else 0
            ),
        },
        "graph": {
            "directed": data["directed"],
            "node_count": len(nodes),
            "edge_count": len(edges),
            "connected_components": components,
            "strongly_connected_components": sccs,
            "directed_cycle_present": bool(sccs),
        },
        "hard_invariants": {
            "static_cycle": (
                "Fail"
                if data["field"] == "static" and data["directed"] and sccs
                else "Pass"
                if data["field"] == "static" and data["directed"]
                else "Not applicable"
            )
        },
        "candidate": None,
        "decision_policy": None,
        "sensitivity": None,
        "policy_result": "NOT_APPLICABLE",
        "architecture_decision": "NOT_EVALUATED",
    }

    if algorithm != "scc":
        partition_result = _analyze_partition(
            nodes,
            undirected,
            algorithm,
            data["analysis"]["decision_policy"],
            data["analysis"].get("groups"),
        )
        result.update(partition_result)

    result["result_sha256"] = _canonical_hash(result)
    return result


def _serialize_output(output: dict[str, Any], pretty: bool) -> str:
    return json.dumps(
        output,
        ensure_ascii=True,
        indent=2 if pretty else None,
        sort_keys=True,
    )


def _self_test() -> None:
    base_policy = {
        "metric": "normalized_cut",
        "operator": "<=",
        "threshold": 0.2,
        "baseline": "two cohesive clusters joined by one weak edge",
        "basis": "declared self-test policy",
        "minimum_evidence": "all embedded self-test edges",
        "minimum_group_fraction": 0.3,
        "sensitivity_fraction": 0.05,
        "minimum_partition_stability": 0.95,
    }
    payload = {
        "schema_version": 1,
        "field": "change",
        "directed": False,
        "dataset": {
            "source": "embedded self-test",
            "window": "fixed",
            "coverage": "all six nodes",
            "blind_spots": [],
            "confidence": "high",
        },
        "nodes": ["a", "b", "c", "d", "e", "f"],
        "edges": [
            {"source": "a", "target": "b", "weight": 5},
            {"source": "a", "target": "c", "weight": 5},
            {"source": "b", "target": "c", "weight": 5},
            {"source": "d", "target": "e", "weight": 5},
            {"source": "d", "target": "f", "weight": 5},
            {"source": "e", "target": "f", "weight": 5},
            {"source": "c", "target": "d", "weight": 0.2},
        ],
        "analysis": {
            "algorithm": "spectral-bisection",
            "decision_policy": base_policy,
        },
    }
    output = analyze(payload, _canonical_hash(payload))
    groups = {
        frozenset(group) for group in output["candidate"]["groups"].values()
    }
    expected = {frozenset({"a", "b", "c"}), frozenset({"d", "e", "f"})}
    assert groups == expected, output
    assert output["policy_result"] == "MEETS_POLICY", output
    assert output["architecture_decision"] == "NOT_EVALUATED", output
    assert analyze(payload, _canonical_hash(payload)) == output

    evaluate_payload = json.loads(json.dumps(payload))
    evaluate_payload["analysis"] = {
        "algorithm": "evaluate-partition",
        "groups": {
            "a": "left",
            "b": "left",
            "c": "left",
            "d": "right",
            "e": "right",
            "f": "right",
        },
        "decision_policy": base_policy,
    }
    evaluate_output = analyze(
        evaluate_payload, _canonical_hash(evaluate_payload)
    )
    assert evaluate_output["policy_result"] == "MEETS_POLICY", evaluate_output
    assert evaluate_output["candidate"]["groups"] == {
        "A": ["a", "b", "c"],
        "B": ["d", "e", "f"],
    }, evaluate_output
    assert (
        evaluate_output["sensitivity"]["partition_stability_basis"]
        == "fixed-supplied-membership"
    ), evaluate_output

    conductance_policy = {**base_policy, "metric": "conductance"}
    conductance_payload = {
        "schema_version": 1,
        "field": "change",
        "directed": False,
        "dataset": {
            "source": "embedded conductance-selection self-test",
            "window": "fixed",
            "coverage": "all six nodes",
            "blind_spots": [],
            "confidence": "high",
        },
        "nodes": ["a", "b", "c", "d", "e", "f"],
        "edges": [
            {"source": "a", "target": "c", "weight": 2},
            {"source": "a", "target": "f", "weight": 3},
            {"source": "b", "target": "e", "weight": 3},
            {"source": "b", "target": "f", "weight": 1},
            {"source": "c", "target": "d", "weight": 3},
            {"source": "c", "target": "f", "weight": 3},
            {"source": "d", "target": "e", "weight": 2},
            {"source": "e", "target": "f", "weight": 3},
        ],
        "analysis": {
            "algorithm": "spectral-bisection",
            "decision_policy": conductance_policy,
        },
    }
    conductance_output = analyze(
        conductance_payload, _canonical_hash(conductance_payload)
    )
    conductance_groups = {
        frozenset(group)
        for group in conductance_output["candidate"]["groups"].values()
    }
    assert conductance_groups == {
        frozenset({"b", "d", "e"}),
        frozenset({"a", "c", "f"}),
    }, conductance_output

    cycle_payload = {
        "schema_version": 1,
        "field": "static",
        "directed": True,
        "dataset": {
            "source": "embedded self-test",
            "window": "not applicable",
            "coverage": "all nodes",
            "blind_spots": [],
            "confidence": "high",
        },
        "nodes": ["a", "b", "c"],
        "edges": [
            {"source": "a", "target": "b", "weight": 1},
            {"source": "b", "target": "c", "weight": 1},
            {"source": "c", "target": "a", "weight": 1},
        ],
        "analysis": {"algorithm": "scc"},
    }
    cycle_output = analyze(cycle_payload, _canonical_hash(cycle_payload))
    assert cycle_output["hard_invariants"]["static_cycle"] == "Fail", cycle_output
    assert cycle_output["graph"]["directed_cycle_present"] is True, cycle_output
    assert cycle_output["graph"]["strongly_connected_components"] == [
        ["a", "b", "c"]
    ], cycle_output

    relabeled_cycle_payload = json.loads(json.dumps(cycle_payload))
    relabeled_cycle_payload["field"] = "imports"
    relabeled_cycle_output = analyze(
        relabeled_cycle_payload, _canonical_hash(relabeled_cycle_payload)
    )
    assert (
        relabeled_cycle_output["hard_invariants"]["static_cycle"]
        == "Not applicable"
    ), relabeled_cycle_output
    assert (
        relabeled_cycle_output["graph"]["directed_cycle_present"] is True
    ), relabeled_cycle_output

    undirected_scc_payload = json.loads(json.dumps(cycle_payload))
    undirected_scc_payload["directed"] = False
    try:
        analyze(undirected_scc_payload, _canonical_hash(undirected_scc_payload))
    except InputError:
        pass
    else:
        raise AssertionError("undirected scc input was accepted")

    duplicate_edge_payload = json.loads(json.dumps(payload))
    duplicate_edge_payload["edges"].append(
        {"source": "b", "target": "a", "weight": 5}
    )
    try:
        analyze(duplicate_edge_payload, _canonical_hash(duplicate_edge_payload))
    except InputError:
        pass
    else:
        raise AssertionError("duplicate undirected edge was accepted")

    unicode_payload = json.loads(json.dumps(cycle_payload))
    unicode_payload["dataset"]["source"] = "δοκιμή"
    unicode_payload["nodes"] = ["Ω", "α", "β"]
    unicode_payload["edges"] = [
        {"source": "Ω", "target": "α", "weight": 1},
        {"source": "α", "target": "β", "weight": 1},
        {"source": "β", "target": "Ω", "weight": 1},
    ]
    unicode_output = analyze(unicode_payload, _canonical_hash(unicode_payload))
    serialized_unicode = _serialize_output(unicode_output, pretty=False)
    serialized_unicode.encode("cp1252")
    assert json.loads(serialized_unicode) == unicode_output

    invalid_payload = json.loads(json.dumps(payload))
    del invalid_payload["analysis"]["decision_policy"]
    try:
        analyze(invalid_payload, _canonical_hash(invalid_payload))
    except InputError:
        pass
    else:
        raise AssertionError("missing decision policy was accepted")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze one evidence graph without choosing a software boundary. "
            "The input JSON must contain a predeclared decision policy for cuts."
        )
    )
    parser.add_argument("input", nargs="?", type=Path, help="input JSON file")
    parser.add_argument(
        "--pretty", action="store_true", help="indent the deterministic JSON output"
    )
    parser.add_argument(
        "--self-test", action="store_true", help="run embedded deterministic tests"
    )
    args = parser.parse_args(argv)
    if not args.self_test and args.input is None:
        parser.error("input is required unless --self-test is used")
    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        if args.self_test:
            _self_test()
            print("self-test: pass")
            return 0

        raw = args.input.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
        output = analyze(payload, hashlib.sha256(raw).hexdigest())
        print(_serialize_output(output, args.pretty))
        return 0
    except (InputError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except AssertionError as exc:
        print(f"SELF-TEST FAILED: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
