#!/usr/bin/env python3
"""Structural conformance checker for a routed Alchemy answer.

`check_topology_report.py` proves one placement record obeys its skill; this
proves the whole answer of an ADAPTIVE, FULL, or audit run obeys the output
contracts it carries: the four report blocks of the root instruction file,
the decision trail and scope block of `alchemy/references/adaptive-route.md`
§6, and the records of the stages that ran. Shape only, never judgement: it
cannot tell whether a score is right, only whether the record that holds it
is complete and consistent with the trail.

A consumer audit of 2026-11-20 broke these contracts in ways no check saw:
nine worth candidates carried a table row but no record, a test obligation
table lost two columns, a principle fell outside the fixed vocabulary, and
`Blocking stage: None` sat beside stages that still ran after a block.

Usage:
    check_alchemy_report.py <answer.md>     # check one routed answer
    check_alchemy_report.py --self-test     # prove the rules still bite
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _topology():
    spec = importlib.util.spec_from_file_location("check_topology_report", HERE / "check_topology_report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


topology = _topology()
BLOCK_RE, parse = topology.BLOCK_RE, topology.parse

# adaptive-route.md §6.
TRAIL_COLUMNS = ("stage", "skill", "decision", "evidence/hand-off", "files/checks", "next action or skip rationale")
SCOPE_FIELDS = ("Scope", "Mode", "Dispatch", "Companions", "Execution", "Blocking stage", "Decision", "Verification")
SCOPE_VOCABULARY = {
    "Mode": ("Design", "Refactor", "Audit"),
    "Dispatch": ("SKIP", "DIRECT", "ADAPTIVE", "FULL"),
    "Decision": ("Proceed", "Redesign", "Drop", "Defer"),
}
EXECUTION_VALUES = ("single-agent", "multi-agent")

# functionality-complexity-tradeoff §9.
WORTH_FIELDS = ("Subject", "Mode", "Necessity", "Outcome evidence", "Decision", "Rationale", "Next action", "Verification")
WORTH_SCORED_FIELDS = ("V scores", "C scores", "Confidence V", "Confidence C")
WORTH_DECISIONS = (
    "BUILD-minimal", "BUILD", "NEGOTIATE", "DEFER", "DROP", "KEEP", "SIMPLIFY",
    "QUARANTINE", "DEPRECATE", "DELETE", "OBSOLETE",
)
WORTH_REVISIT = ("DEFER", "QUARANTINE", "BUILD-minimal", "DEPRECATE")
SIGNED_SCORE_RE = re.compile(r"=\s*[+±−-]\s*\d")

# architecture-guidelines §11.
PRINCIPLES = (
    "YAGNI", "Rule of 3", "DRY", "SoC", "SRP", "capability-boundary", "DI", "fail-fast",
    "idempotency", "atomicity", "integration", "layer-self-sufficiency", "naming",
    "concurrency", "aspect",
)

# test-strategy Output Contract.
OBLIGATION_COLUMNS = (
    "risk/criterion", "failure mode", "oracle", "technique", "scope/fidelity",
    "dependencies", "data/environment", "evidence", "residual blind spot",
)

# A trail row that names one of these skills with a decision owes its record.
RECORD_MARKERS = {
    "functionality-complexity-tradeoff": "Necessity",
    "architecture-guidelines": "Principle",
    "morphogenetic-architecture": "Analysis mode",
    "test-strategy": "Strategy pass",
}

UNCHECKED_HEAD_RE = re.compile(r"^[ \t>#*_-]*What I did not check\b[^\n]*$", re.M)
NOTE_RE = re.compile(r"^\W*(?:not run|not triggered|not selected|deferred|skipped)\b", re.I)
LIST_ITEM_RE = re.compile(r"^[ \t>]*(?:[-*+]|\d+[.)])[ \t]+(?P<text>\S.*)$")


def cells(line: str) -> list[str] | None:
    row = line.strip(" \t>")
    if not row.startswith("|"):
        return None
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", row.strip().strip("|"))]


def normalize(cell: str) -> str:
    cell = re.sub(r"\s*/\s*", "/", cell.strip("*_` ").lower())
    return re.sub(r"\s+", " ", cell)


def tables(markdown: str) -> list[tuple[list[str], list[list[str]]]]:
    """Every pipe table: its normalized header and its body rows."""
    found: list[tuple[list[str], list[list[str]]]] = []
    current: tuple[list[str], list[list[str]]] | None = None
    for line in markdown.splitlines():
        row = cells(line)
        if row is None:
            current = None
            continue
        if current is None:
            current = ([normalize(cell) for cell in row], [])
            found.append(current)
        elif not all(re.fullmatch(r":?-{3,}:?", cell) for cell in row):
            current[1].append(row)
    return found


def words(value: str, vocabulary: tuple[str, ...]) -> list[str]:
    """Vocabulary words a field value names, longest first so BUILD-minimal is
    not also read as BUILD."""
    found, rest = [], value
    for word in sorted(vocabulary, key=len, reverse=True):
        pattern = re.compile(rf"(?<![\w-]){re.escape(word)}(?![\w-])")
        if pattern.search(rest):
            found.append(word)
            rest = pattern.sub(" ", rest)
    return found


def unchecked_items(markdown: str) -> list[str] | None:
    """Items of the What I did not check block: the text after its label, and
    every list item until the block ends at a blank line followed by prose, a
    fence, a table, a rule, a heading, or the next bold label."""
    match = UNCHECKED_HEAD_RE.search(markdown)
    if not match:
        return None
    head = re.sub(r"^[ \t>#*_-]*What I did not check\W*", "", match.group(0)).strip()
    items = [head] if head else []
    blank = False
    for line in markdown[match.end():].splitlines()[1:]:
        if not line.strip():
            blank = True
            continue
        item = LIST_ITEM_RE.match(line)
        if item:
            items.append(item.group("text").strip())
            blank = False
        elif blank or re.match(r"^[ \t]*(?:```|\||-{3,}|#|\*\*)", line):
            break
        elif items:
            items[-1] += " " + line.strip()
    return items


def names_row(blocking: str, row: list[str], stage_at: int, skill_at: int) -> bool:
    """`Blocking stage` names a trail row by its stage's first word, as in
    `M — DROP` for the row `M — Minimum`, or by the skill the row ran."""
    def head(text: str) -> str:
        match = re.match(r"\W*([^\W_]+)", text)
        return match.group(1).lower() if match else ""
    skill = re.search(r"[a-z]{3,}(?:-[a-z]+)+", row[skill_at])
    return bool(head(row[stage_at]) and head(row[stage_at]) == head(blocking)) or bool(skill and skill.group(0) in blocking)


def check(markdown: str, label: str) -> list[str]:
    """Return one message per violated rule; empty means conforming."""
    problems: list[str] = []

    def bad(rule: str, detail: str) -> None:
        problems.append(f"{label}: [{rule}] {detail}")

    blocks = [(block, parse(block)) for block in BLOCK_RE.findall(markdown)]
    scope = next((fields for _, fields in blocks if "Blocking stage" in fields), None)

    # T1-T3 — the decision trail.
    trail = None
    for header, rows in tables(markdown):
        if {"stage", "skill", "decision"} <= set(header):
            trail = (header, rows)
            if tuple(header) != TRAIL_COLUMNS:
                bad("T1", f"trail columns are {header}, expected {list(TRAIL_COLUMNS)}")
            break
    rows = []
    if trail:
        header, rows = trail
        stage_at, skill_at, decision_at = (header.index(name) for name in ("stage", "skill", "decision"))
        rows = [row + [""] * (len(header) - len(row)) for row in rows]
        previous = None
        for row in rows:
            if not re.search(r"\w", row[-1]):
                bad("T2", f"trail row '{row[stage_at]}' has no next action or skip rationale")
            number = re.match(r"\D*?(\d+)", row[stage_at])
            if number:
                value = int(number.group(1))
                if previous is not None and value not in (previous, previous + 1):
                    bad("T3", f"trail stage {value} follows stage {previous}")
                previous = value

    # S1-S3 — the scope block.
    if scope is None:
        bad("S1", "no scope block with 'Blocking stage:'")
    else:
        for field in SCOPE_FIELDS:
            if field not in scope:
                bad("S1", f"scope block missing '{field}:'")
        for field, vocabulary in SCOPE_VOCABULARY.items():
            named = words(scope.get(field, ""), vocabulary)
            if field in scope and len(named) != 1:
                bad("S2", f"scope '{field}:' must name exactly one of {list(vocabulary)}, found {named or 'none'}")
        execution = scope.get("Execution", "")
        if "Execution" in scope and not execution.startswith(EXECUTION_VALUES):
            bad("S2", f"scope 'Execution:' must open with single-agent or multi-agent, found '{execution[:30]}'")
        blocking = scope.get("Blocking stage", "")
        if trail and blocking and not re.match(r"^none\b", blocking, re.I):
            at = next((index for index, row in enumerate(rows) if names_row(blocking, row, stage_at, skill_at)), None)
            if at is None:
                bad("S3", f"'Blocking stage: {blocking[:40]}' names no trail row")
            else:
                for row in rows[at + 1:]:
                    if re.search(r"\w", row[decision_at]) and not NOTE_RE.search(row[decision_at]):
                        bad("S3", f"stage '{row[stage_at]}' after the blocking stage has decision '{row[decision_at][:30]}'")

    # R1 — a stage the trail gives a decision emits its record.
    if trail:
        for row in rows:
            decision = row[decision_at]
            if not re.search(r"\w", decision) or NOTE_RE.search(decision):
                continue
            for skill, marker in RECORD_MARKERS.items():
                if skill in row[skill_at] and not any(marker in fields for _, fields in blocks):
                    bad("R1", f"trail row '{row[stage_at]}' decides {skill} but no record carries '{marker}:'")

    # M1-M4 — worth records.
    for block, fields in blocks:
        if "Necessity" not in fields:
            continue
        subject = fields.get("Subject", "?")[:40]
        for field in WORTH_FIELDS:
            if field not in fields:
                bad("M1", f"worth record '{subject}' missing '{field}:'")
        passed = fields.get("Necessity", "").lower().startswith("pass")
        for field in WORTH_SCORED_FIELDS:
            if passed and field not in fields:
                bad("M2", f"worth record '{subject}' passed necessity but omits '{field}:'")
        decision = words(fields.get("Decision", ""), WORTH_DECISIONS)
        if len(decision) != 1:
            bad("M3", f"worth record '{subject}' Decision must name one word, found {decision or 'none'}")
        elif decision[0] in WORTH_REVISIT and not re.search(
            r"\w", re.sub(r"^\W*(?:none|not required|n/?a)\b.*", "", fields.get("Revisit when", ""), flags=re.I)
        ):
            bad("M3", f"worth record '{subject}' {decision[0]} requires 'Revisit when:'")
        if fields.get("Mode", "").startswith("Retrospective") and SIGNED_SCORE_RE.search(fields.get("C scores", "")):
            bad("M4", f"retrospective worth record '{subject}' gives C scores as deltas, not measured absolutes")

    # A1 — design records name principles from the fixed vocabulary.
    known = {principle.lower() for principle in PRINCIPLES}
    for _, fields in blocks:
        if "Principle" not in fields:
            continue
        value = re.sub(r"\([^)]*\)", "", fields["Principle"])
        for token in re.split(r"\s*(?:[,;/+|]|\band\b)\s*", value):
            if token.strip() and token.strip().lower() not in known:
                bad("A1", f"principle '{token.strip()}' is outside the fixed vocabulary")

    # O1 — the test obligation table keeps every column.
    for header, _ in tables(markdown):
        if "oracle" in header and "failure mode" in header and tuple(header) != OBLIGATION_COLUMNS:
            missing = [column for column in OBLIGATION_COLUMNS if column not in header]
            bad("O1", f"obligation table columns are {header}; missing {missing}")

    # L1 — placement records pass their own checker.
    for block, fields in blocks:
        if "Analysis mode" in fields:
            for problem in topology.check(block, "placement record"):
                bad("L1", problem)

    # B1-B2 — the What I did not check block.
    items = unchecked_items(markdown)
    if items is None:
        bad("B1", "no 'What I did not check' block")
    else:
        for item in items:
            if not re.match(r"^\W*nothing\b", item, re.I) and "`" not in item:
                bad("B1", f"unchecked item names no closing command: '{item[:50]}'")
        audit = scope is not None and scope.get("Mode", "").startswith("Audit")
        if audit and not any("correctness" in item.lower() for item in items):
            bad("B2", "an audit's 'What I did not check' must name functional correctness")

    return problems


CONFORMING = """
**What I found:** The export subsystem's retry wrapper repeats what the queue
already guarantees: delete it (the record calls this OBSOLETE). The queue
redelivers on every failure.

**Why it matters:** Removing it drops one subsystem and two edges. Keeping it
leaves a second retry path that hides queue failures.

**Do this first:**

1. Delete `export/retry.py` and run `pytest tests/export`.

**What I did not check:**

- Functional correctness of the export logic: run `/code-review`.
- Queue redelivery under load: run `pytest tests/queue -m load`.

| Stage | Skill | Decision | Evidence / hand-off | Files/checks | Next action or skip rationale |
| --- | --- | --- | --- | --- | --- |
| 1 | `structural-simplification` C₀ | Baseline scored | 5 kinds, 9 edges | `export/` | Bound recovery to export |
| 2 | `requirements-grounding` | Not run | Intent is current | - | Skipped: README states intent |
| 3 | `functionality-complexity-tradeoff` | OBSOLETE | Queue redelivers | `export/retry.py` | Remediation increment: delete |
| 4 | `architecture-guidelines` | Proceed | Removal keeps the queue edge | `export/` | Gate L next |
| 5 | `morphogenetic-architecture` | KEEP | Position legal | `export/` | No boundary moves |
| 6 | `test-strategy` | PARTIAL | Redelivery untested | `tests/queue` | Add the load test |

| Risk / criterion | Failure mode | Oracle | Technique | Scope / fidelity | Dependencies | Data / environment | Evidence | Residual blind spot |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Redelivery | Lost job | Job count | Fault injection | Integration | Real queue | Seeded queue | None yet | Broker failover |

```
Scope:          export subsystem
Mode:           Audit
Dispatch:       FULL
Companions:     test-strategy
Execution:      single-agent - one subsystem, no independent parts
Blocking stage: None
Decision:       Proceed
Verification:   Not run - read-only audit
```

```
Subject:        export/retry.py
Mode:           Retrospective
Necessity:      Pass
Necessity note: The wrapper still runs on every export.
V scores:       U=0  F=0  R=1  I=0
C scores:       Subsystem-kinds=1  Dependency-edges=2
                Max-chain-depth=1  Subsystem-count=1
                Maintenance=1  Risk=2  Evolution=1
Confidence V:   High
Confidence C:   High
Outcome evidence: not applicable
Decision:       OBSOLETE
Rationale:      The queue redelivers every failed job, so the wrapper retries
                work that is already retried.
Next action:    Delete export/retry.py.
Verification:   Not run - read-only audit
```

```
Subject:        export/retry.py removal
Decision:       Proceed
Principle:      YAGNI, SoC
Evidence:       export/worker.py imports retry once
Enforcement:    none
Next action:    Delete the import with the module.
Verification:   Not run - read-only audit
```

```
Subject:             export
Mode:                Audit
Analysis mode:       Rapid
Selection reason:    Bounded placement check; no boundary moves.
Decision:            KEEP
Declared topology:   export / capability / application
Position legality:   Pass
Static cycle:        Pass
Runtime cycles:      none
Observed fields:     Static = checked; change = Not measured
Boundary evidence:   Not required - no boundary moves.
Enforcement:         none
Next action:         None.
Verification:        Not run - read-only audit
```

```
Subject:              export redelivery
Mode:                 Audit
Strategy pass:        Combined
Decision:             PARTIAL
Next action:          Add the load test.
Verification:         Not run - read-only audit
```
""".strip()

# Each mutation must trip exactly the rule it is named for; each reproduces a
# break the 2026-11-20 consumer audit shipped, or the shape that would hide it.
SELF_TEST_CASES = (
    ("T1", ("| Evidence / hand-off | Files/checks |", "| Evidence | Files/checks |")),
    ("T2", ("| Skipped: README states intent |", "|  |")),
    ("T3", ("| 6 | `test-strategy` |", "| 8 | `test-strategy` |")),
    ("S1", ("Companions:     test-strategy\n", "")),
    ("S2", ("Dispatch:       FULL", "Dispatch:       FULL audit, ADAPTIVE")),
    ("S3", ("Blocking stage: None", "Blocking stage: 3 functionality-complexity-tradeoff")),
    ("R1", ("Necessity:      Pass", "Need:           Pass")),
    ("M2", ("Confidence V:   High\n", "")),
    ("M3", ("Decision:       OBSOLETE", "Decision:       DEFER")),
    ("M4", ("Subsystem-kinds=1  Dependency-edges=2", "Subsystem-kinds Δ=-1  Dependency-edges Δ=-2")),
    ("A1", ("Principle:      YAGNI, SoC", "Principle:      Dependency discipline, Functional core / DI")),
    ("O1", ("| Dependencies | Data / environment | Evidence |", "| Evidence |")),
    ("L1", ("Static cycle:        Pass\n", "")),
    ("B1", ("Queue redelivery under load: run `pytest tests/queue -m load`.", "Queue redelivery under load.")),
    ("B2", ("Functional correctness of the export logic", "The export logic")),
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
        tripped = {p.split("[")[1].split("]")[0] for p in check(CONFORMING.replace(old, new, 1), "mutant")}
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
    path = Path(argv[0])
    problems = check(path.read_text(encoding="utf-8"), path.name)
    for problem in problems:
        print(f"ERROR: {problem}")
    if problems:
        return 1
    print("answer conforms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
