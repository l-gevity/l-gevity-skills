#!/usr/bin/env python3
"""Run the plan's command criteria and the profile's verification commands once,
at a clean committed head, and record each result as ledger evidence.

The lead runs this on the integrated head (SKILL.md section 4 step 7). A
verifier then reads the log and cites the evidence ID instead of running the
same command on the same commit again: the record is written by code, so it is
evidence, not an agent's claim.

Usage:
    record_evidence.py --plan <plan.json> --root <repository>
                       [--criterion <id>]... [--verification]
                       [--profile <alchemy-workspace.json>] [--out <dir>] [--timeout <seconds>]

Runs only commands the plan or the profile declares; it takes no command of its
own. Without --criterion or --verification it runs all of them.
--reuse-identical runs each exact command once within this invocation, retaining
one record and log per criterion (aliases name reused_from). Opt in only for
repeat-safe checks with stable inputs and environment; sampling, state changes,
and order-dependent checks must execute separately. No cross-run cache exists. Refuses a
repository whose HEAD is not committed and clean outside the state directory.
Writes `<id>.log` (combined stdout and stderr) and `<id>.json` (one
`evidence[]` item of the ledger) per command into --out, default `evidence/`
beside the plan, which must lie under the profile's state_dir when it is inside
the repository. Prints one JSON report. Exit 0 when every command exited 0 and
the work tree stayed clean, 1 otherwise, 2 on unreadable input or bad usage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_orchestration as checker  # noqa: E402  (same directory, loaded by path)

TIMEOUT_EXIT = 124
UNSAFE = re.compile(r"[^A-Za-z0-9._@-]")


def plan_commands(plan: Any) -> list[dict[str, str]]:
    """Every `command` criterion of the plan, amendment packages included."""
    if not isinstance(plan, dict):
        raise checker.InputError("the plan must be a JSON object")
    packages = list(plan.get("packages") or [])
    packages += [a.get("package") for a in plan.get("amendments") or [] if isinstance(a, dict)]
    found: list[dict[str, str]] = []
    for pkg in packages:
        if not isinstance(pkg, dict):
            continue
        for item in pkg.get("acceptance") or []:
            if isinstance(item, dict) and item.get("check") == "command" and checker._command(item.get("command")):
                found.append({"criterion": item.get("id"), "command": item["command"]})
    return found


def profile_commands(view: dict[str, Any]) -> list[dict[str, str]]:
    return [{"verification": entry["id"] or f"verify-{index}", "command": entry["command"]}
            for index, entry in enumerate(view["verification"], 1)]


def select(plan: Any, view: dict[str, Any], criteria: list[str], verification: bool) -> list[dict[str, str]]:
    planned = plan_commands(plan)
    if not criteria and not verification:
        return planned + profile_commands(view)
    known = {item["criterion"]: item for item in planned}
    missing = [cid for cid in criteria if cid not in known]
    if missing:
        raise checker.InputError(f"no command criterion in the plan has id {', '.join(missing)}")
    chosen = [known[cid] for cid in dict.fromkeys(criteria)]
    return chosen + (profile_commands(view) if verification else [])


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def run_one(item: dict[str, str], root: Path, out: Path, commit: str, timeout: int,
            previous: dict[str, Any] | None = None) -> dict[str, Any]:
    label = item.get("criterion") or item["verification"]
    eid = f"{label}@{commit[:7]}"
    stem = UNSAFE.sub("_", eid)
    log = out / f"{stem}.log"
    if previous is not None:
        output = (root / previous["log"]).read_bytes()
        exit_code = previous["exit_code"]
    else:
        try:
            proc = subprocess.run(item["command"], shell=True, cwd=root, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, timeout=timeout)
            output, exit_code = proc.stdout, proc.returncode
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or b"") + f"\n[record_evidence: timed out after {timeout} s]\n".encode()
            exit_code = TIMEOUT_EXIT
    log.write_bytes(output)
    record: dict[str, Any] = {
        "id": eid,
        "command": item["command"],
        "exit_code": exit_code,
        "commit": commit,
        "produced_by": "harness",
        "log": _relative(log, root),
        "log_sha256": hashlib.sha256(output).hexdigest(),
    }
    if item.get("criterion"):
        record["criterion"] = item["criterion"]
    if previous is not None:
        record["reused_from"] = previous["id"]
    (out / f"{stem}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def record(plan_path: Path, root: Path, profile: dict[str, Any], criteria: list[str], verification: bool,
           out: Path | None, timeout: int, reuse_identical: bool = False) -> dict[str, Any]:
    view = checker._profile_view(profile, checker.Report("profile"))
    plan = checker._read_json(plan_path)
    commands = select(plan, view, criteria, verification)
    if not commands:
        raise checker.InputError("the plan has no command criterion and the profile no verification command")
    out = out if out is not None else plan_path.parent / "evidence"
    state_dir = view["state_dir"]
    if _inside(out, root):
        relative = _relative(out, root).casefold()
        base = (state_dir or "").rstrip("/").casefold()
        if not base or not (relative == base or relative.startswith(base + "/")):
            raise checker.InputError(f"--out {_relative(out, root)} lies in the repository outside state_dir "
                                     f"{state_dir}; the log would dirty the work tree")
    problems, ran = checker._workspace_problems(root, [], state_dir, "")
    if problems or not ran:
        raise checker.InputError("evidence needs a committed, clean head: " + "; ".join(problems))
    head, error = checker._git(root, "rev-parse", "HEAD")
    if error:
        raise checker.InputError(error)
    commit = head.strip()
    out.mkdir(parents=True, exist_ok=True)
    evidence = []
    # Invocation-local only: no result survives a head, environment, or run change.
    reusable = {}
    for item in commands:
        entry = run_one(item, root, out, commit, timeout,
                        reusable.get(item["command"]) if reuse_identical else None)
        evidence.append(entry)
        reusable.setdefault(item["command"], entry)
    after, _ = checker._workspace_problems(root, [commit], state_dir, "the head the commands ran on")
    passed = all(item["exit_code"] == 0 for item in evidence) and not after
    return {
        "verdict": "PASS" if passed else "FAIL",
        "commit": commit,
        "evidence": evidence,
        # A command that changed tracked files or left untracked ones did not
        # run on the commit alone; its evidence is not anchored to it.
        "workspace_after": after,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record plan and profile check results as ledger evidence.")
    parser.add_argument("--plan", type=Path, required=True, help="alchemy-plan/1 JSON file")
    parser.add_argument("--root", type=Path, required=True, help="repository at the head to record")
    parser.add_argument("--criterion", action="append", default=[], help="a command criterion id; repeatable")
    parser.add_argument("--verification", action="store_true", help="the profile's repository.verification")
    parser.add_argument("--profile", type=Path, help=f"project profile; {checker.PROJECT_PROFILE} at --root "
                        "when omitted and present")
    parser.add_argument("--out", type=Path, help="directory for logs and records; default evidence/ beside the plan")
    parser.add_argument("--timeout", type=int, default=1800, help="seconds per command (default 1800)")
    parser.add_argument("--reuse-identical", action="store_true",
                        help="reuse exact commands within this invocation; only for repeat-safe checks "
                        "with stable inputs and environment, never sampling or state-changing commands")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if not args.root.is_dir():
            raise checker.InputError(f"{args.root}: --root is not a directory")
        profile_path = args.profile
        if profile_path is None and (args.root / checker.PROJECT_PROFILE).is_file():
            profile_path = args.root / checker.PROJECT_PROFILE
        profile = checker.load_profile(profile_path)
        result = record(args.plan, args.root, profile, args.criterion, args.verification, args.out,
                        args.timeout, args.reuse_identical)
    except checker.InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    result["profile"] = str(profile_path) if profile_path is not None else "defaults"
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
