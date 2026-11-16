#!/usr/bin/env python3
"""Unstoppable Code project action: run alchemy-orchestrate's check_orchestration.py.

Inputs arrive as INPUT_<NAME> environment variables (see action.yml). Outputs
are appended as key=value lines to $UNSTOPPABLE_CODE_OUTPUT, and the JSON
report is kept under $UNSTOPPABLE_CODE_OUTPUT_DIR. The checker is found in the
repository's skills tree, never copied here, so the rules stay in one place.

Exit 0 when the verdict is PASS or ACCEPT, or when enforce is "false"; 1 on any
other verdict; 2 on unreadable input.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

SKILL = "alchemy-orchestrate"
SKILL_ROOTS = (".agents/skills", ".claude/skills")
PROFILE_NAME = "alchemy-workspace.json"
MODES = ("plan", "preflight", "handoff", "gate")
PASSING = ("PASS", "ACCEPT")
# Verdict precedence from references/contracts.md: ESCALATE over REJECT/FAIL
# over STALE over RETRY over a pass.
RANK = {"PASS": 0, "ACCEPT": 0, "RETRY": 1, "STALE": 2, "FAIL": 3, "REJECT": 3, "ESCALATE": 4}
HEAD_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")


class InputError(Exception):
    """Input the action cannot use; the step fails with exit 2."""


def option(name: str, default: str = "") -> str:
    return os.environ.get(f"INPUT_{name.upper()}", default).strip()


def flag(name: str, default: str) -> bool:
    value = option(name, default).lower() or default
    if value not in ("true", "false"):
        raise InputError(f"input {name} must be true or false, not {value!r}")
    return value == "true"


def repo_root() -> Path:
    start = Path.cwd().resolve()
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    raise InputError(f"no git repository at or above {start}")


def skill_dir(root: Path) -> Path:
    searched = []
    for tree in SKILL_ROOTS:
        candidate = root / tree / SKILL
        searched.append(str(candidate / "scripts" / "check_orchestration.py"))
        if (candidate / "scripts" / "check_orchestration.py").is_file():
            return candidate
    raise InputError("check_orchestration.py not found; searched " + ", ".join(searched))


def resolve(raw: str, root: Path) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else root / path


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_bytes().decode("utf-8-sig"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise InputError(f"{path}: {exc}") from exc


def deep_merge(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def inside(value: Any, label: str, root: Path) -> str:
    """A '/'-separated path strictly inside root, refused by Windows or POSIX rules alike."""
    if not isinstance(value, str):
        raise InputError(f"{label} must be a string, not {value!r}")
    text = value.strip()
    parts = text.replace("\\", "/").split("/")
    problem = ""
    if not text:
        problem = "is empty"
    elif text[0] in "/\\":
        problem = "is absolute (a leading slash, backslash, or UNC prefix)"
    elif ":" in text:
        problem = "contains ':' (a drive letter such as C: or D:x, or a stream name)"
    elif ".." in parts:
        problem = "contains a '..' segment"
    elif not [part for part in parts if part not in ("", ".")]:
        problem = "names the root itself"
    else:
        base = root.resolve()
        target = (base / "/".join(parts)).resolve()
        if base not in target.parents:
            problem = "does not resolve strictly inside the repository"
    if problem:
        raise InputError(f"{label} {value!r} {problem}")
    return "/".join(part for part in parts if part not in ("", "."))


def state_dir(skill: Path, profile: Path | None, root: Path) -> str:
    merged = read_json(skill / "assets" / PROFILE_NAME)
    if profile is not None:
        overlay = read_json(profile)
        if not isinstance(overlay, dict):
            raise InputError(f"{profile}: a profile must be a JSON object")
        merged = deep_merge(merged, overlay)
    repository = merged.get("repository") if isinstance(merged.get("repository"), dict) else {}
    return inside(repository.get("state_dir", ".alchemy/runs/"), "repository.state_dir", root)


def integrated_heads() -> list[str]:
    """Heads the lead integrated a wave at, from comma- or space-separated input."""
    heads = [token for token in re.split(r"[\s,]+", option("integrated")) if token]
    bad = [token for token in heads if not HEAD_RE.match(token)]
    if bad:
        raise InputError(f"input integrated holds non-commit values {', '.join(bad)}; "
                         "expected hex commit IDs of 7 to 64 characters")
    return heads


def output_dir() -> Path:
    configured = os.environ.get("UNSTOPPABLE_CODE_OUTPUT_DIR", "").strip()
    if configured:
        path = Path(configured)
    elif os.environ.get("UNSTOPPABLE_CODE_OUTPUT", "").strip():
        path = Path(os.environ["UNSTOPPABLE_CODE_OUTPUT"]).parent
    else:
        path = Path(tempfile.mkdtemp(prefix="alchemy-check-"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def same_commit(left: str, right: str) -> bool:
    """Equal commits; an abbreviation must be hex and at least 7 characters on both sides."""
    left, right = left.strip().lower(), right.strip().lower()
    if not (HEAD_RE.match(left) and HEAD_RE.match(right)):
        return False
    short, full = sorted((left, right), key=len)
    return full.startswith(short)


def prepare_plan(mode: str, root: Path, skill: Path, profile: Path | None, out: Path) -> dict[str, str]:
    """Extract the plan when plan_field is set; in plan mode also verify and publish it."""
    source = resolve(option("plan"), root)
    field = option("plan_field")
    data = read_json(source)
    if field:
        if not isinstance(data, dict) or field not in data:
            raise InputError(f"{source}: no field {field!r}")
        value = data[field]
        if isinstance(value, str):
            if not value.strip():
                raise InputError(f"{source}: field {field!r} is empty; the planning step returned no plan")
            try:
                value = json.loads(value)
            except ValueError as exc:
                raise InputError(f"{source}: field {field!r} is not JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise InputError(f"{source}: field {field!r} must hold a JSON object")
        data = value
    if not isinstance(data, dict):
        raise InputError(f"{source}: a plan must be a JSON object")
    heads = integrated_heads()
    if heads:
        if not isinstance(data.get("base"), dict):
            raise InputError(f"{source}: the plan has no base object to add integrated heads to")
        known = data["base"].get("integrated")
        known = list(known) if isinstance(known, list) else []
        data["base"]["integrated"] = known + [head for head in heads if head not in known]
    if mode != "plan":
        if not field and not heads:
            return {"plan_file": str(source)}
        plan_file = out / f"alchemy-plan-{uuid.uuid4().hex[:8]}.json"
        write_json(plan_file, data)
        return {"plan_file": str(plan_file)}

    base = data.get("base") if isinstance(data.get("base"), dict) else {}
    base_commit = str(base.get("commit") or "")
    expected = option("expect_base")
    if expected and not same_commit(base_commit, expected):
        raise InputError(f"plan base.commit {base_commit or '(none)'} is not {expected}, "
                         "the commit this run started from")

    outputs = {"base_commit": base_commit, "run_dir": ""}
    plan_file = source
    if flag("publish", "false"):
        canonical = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        state = root / state_dir(skill, profile, root)
        ignore = state / ".gitignore"
        if not ignore.exists():
            state.mkdir(parents=True, exist_ok=True)
            with open(ignore, "w", encoding="utf-8", newline="\n") as handle:
                handle.write("*\n")
        run = state / f"{stamp}-{hashlib.sha256(canonical).hexdigest()[:8]}"
        plan_file = run / "plan.json"
        write_json(plan_file, data)
        outputs["run_dir"] = str(run)
    elif field or heads:
        plan_file = out / f"alchemy-plan-{uuid.uuid4().hex[:8]}.json"
        write_json(plan_file, data)
    outputs["plan_file"] = str(plan_file)
    return outputs


def run_checker(checker: Path, args: list[str]) -> dict[str, Any]:
    result = subprocess.run([sys.executable, str(checker), *args], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    if result.returncode == 2:
        raise InputError(f"check_orchestration.py rejected its input: {result.stderr.strip()}")
    try:
        report = json.loads(result.stdout)
    except ValueError as exc:
        raise InputError(f"check_orchestration.py printed no JSON report (exit {result.returncode})") from exc
    if not isinstance(report, dict) or report.get("verdict") not in RANK:
        raise InputError(f"check_orchestration.py returned an unknown verdict: {report!r:.200}")
    return report


def codes(report: dict[str, Any]) -> str:
    errors = report.get("errors") or []
    if not errors:
        return "none"
    return ", ".join(f"{e.get('code')}({e.get('subject') or '-'})" for e in errors)


def listing(values: Any) -> str:
    items = [v.get("id", "?") if isinstance(v, dict) else str(v) for v in (values or [])]
    return ", ".join(items) or "None"


def summarize(mode: str, report: dict[str, Any]) -> str:
    verdict = report["verdict"]
    if mode == "plan":
        waves = " | ".join(",".join(wave) for wave in report.get("waves") or [])
        text = (f"Plan: {verdict}; derived mode {report.get('derived_mode')}; recommendation "
                f"{report.get('recommendation')}; unattended {str(report.get('unattended') is True).lower()}; "
                f"waves {waves or 'none'}; errors {codes(report)}")
    elif mode == "preflight":
        text = (f"Preflight: {verdict}; plan digest {report.get('plan_digest')}; queued "
                f"{listing(report.get('queued'))}; errors {codes(report)}")
    elif mode == "gate":
        text = (f"Gate: {verdict}; Verified: {listing(report.get('verified'))}; "
                f"Unverified: {listing(report.get('unverified'))}; Open: {listing(report.get('open'))}; "
                f"Coverage: {report.get('coverage')}; Errors: {codes(report)}; Merge: human approval required")
    elif "records" in report:
        parts = [f"{r['report'].get('package') or Path(r['file']).name}:{r['report']['verdict']}"
                 for r in report["records"]]
        errors = "; ".join(codes(r["report"]) for r in report["records"] if r["report"].get("errors"))
        text = f"Hand-offs: {verdict}; {', '.join(parts)}; errors {errors or 'none'}"
    else:
        text = (f"Hand-off: {verdict}; package {report.get('package')} status {report.get('status')}; "
                f"errors {codes(report)}")
    return " ".join(text.split())


def check(mode: str, root: Path, checker: Path, profile: Path | None, plan_file: str) -> dict[str, Any]:
    common = ["--profile", str(profile)] if profile is not None else []
    if mode == "plan":
        return run_checker(checker, ["plan", plan_file, *common])
    raw_record = option("record")
    if not raw_record:
        raise InputError(f"{mode} mode needs the record input")
    record = resolve(raw_record, root)
    if mode == "preflight":
        # Probes ran at the plan base, so the repository must still be there and clean.
        if not record.is_file():
            raise InputError(f"preflight record not found: {record}")
        return run_checker(checker, ["preflight", str(record), "--plan", plan_file, *common, "--root", str(root)])
    if mode == "gate":
        if not record.is_file():
            raise InputError(f"ledger not found: {record}")
        # A missing record is passed over here; the checker then refuses an
        # unattended plan (PREFLIGHT_REQUIRED), and an attended one needs none.
        preflight = resolve(option("preflight"), root) if option("preflight") else None
        extra = ["--preflight", str(preflight)] if preflight is not None and preflight.is_file() else []
        return run_checker(checker, ["gate", str(record), "--plan", plan_file, *common, *extra])
    extra = ["--plan", plan_file, *common]
    if flag("digests", "true"):
        workspace = resolve(option("root"), root) if option("root") else root
        if not workspace.is_dir():
            raise InputError(f"root is not a directory: {workspace}")
        extra += ["--root", str(workspace)]
    if record.is_dir():
        files = sorted(path for path in record.glob("*.json") if path.is_file())
        if not files:
            raise InputError(f"no *.json hand-off records in {record}")
        records = [{"file": str(path), "report": run_checker(checker, ["handoff", str(path), *extra])}
                   for path in files]
        verdict = max((r["report"]["verdict"] for r in records), key=lambda v: RANK[v])
        return {"check": "handoff", "verdict": verdict, "records": records}
    if not record.is_file():
        raise InputError(f"hand-off not found: {record}")
    return run_checker(checker, ["handoff", str(record), *extra])


def emit(outputs: dict[str, str]) -> None:
    lines = [f"{key}={' '.join(str(value).split())}" for key, value in outputs.items()]
    target = os.environ.get("UNSTOPPABLE_CODE_OUTPUT", "").strip()
    if target:
        with open(target, "a", encoding="utf-8", newline="\n") as handle:
            handle.write("".join(line + "\n" for line in lines))
    for line in lines:
        print(line)


def main() -> int:
    try:
        mode = option("mode").lower()
        if mode not in MODES:
            raise InputError(f"input mode must be one of {', '.join(MODES)}, not {mode!r}")
        if not option("plan"):
            raise InputError("input plan is required")
        enforce = flag("enforce", "true")
        root = repo_root()
        skill = skill_dir(root)
        checker = skill / "scripts" / "check_orchestration.py"
        raw_profile = option("profile")
        profile = resolve(raw_profile, root) if raw_profile else root / PROFILE_NAME
        if raw_profile and not profile.is_file():
            raise InputError(f"profile not found: {profile}")
        if not profile.is_file():
            profile = None
        out = output_dir()

        outputs = prepare_plan(mode, root, skill, profile, out)
        report = check(mode, root, checker, profile, outputs["plan_file"])
        report_file = out / f"alchemy-{mode}-report-{uuid.uuid4().hex[:8]}.json"
        write_json(report_file, report)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if mode == "plan":
            # The pipeline runs the preflight only for an unattended plan, and
            # the preflight record binds to this digest.
            outputs["unattended"] = "true" if report.get("unattended") is True else "false"
            outputs["plan_digest"] = str(report.get("plan_digest") or "")
        emit({"verdict": report["verdict"], "summary": summarize(mode, report),
              "report_file": str(report_file), **outputs})
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if enforce and report["verdict"] not in PASSING:
        print(f"ERROR: verdict {report['verdict']}; see {report_file}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
