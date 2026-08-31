#!/usr/bin/env python3
"""Structural conformance checker for `morphogenetic-architecture` reports.

`validate-skills.py` proves the skill *says* the right thing. This proves a
produced report *obeys* it. Everything here is shape-checking against a fixed
template, never judgement: it cannot tell whether an analyst really ran
`git log`, only whether the report is internally complete and consistent.

Usage:
    check_topology_report.py <report-file>      # check one report block
    check_topology_report.py --samples <md>     # check every topology block
    check_topology_report.py --self-test        # prove the rules still bite
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Emitted in every report — SKILL.md §8.
CORE_FIELDS = (
    "Subject",
    "Mode",
    "Analysis mode",
    "Selection reason",
    "Decision",
    "Declared topology",
    "Position legality",
    "Static cycle",
    "Runtime cycles",
    "Observed fields",
    "Boundary evidence",
    "Enforcement",
    "Next action",
    "Verification",
)

# Emitted only when a boundary actually moves, or a DEFER withholds one.
RESTRUCTURING_FIELDS = (
    "Decision policy",
    "Graph analysis",
    "Candidate baseline",
    "Second candidate",
    "Reversibility",
    "Prediction",
    "Measurement",
)

DECISIONS = (
    "PLACE",
    "KEEP",
    "MOVE",
    "SPLIT",
    "MERGE",
    "INTRODUCE-BOUNDARY",
    "DECLARE-RUNTIME-CYCLE",
    "DEFER",
)
RESTRUCTURING_DECISIONS = ("MOVE", "SPLIT", "MERGE", "INTRODUCE-BOUNDARY")
POSITION_ONLY_DECISIONS = ("PLACE", "KEEP", "DECLARE-RUNTIME-CYCLE")

# Retired by the B2 refactor; a lens now reaches the report via Second candidate.
RETIRED_FIELDS = ("Natural lens", "Lens contribution", "Lens falsifier", "Transfer")

GENERATORS = ("algorithmic cut", "natural lens", "manual")

FIELD_RE = re.compile(r"^(?P<name>[A-Z][A-Za-z ]*):[ \t]*(?P<value>.*)$")
BLOCK_RE = re.compile(r"```(?:text)?[ \t]*\r?\n(.*?)```", re.S)
NOT_REQUIRED_RE = re.compile(r"^not required\b", re.I)


def parse(report: str) -> dict[str, str]:
    """Map field name to its value, folding indented continuation lines in."""
    fields: dict[str, str] = {}
    current: str | None = None
    for line in report.splitlines():
        if not line.strip():
            continue
        match = FIELD_RE.match(line)
        if match:
            current = match.group("name")
            fields[current] = match.group("value").strip()
        elif current is not None:
            fields[current] = (fields[current] + " " + line.strip()).strip()
    return fields


def check(report: str, label: str) -> list[str]:
    """Return one message per violated rule; empty means conforming."""
    fields = parse(report)
    problems: list[str] = []

    def bad(rule: str, detail: str) -> None:
        problems.append(f"{label}: [{rule}] {detail}")

    # R1 — core fields are unconditional.
    for field in CORE_FIELDS:
        if field not in fields:
            bad("R1", f"missing core field '{field}:'")

    # R9 — fields the B2 refactor removed must not reappear.
    for field in RETIRED_FIELDS:
        if field in fields:
            bad("R9", f"retired field '{field}:' must not appear")

    decision_value = fields.get("Decision", "")
    matched = [d for d in DECISIONS if re.search(rf"\b{re.escape(d)}\b", decision_value)]
    # INTRODUCE-BOUNDARY and DECLARE-RUNTIME-CYCLE are not substrings of others,
    # so an exact single match is the only conforming shape.
    if len(matched) != 1:
        bad(
            "R2",
            f"Decision must name exactly one vocabulary word, found {matched or 'none'}",
        )
        return problems
    decision = matched[0]

    present = [f for f in RESTRUCTURING_FIELDS if f in fields]

    # R3 / R4 — the restructuring set rides the reversibility-grade trigger.
    if decision in RESTRUCTURING_DECISIONS:
        for field in RESTRUCTURING_FIELDS:
            if field not in fields:
                bad("R3", f"{decision} requires restructuring field '{field}:'")
    elif decision in POSITION_ONLY_DECISIONS:
        for field in present:
            bad("R4", f"{decision} must omit restructuring field '{field}:'")
    # DEFER may or may not carry the set: only a DEFER that withholds a
    # restructuring needs it, and the report alone cannot say which it is.

    # R5 — an accepted restructuring cannot waive its own proof.
    if decision in RESTRUCTURING_DECISIONS:
        for field in ("Measurement", "Prediction", "Reversibility"):
            value = fields.get(field, "")
            if NOT_REQUIRED_RE.match(value):
                bad("R5", f"{decision} cannot mark '{field}:' Not required")

    boundary = fields.get("Boundary evidence", "")
    probationary = boundary.lower().lstrip().startswith("probationary")

    # R6 — probation carries its whole record or it is not probation.
    if probationary:
        required_parts = {
            "why unmeasurable": ("cannot be measured", "unmeasurable", "not measurable"),
            "expiry": ("expiry", "revisit"),
            "instrumentation": ("instrumentation",),
            "reversal path": ("reversal path",),
        }
        low = boundary.lower()
        for part, needles in required_parts.items():
            if not any(n in low for n in needles):
                bad("R6", f"probationary Boundary evidence omits {part}")
        reversibility = fields.get("Reversibility", "").lower().lstrip()
        if not reversibility.startswith(("high", "medium")):
            bad(
                "R6",
                "probation requires High, or Medium with a named reversal path; "
                f"found '{fields.get('Reversibility', '')[:40]}'",
            )
        if NOT_REQUIRED_RE.match(fields.get("Prediction", "")):
            bad("R6", "probation requires a Prediction, not 'Not required'")

    # R7 — `none` must account for every generator, not just assert absence.
    second = fields.get("Second candidate", "")
    if second.lower().lstrip().startswith("none"):
        for generator in GENERATORS:
            if generator not in second.lower():
                bad("R7", f"'Second candidate: none' does not account for '{generator}'")

    # R8 — the reversibility bar on probation, stated from the other side.
    reversibility_value = fields.get("Reversibility", "").lower().lstrip()
    if reversibility_value.startswith(("low", "unknown")) and probationary:
        bad("R8", "Low or Unknown reversibility can never be accepted probationarily")

    return problems


def topology_blocks(markdown: str) -> list[str]:
    """Fenced blocks whose Decision names a morphogenetic vocabulary word."""
    blocks = []
    for block in BLOCK_RE.findall(markdown):
        fields = parse(block)
        value = fields.get("Decision", "")
        if any(re.search(rf"\b{re.escape(d)}\b", value) for d in DECISIONS):
            blocks.append(block)
    return blocks


CONFORMING = """
Subject:             notifications/scheduling-contract
Mode:                Design
Analysis mode:       Rapid -> Full
Selection reason:    INTRODUCE-BOUNDARY became a candidate.
Decision:            INTRODUCE-BOUNDARY
Declared topology:   notifications / capability / application
Position legality:   Fail: cross-domain coupling on dispatcher -> schedule-store
Static cycle:        Pass
Runtime cycles:      none
Observed fields:     Static = checked; change = Not measured
Decision policy:     Change affinity - baseline = 20 merges; >= 80% local.
Graph analysis:      Not required - no algorithmic cut generated the candidate.
Candidate baseline:  One scheduling contract between dispatcher and store.
Second candidate:    none - algorithmic cut: attempted, no weighted graph at this
                     depth; natural lens: attempted, the index routes nothing;
                     manual alternative: attempted, falls on the same edge.
Boundary evidence:   probationary - separate owners and retry semantics; change
                     affinity cannot be measured at 7 of 20 merges; expiry at
                     merge 20; instrumentation: co-change report; reversal path:
                     collapse the contract back into the dispatcher.
Reversibility:       medium - three internal call sites share the contract.
Prediction:          Cluster-local change reaches >= 80% over merges 1-20.
Enforcement:         add architecture rule: forbid dispatcher -> schedule-store
Measurement:         Proceed - Component-kinds +1; Dependency-edges 0.
Next action:         Add the contract and enable the co-change report.
Verification:        Architecture lint plus the expiry comparison.
""".strip()

# Each mutation must trip exactly the rule it is named for.
SELF_TEST_CASES = (
    ("R1", ("Static cycle:        Pass\n", "")),
    ("R9", ("Runtime cycles:      none", "Transfer:            mechanism\nRuntime cycles:      none")),
    ("R2", ("Decision:            INTRODUCE-BOUNDARY", "Decision:            REORGANIZE")),
    ("R3", ("Prediction:          Cluster-local change reaches >= 80% over merges 1-20.\n", "")),
    ("R5", ("Measurement:         Proceed - Component-kinds +1; Dependency-edges 0.",
            "Measurement:         Not required - nothing to measure.")),
    ("R6", ("affinity cannot be measured at 7 of 20 merges; expiry at",
            "affinity was skipped; expiry at")),
    ("R7", ("manual alternative: attempted, falls on the same edge.", "that is all.")),
    ("R8", ("Reversibility:       medium - three internal call sites share the contract.",
            "Reversibility:       low - external consumers depend on the contract.")),
)


def self_test() -> int:
    failures = []

    problems = check(CONFORMING, "conforming")
    if problems:
        failures.append("conforming fixture rejected: " + "; ".join(problems))

    for rule, (old, new) in SELF_TEST_CASES:
        if old not in CONFORMING:
            failures.append(f"{rule}: fixture anchor missing")
            continue
        mutated = CONFORMING.replace(old, new, 1)
        tripped = {p.split("[")[1].split("]")[0] for p in check(mutated, "mutant")}
        if rule not in tripped:
            failures.append(f"{rule}: mutation not caught (tripped {sorted(tripped)})")

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1
    print("self-test: pass")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2

    if argv[0] == "--self-test":
        return self_test()

    if argv[0] == "--samples":
        if len(argv) < 2:
            print("ERROR: --samples needs a markdown path")
            return 2
        path = Path(argv[1])
        blocks = topology_blocks(path.read_text(encoding="utf-8"))
        if not blocks:
            print(f"ERROR: {path} contains no topology report block")
            return 1
        problems = []
        for index, block in enumerate(blocks, 1):
            problems.extend(check(block, f"{path.name} block {index}"))
        for problem in problems:
            print(f"ERROR: {problem}")
        if problems:
            return 1
        print(f"{len(blocks)} topology reports conform")
        return 0

    path = Path(argv[0])
    problems = check(path.read_text(encoding="utf-8"), path.name)
    for problem in problems:
        print(f"ERROR: {problem}")
    if problems:
        return 1
    print("report conforms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
