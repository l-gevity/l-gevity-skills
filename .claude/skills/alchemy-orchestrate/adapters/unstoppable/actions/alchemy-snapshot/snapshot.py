#!/usr/bin/env python3
"""Unstoppable Code project action: record the head and the diff of an ALCHEMY run.

Read-only reviewers on some harnesses cannot run git, so the integrated diff is
produced here, by code, rather than by the agent whose work is under review.
Inputs arrive as INPUT_<NAME>; outputs are appended as key=value lines to
$UNSTOPPABLE_CODE_OUTPUT; the diff is kept under $UNSTOPPABLE_CODE_OUTPUT_DIR.
"""

from __future__ import annotations

import os
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


class InputError(Exception):
    """Input the action cannot use; the step fails with exit 2."""


def repo_root() -> Path:
    start = Path.cwd().resolve()
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise InputError(f"no git repository at or above {start}")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-c", "core.quotepath=off", "-C", str(root), *args],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise InputError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def output_dir() -> Path:
    configured = os.environ.get("UNSTOPPABLE_CODE_OUTPUT_DIR", "").strip()
    if configured:
        path = Path(configured)
    elif os.environ.get("UNSTOPPABLE_CODE_OUTPUT", "").strip():
        path = Path(os.environ["UNSTOPPABLE_CODE_OUTPUT"]).parent
    else:
        path = Path(tempfile.mkdtemp(prefix="alchemy-snapshot-"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def emit(outputs: dict[str, str]) -> None:
    lines = [f"{key}={' '.join(str(value).split())}" for key, value in outputs.items()]
    target = os.environ.get("UNSTOPPABLE_CODE_OUTPUT", "").strip()
    if target:
        with open(target, "a", encoding="utf-8", newline="\n") as handle:
            handle.write("".join(line + "\n" for line in lines))
    for line in lines:
        print(line)


def review_base(root: Path, base: str, ledger_path: str) -> str:
    """A correction starts at the last reviewed ledger head, never plan base."""
    if not ledger_path:
        return base
    if base:
        raise InputError("base and base_ledger are mutually exclusive")
    try:
        ledger = json.loads((root / ledger_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise InputError(f"cannot read review ledger: {exc}") from exc
    if not isinstance(ledger, dict) or ledger.get("schema") != "alchemy-ledger/1" or not \
            re.fullmatch(r"[0-9a-fA-F]{7,64}", str(ledger.get("head_commit", ""))):
        raise InputError("review ledger needs schema alchemy-ledger/1 and a valid head_commit")
    return ledger["head_commit"]


def main() -> int:
    try:
        root = repo_root()
        head = git(root, "rev-parse", "HEAD").strip()
        branch = git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
        status = git(root, "status", "--porcelain", "--untracked-files=normal")
        outputs = {"head_commit": head, "branch": branch, "dirty": "true" if status.strip() else "false",
                   "changed_files": "", "diff_file": ""}
        ledger_path = os.environ.get("INPUT_BASE_LEDGER", "").strip()
        base = review_base(root, os.environ.get("INPUT_BASE", "").strip(), ledger_path)
        outputs["base_commit"] = ""
        if base:
            base = git(root, "rev-parse", "--verify", f"{base}^{{commit}}").strip()
            if ledger_path:
                git(root, "merge-base", "--is-ancestor", base, head)
            outputs["base_commit"] = base
            names = [line for line in git(root, "diff", "--name-only", base).splitlines() if line]
            untracked = [line for line in git(root, "ls-files", "--others", "--exclude-standard").splitlines()
                         if line]
            diff = git(root, "diff", "--no-color", "--no-ext-diff", "--find-renames", base)
            header = [f"# ALCHEMY integrated diff: base {base}, head {head}, "
                      f"uncommitted changes {'present' if status.strip() else 'none'}",
                      f"# Untracked files not shown below: {', '.join(untracked) or 'none'}", ""]
            diff_file = output_dir() / f"alchemy-diff-{base[:12]}-{head[:12]}.patch"
            with open(diff_file, "w", encoding="utf-8", newline="\n") as handle:
                handle.write("\n".join(header) + diff)
            outputs["changed_files"] = str(len(set(names) | set(untracked)))
            outputs["diff_file"] = str(diff_file)
        emit(outputs)
    except (InputError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if os.environ.get("INPUT_REQUIRE_CLEAN", "").strip().lower() == "true" and status.strip():
        print("ERROR: uncommitted changes outside ignored paths:", file=sys.stderr)
        print(status.rstrip(), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
