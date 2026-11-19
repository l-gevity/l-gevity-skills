#!/usr/bin/env python3
"""Run one arm of the single- vs multi-agent ALCHEMY pilot, headless.

    python .pilot/run_pilot.py --arm single|multi [--runtime claude|codex]
        [--objective audit|trivial | --objective-file PATH] [--model ID]
        [--out .pilot/results/<name>.json] [--keep DIR] [--timeout SECONDS]
        [--max-budget-usd N] [--inject-agent-failure] [--codex-user-config] [--dry-run]
    python .pilot/run_pilot.py --analyze-stream FILE [--runtime claude|codex]

Both arms send the identical objective through the normal entrypoint
(`/alchemy ...` for Claude Code, `$alchemy ...` for Codex) and both install the
alchemy-orchestrate runtime adapter with init_workspace.py. The arms differ
only in the workspace profile: `single` sets execution.multi_agent to "off",
`multi` keeps "auto". The run project is a throwaway copy of the fixture plus
the skill library; .pilot/, defects.json, and the hidden tests never enter it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

PILOT = Path(__file__).resolve().parent
REPO = PILOT.parent
sys.path.insert(0, str(PILOT))

import pilot_analysis  # noqa: E402
import score as scorer  # noqa: E402

INIT_SCRIPT = REPO / ".agents" / "skills" / "alchemy-orchestrate" / "scripts" / "init_workspace.py"
SKILL_TREES = (Path(".claude") / "skills", Path(".agents") / "skills")
SKILL_IGNORE = ("__pycache__", "*.pyc")
ENTRYPOINT = {"claude": "/alchemy", "codex": "$alchemy"}
INIT_RUNTIME = {"claude": "claude-code", "codex": "codex"}
OBJECTIVES = {
    "audit": {
        "text": (
            "Audit this backend and fix what you find: correctness bugs, security defects, dead code, "
            "and architectural simplification. Keep the visible tests passing. Verify your changes, then "
            "write a pull request description to PR.md with what changed, the evidence (commands and "
            "results), and what you did not verify. Do not push or open a real pull request."
        ),
        "checks": [],
    },
    "trivial": {
        "text": "Rename the function paginate in src/lib/pagination.js to paginateList and update its references.",
        "checks": [
            {"id": "old-name-gone", "check": {"kind": "absent", "pattern": r"\bpaginate\b"}},
            {"id": "new-name-present", "check": {"kind": "present", "pattern": r"\bpaginateList\b"}},
        ],
    },
}
ANSWER_MARKERS = ("alchemy-pilot-defects/1", "PILOT-SECRET-6f1d0c", "hidden-test-secret")
FORBIDDEN_NAMES = {".pilot", "hidden-tests", "defects.json", "score.py", "run_pilot.py"}
HARNESS_FILES = {"fail_first_agent.py", "fail_first_agent.marker", "fail_first_agent.log"}
NOT_FIXTURE_PREFIXES = (".claude/", ".agents/", ".codex/", ".alchemy/")
NOT_FIXTURE_FILES = {"PR.md", "alchemy-workspace.json", "CLAUDE.md", "AGENTS.md"}
HOOK_COMMAND = "python .alchemy/fail_first_agent.py"
HOOK_SCRIPT = '''"""Pilot fault injection: block the first Agent launch, allow every later one."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = HERE / "fail_first_agent.marker"
LOG = HERE / "fail_first_agent.log"


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        event = {}
    tool = event.get("tool_name", "")
    blocked = tool in ("Agent", "Task") and not MARKER.exists()
    with LOG.open("a", encoding="utf-8") as log:
        log.write(json.dumps({"tool": tool, "blocked": blocked}) + "\\n")
    if blocked:
        MARKER.write_text("blocked\\n", encoding="utf-8")
        sys.stderr.write("simulated agent crash: retry from the base commit\\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


class PilotError(Exception):
    pass


# ---------------------------------------------------------------- redaction

SECRET_PATTERNS = (
    re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{16,}"),
    re.compile(r"(?i)((?:api[_-]?key|secret|password|token)[\"']?\s*[:=]\s*[\"']?)[A-Za-z0-9._~+/=-]{24,}"),
)


def path_forms(path: Path) -> list[str]:
    text = str(path)
    forms = {text, path.as_posix()}
    match = re.match(r"^([A-Za-z]):[\\/](.*)$", text)
    if match:
        rest = match.group(2).replace("\\", "/")
        forms.add(f"/{match.group(1).lower()}/{rest}")
        forms.add(f"/mnt/{match.group(1).lower()}/{rest}")
    return [form for form in forms if len(form) > 3]


def git_identity() -> list[str]:
    values = []
    for key in ("user.email", "user.name"):
        run = subprocess.run(["git", "config", "--get", key], cwd=REPO, capture_output=True, text=True, check=False)
        if run.returncode == 0 and len(run.stdout.strip()) > 2:
            values.append(run.stdout.strip())
    return values


def make_redactor(project: Path | None) -> callable:
    """Replace machine paths, the git identity, and token-like strings."""
    pairs = []
    if project is not None:
        pairs += [(form, "<run-project>") for form in path_forms(project)]
    pairs += [(form, "<repo>") for form in path_forms(REPO)]
    pairs += [(form, "<tmp>") for form in path_forms(Path(tempfile.gettempdir()))]
    pairs += [(form, "~") for form in path_forms(Path.home())]
    pairs += [(value, "<git-identity>") for value in git_identity()]
    pairs.sort(key=lambda pair: len(pair[0]), reverse=True)
    compiled = [(re.compile(re.escape(old), re.I), new) for old, new in pairs]
    # The account name also surfaces outside paths: directory listings and
    # escaped or mangled path forms such as C--Users-<name>-AppData.
    user = Path.home().name
    if user:
        compiled.append((re.compile(rf"(?<![A-Za-z0-9]){re.escape(user)}(?![A-Za-z0-9])", re.I), "<user>"))

    def redact_text(text: str) -> str:
        for pattern, new in compiled:
            text = pattern.sub(lambda _, new=new: new, text)
        for pattern in SECRET_PATTERNS:
            text = pattern.sub(lambda m: (m.group(1) if m.groups() else "") + "<redacted>", text)
        return text

    def redact(value):
        if isinstance(value, str):
            return redact_text(value)
        if isinstance(value, list):
            return [redact(item) for item in value]
        if isinstance(value, dict):
            return {key: redact(item) for key, item in value.items()}
        return value

    return redact


# ---------------------------------------------------------------- helpers

def remove_tree(path: Path) -> None:
    """rmtree that also clears the read-only bit git sets on Windows objects."""
    def retry(function, target, _):
        os.chmod(target, stat.S_IWRITE)
        function(target)
    if path.exists():
        shutil.rmtree(path, onexc=retry)


def git(project: Path, *args: str) -> str:
    run = subprocess.run(["git", *args], cwd=project, capture_output=True, text=True, encoding="utf-8", check=False)
    if run.returncode != 0:
        raise PilotError(f"git {' '.join(args)} failed: {run.stderr.strip()}")
    return run.stdout


def commit(project: Path, message: str) -> str:
    git(project, "add", "-A")
    git(project, "-c", "user.name=Pilot Harness", "-c", "user.email=pilot@example.invalid",
        "commit", "--quiet", "--no-verify", "-m", message)
    return git(project, "rev-parse", "HEAD").strip()


def file_set(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }


def resolve_objective(args) -> tuple[str, str, list[dict]]:
    if args.objective_file:
        body = Path(args.objective_file).read_text(encoding="utf-8").strip()
        name, checks = f"file:{Path(args.objective_file).name}", []
    else:
        body, checks, name = OBJECTIVES[args.objective]["text"], OBJECTIVES[args.objective]["checks"], args.objective
    body = re.sub(r"^\s*[/$]alchemy\b\s*", "", body)
    if not body:
        raise PilotError("the objective is empty")
    return name, body, checks


# ---------------------------------------------------------------- project

def isolation_check(project: Path) -> dict:
    """Prove the answers stayed out: no pilot paths, no answer markers in any file."""
    paths, markers = [], []
    for path in project.rglob("*"):
        relative = path.relative_to(project)
        if ".git" in relative.parts:
            continue
        if FORBIDDEN_NAMES & set(relative.parts) or re.fullmatch(r"D\d\d\.test\.js", path.name):
            paths.append(relative.as_posix())
        if path.is_file() and path.stat().st_size < 2_000_000:
            text = path.read_text(encoding="utf-8", errors="ignore")
            markers.extend(f"{relative.as_posix()}: {marker}" for marker in ANSWER_MARKERS if marker in text)
    return {"forbidden_paths": paths, "answer_markers": markers, "clean": not paths and not markers}


def install_failure_hook(project: Path) -> dict:
    state = project / ".alchemy"
    state.mkdir(exist_ok=True)
    (state / "fail_first_agent.py").write_text(HOOK_SCRIPT, encoding="utf-8")
    settings_path = project / ".claude" / "settings.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.is_file() else {}
    hook = {"matcher": "Agent|Task", "hooks": [{"type": "command", "command": HOOK_COMMAND}]}
    settings.setdefault("hooks", {}).setdefault("PreToolUse", []).append(hook)
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    exclude = project / ".git" / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    with exclude.open("a", encoding="utf-8") as handle:
        handle.write(".alchemy/fail_first_agent.marker\n.alchemy/fail_first_agent.log\n")
    return {"settings": ".claude/settings.json", "hook": hook, "script": ".alchemy/fail_first_agent.py"}


def build_project(project: Path, fixture_dir: Path, arm: str, runtime: str, inject: bool) -> dict:
    shutil.copytree(fixture_dir / "project", project, dirs_exist_ok=True)
    git(project, "init", "--quiet", "-b", "main")
    git(project, "config", "core.autocrlf", "false")
    git(project, "config", "user.name", "Pilot Agent")
    git(project, "config", "user.email", "pilot-agent@example.invalid")
    fixture_commit = commit(project, "Import orders-service")

    for tree in SKILL_TREES:
        if (REPO / tree).is_dir():
            shutil.copytree(REPO / tree, project / tree, ignore=shutil.ignore_patterns(*SKILL_IGNORE))
    shutil.copyfile(REPO / "CLAUDE.md", project / "CLAUDE.md")
    shutil.copyfile(REPO / "CLAUDE.md", project / "AGENTS.md")

    before = file_set(project)
    init = subprocess.run(
        [sys.executable, str(INIT_SCRIPT), "--runtime", INIT_RUNTIME[runtime], "--root", str(project)],
        cwd=project, capture_output=True, text=True, encoding="utf-8", check=False,
    )
    if init.returncode != 0:
        raise PilotError(f"init_workspace.py exited {init.returncode}: {(init.stderr or init.stdout).strip()}")
    created = sorted(file_set(project) - before)

    profile_path = project / "alchemy-workspace.json"
    if not profile_path.is_file():
        raise PilotError("init_workspace.py did not write alchemy-workspace.json")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    execution = profile.setdefault("execution", {})
    written = execution.get("multi_agent")
    if arm == "single":
        execution["multi_agent"] = "off"
        profile_path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    elif written != "auto":
        raise PilotError(f"the multi arm needs execution.multi_agent == 'auto'; init_workspace.py wrote {written!r}")

    hook = install_failure_hook(project) if inject else None
    base_commit = commit(project, "Add skill library and workspace profile")
    return {
        "files_before_run": file_set(project),
        "fixture_commit": fixture_commit,
        "base_commit": base_commit,
        "init_workspace": {"exit": init.returncode, "created": created, "stdout": init.stdout.strip()[-2000:]},
        "multi_agent_written": written,
        "multi_agent": execution["multi_agent"],
        "execution_profile": execution,
        "failure_hook": hook,
    }


def build_command(runtime: str, launcher: list[str], prompt: str, project: Path, args) -> list[str]:
    if runtime == "claude":
        command = [
            *launcher, "-p", prompt,
            "--output-format", "stream-json", "--verbose",
            "--setting-sources", "project", "--strict-mcp-config",
            "--no-session-persistence", "--permission-mode", "bypassPermissions",
            "--forward-subagent-text",
        ]
        if args.model:
            command += ["--model", args.model]
        if args.max_budget_usd is not None:
            command += ["--max-budget-usd", str(args.max_budget_usd)]
        return command
    # No --ephemeral: a sub-agent spawned with the parent's context loads the
    # parent's saved session, and an ephemeral session has none, so every
    # spawn failed with "no rollout found for thread" (codex-multi-audit-1).
    command = [*launcher, "exec", "--json", "--dangerously-bypass-approvals-and-sandbox", "-C", str(project)]
    if not args.codex_user_config:
        command.append("--ignore-user-config")
    if args.model:
        command += ["-m", args.model]
    return command + [prompt]


def runtime_environment(runtime: str) -> dict:
    environment = dict(os.environ)
    if runtime == "claude":
        environment.pop("CLAUDECODE", None)
        # Headless runs stop background sub-agents 10 minutes after the lead's
        # last turn; claude-multi-parallel-1 lost its verifier that way. The
        # adapter settings carry the same bound; the environment makes sure it
        # applies before the project settings are read.
        environment["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "3600000"
    return environment


# ---------------------------------------------------------------- run

def run_agent(command: list[str], project: Path, environment: dict, timeout: int) -> dict:
    """Start the agent and stamp every stdout line with its arrival time."""
    started = datetime.now(timezone.utc)
    origin = time.monotonic()
    process = subprocess.Popen(
        command, cwd=project, env=environment, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, **scorer.group_kwargs(),
    )
    lines: list[tuple[float, str]] = []
    errors: list[bytes] = []

    def read_stdout():
        for raw in iter(process.stdout.readline, b""):
            lines.append((round(time.monotonic() - origin, 3), raw.decode("utf-8", errors="replace").rstrip("\r\n")))

    def read_stderr():
        errors.append(process.stderr.read())

    readers = [threading.Thread(target=read_stdout, daemon=True), threading.Thread(target=read_stderr, daemon=True)]
    for reader in readers:
        reader.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        scorer.kill_tree(process)
        process.wait()
    for reader in readers:
        reader.join(timeout=30)
    stamped, non_json = [], 0
    for seconds, text in lines:
        try:
            event = json.loads(text)
        except json.JSONDecodeError:
            non_json += 1 if text.strip() else 0
            continue
        if isinstance(event, dict):
            event["_t"] = seconds
            stamped.append((seconds, event))
    return {
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "wall_clock_seconds": round(time.monotonic() - origin, 1),
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "stamped": stamped,
        "non_json_lines": non_json,
        "stderr": b"".join(errors).decode("utf-8", errors="replace"),
    }


def git_facts(project: Path, base: str, fixture_commit: str) -> dict:
    changed = []
    for line in git(project, "diff", "--numstat", base).splitlines():
        added, deleted, path = line.split("\t", 2)
        changed.append({"path": path, "added": added, "deleted": deleted, "status": "tracked"})
    for path in git(project, "ls-files", "--others", "--exclude-standard").splitlines():
        if Path(path).name in HARNESS_FILES:
            continue
        try:
            lines = len((project / path).read_text(encoding="utf-8", errors="ignore").splitlines())
        except OSError:
            lines = None
        changed.append({"path": path, "added": str(lines), "deleted": "0", "status": "untracked"})
    fixture_changed = [
        item["path"] for item in changed
        if not item["path"].startswith(NOT_FIXTURE_PREFIXES) and item["path"] not in NOT_FIXTURE_FILES
    ]
    return {
        "fixture_commit": fixture_commit,
        "base_commit": base,
        "agent_commits": int(git(project, "rev-list", "--count", f"{base}..HEAD").strip() or 0),
        "files_changed": changed,
        "fixture_files_changed": fixture_changed,
        "fixture_files_changed_count": len(fixture_changed),
    }


def pr_facts(project: Path) -> dict:
    candidates = [path for path in project.iterdir() if path.is_file() and path.name.lower() == "pr.md"]
    if not candidates:
        return {"exists": False}
    text = candidates[0].read_text(encoding="utf-8", errors="replace")
    return {
        "exists": True,
        "bytes": len(text.encode("utf-8")),
        "mentions_test_command": bool(re.search(r"node --test|npm (run )?test", text)),
        "mentions_results": bool(re.search(
            r"(?i)(\b\d+\s*(?:/\s*\d+\s*)?(?:tests?\s+)?(?:passed|passing|pass)\b|#\s*pass\s+\d+|\bpass(?:ed)?\s*[:=]\s*\d+|exit(?: code)?\s*[:=]?\s*0\b|all tests pass)",
            text,
        )),
        "mentions_unverified": bool(re.search(
            r"(?i)(not verif|did not verif|unverified|not check|did not check|not run|not tested)", text
        )),
        "text": text[:20000],
    }


def orchestration_artifacts(project: Path, before: set[str]) -> list[str]:
    """Files the run wrote under .alchemy/ (plans, ledgers, hand-offs); files present before the run excluded."""
    return sorted(
        path for path in file_set(project)
        if path.startswith(".alchemy/") and path not in before and Path(path).name not in HARNESS_FILES
    )


def hook_log(project: Path) -> list[dict]:
    log = project / ".alchemy" / "fail_first_agent.log"
    if not log.is_file():
        return []
    entries = []
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def runtime_version(launcher: list[str], runtime: str, analysis: dict) -> str | None:
    if runtime == "claude" and analysis["init"].get("claude_code_version"):
        return f"claude-code {analysis['init']['claude_code_version']}"
    run = subprocess.run([*launcher, "--version"], capture_output=True, text=True, check=False)
    return run.stdout.strip() or None


def default_out(args, objective_name: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    label = re.sub(r"[^A-Za-z0-9_-]+", "-", objective_name)
    return PILOT / "results" / f"{args.arm}-{args.runtime}-{label}-{stamp}.json"


def keep_project(project: Path, keep: Path) -> None:
    if keep.exists() and any(keep.iterdir()):
        raise PilotError(f"--keep directory is not empty: {keep}")
    shutil.copytree(project, keep, dirs_exist_ok=True)


# ---------------------------------------------------------------- main

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run one arm of the ALCHEMY single- vs multi-agent pilot.")
    parser.add_argument("--arm", choices=("single", "multi"), help="single: execution.multi_agent=off; multi: auto")
    parser.add_argument("--runtime", choices=("claude", "codex"), default="claude")
    parser.add_argument("--model", help="model id passed to the runtime (default: the runtime's default)")
    objective = parser.add_mutually_exclusive_group()
    objective.add_argument("--objective", choices=sorted(OBJECTIVES), default="audit", help="built-in objective")
    objective.add_argument("--objective-file", type=Path, help="file holding the objective text")
    parser.add_argument("--fixture", default="server-audit", help="fixture directory under .pilot/")
    parser.add_argument("--out", type=Path, help="result JSON path (default: .pilot/results/<arm>-<runtime>-<objective>-<utc>.json)")
    parser.add_argument("--keep", type=Path, help="copy the finished run project to this empty directory")
    parser.add_argument("--timeout", type=int, default=3600, help="agent timeout in seconds (default: 3600)")
    parser.add_argument("--max-budget-usd", type=float, help="claude only: pass --max-budget-usd")
    parser.add_argument("--inject-agent-failure", action="store_true",
                        help="claude only: a PreToolUse hook blocks the first Agent launch")
    parser.add_argument("--codex-user-config", action="store_true",
                        help="codex only: load ~/.codex/config.toml (default: --ignore-user-config)")
    parser.add_argument("--cli", help="runtime executable to run instead of the one on PATH; a .py file runs with this Python")
    parser.add_argument("--dry-run", action="store_true", help="build the run project and print the command; no model call")
    parser.add_argument("--analyze-stream", type=Path, help="print acceptance facts for a saved stream and exit")
    args = parser.parse_args(argv)
    if not args.analyze_stream and not args.arm:
        parser.error("--arm is required unless --analyze-stream is given")
    if args.inject_agent_failure and args.runtime != "claude":
        parser.error("--inject-agent-failure supports --runtime claude only")
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.analyze_stream:
        analysis = pilot_analysis.analyze(pilot_analysis.load_stream(args.analyze_stream), args.runtime)
        print(json.dumps(analysis, indent=2))
        return 0

    fixture_dir = PILOT / args.fixture
    try:
        if not (fixture_dir / "project").is_dir():
            raise PilotError(f"fixture not found: {fixture_dir / 'project'}")
        if not INIT_SCRIPT.is_file():
            raise PilotError(
                f"{INIT_SCRIPT.relative_to(REPO).as_posix()} does not exist. Both arms install the "
                "alchemy-orchestrate runtime adapter with it; add the script before running the pilot."
            )
        objective_name, body, objective_checks = resolve_objective(args)
    except PilotError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    prompt = f"{ENTRYPOINT[args.runtime]} {body}"
    cli = str(Path(args.cli).resolve()) if args.cli else shutil.which(args.runtime)
    warnings = []
    if cli is None:
        if not args.dry_run:
            print(f"ERROR: the {args.runtime} CLI is not on PATH", file=sys.stderr)
            return 2
        warnings.append(f"the {args.runtime} CLI is not on PATH; the command shows its bare name")
        cli = args.runtime
    launcher = [sys.executable, cli] if cli.endswith(".py") else [cli]
    if args.runtime == "claude" and not (REPO / ".claude" / "skills" / "alchemy-orchestrate" / "SKILL.md").is_file():
        warnings.append(".claude/skills/alchemy-orchestrate is missing: Claude Code discovers skills there, "
                        "so the run can only read the .agents/skills copy")

    project = Path(tempfile.mkdtemp(prefix=f"alchemy-pilot-{args.arm}-{args.runtime}-")).resolve()
    try:
        setup = build_project(project, fixture_dir, args.arm, args.runtime, args.inject_agent_failure)
        isolation = isolation_check(project)
        if not isolation["clean"]:
            raise PilotError(f"answers leaked into the run project: {isolation}")
        command = build_command(args.runtime, launcher, prompt, project, args)
        environment = runtime_environment(args.runtime)

        if args.dry_run:
            listing = sorted({path.relative_to(project).parts[0] for path in project.iterdir()})
            report = {
                "dry_run": True,
                "arm": args.arm,
                "runtime": args.runtime,
                "objective": {"name": objective_name, "prompt": prompt},
                "run_project": str(project) + ("" if args.keep else " (deleted after the dry run)"),
                "top_level": listing,
                "skill_count": {tree.as_posix(): len(list((project / tree).glob("*/SKILL.md"))) for tree in SKILL_TREES},
                "isolation": isolation,
                "workspace": {key: value for key, value in setup.items() if key != "files_before_run"},
                "command": command,
                "environment_removed": ["CLAUDECODE"] if args.runtime == "claude" else [],
                "timeout_seconds": args.timeout,
                "warnings": warnings,
            }
            print(json.dumps(report, indent=2))
            if args.keep:
                keep_project(project, args.keep)
            return 0

        run = run_agent(command, project, environment, args.timeout)
        analysis = pilot_analysis.analyze([(t, e) for t, e in run["stamped"]], args.runtime)
        scored = scorer.score(project, args.fixture)
        files = scorer.source_files(project)
        checks = []
        for item in objective_checks:
            holds, evidence = scorer.static_check(item["check"], files)
            checks.append({"id": item["id"], "holds": holds, "evidence": evidence})
        acceptance = analysis["acceptance"]
        injection = None
        if args.inject_agent_failure:
            log = hook_log(project)
            injection = {
                **acceptance["injected_failure"],
                "hook_invocations": len(log),
                "hook_blocked": sum(1 for entry in log if entry.get("blocked")),
            }
        if args.runtime == "codex" and not args.model:
            warnings.append("codex exec --json does not report the model; none was requested")
        if acceptance["agent_launches"] and acceptance["subagent_events_observed"] == 0:
            warnings.append("agents launched but no sub-agent events carried parent_tool_use_id; "
                            "skills_loaded_by_subagents is unobservable for this run")

        out = args.out or default_out(args, objective_name)
        stream_path = out.with_name(out.stem + ".stream.jsonl")
        redact = make_redactor(project)
        record = {
            "schema": "alchemy-pilot-result/1",
            "fixture": args.fixture,
            "arm": args.arm,
            "runtime": args.runtime,
            "runtime_version": runtime_version(launcher, args.runtime, analysis),
            "model_requested": args.model,
            "model_reported": analysis["init"].get("model"),
            "objective": {"name": objective_name, "prompt": prompt},
            "workspace": {
                "multi_agent": setup["multi_agent"],
                "multi_agent_written_by_init": setup["multi_agent_written"],
                "init_workspace_created": setup["init_workspace"]["created"],
                "failure_hook": setup["failure_hook"],
            },
            "command": [args.runtime, *command[len(launcher):]],
            "started_at": run["started_at"],
            "finished_at": run["finished_at"],
            "wall_clock_seconds": run["wall_clock_seconds"],
            "exit_code": run["exit_code"],
            "timed_out": run["timed_out"],
            "result_event": analysis["result_event"],
            "metrics": analysis["metrics"],
            "tools_available": analysis["init"].get("tools"),
            "skills_available": analysis["init"].get("skills"),
            "tool_calls": analysis["tool_calls"],
            "acceptance": acceptance,
            "injection": injection,
            "score": scored,
            "objective_checks": checks,
            "git": git_facts(project, setup["base_commit"], setup["fixture_commit"]),
            "pr_md": pr_facts(project),
            "orchestration_artifacts": orchestration_artifacts(project, setup["files_before_run"]),
            "isolation": isolation,
            "stream": {
                "file": stream_path.name,
                "events": len(run["stamped"]),
                "non_json_lines": run["non_json_lines"],
                "census": analysis["census"],
                "collab_item_keys": analysis.get("collab_item_keys"),
            },
            "stderr_tail": run["stderr"][-2000:],
            "warnings": warnings,
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(redact(record), indent=2) + "\n", encoding="utf-8")
        with stream_path.open("w", encoding="utf-8") as handle:
            for _, event in run["stamped"]:
                handle.write(json.dumps(redact(event)) + "\n")
        if args.keep:
            keep_project(project, args.keep)
        summary = {
            "result": str(out),
            "exit_code": run["exit_code"],
            "timed_out": run["timed_out"],
            "wall_clock_seconds": run["wall_clock_seconds"],
            "total_cost_usd": analysis["metrics"].get("total_cost_usd"),
            "defects_fixed": f"{scored['defects_fixed']}/{scored['defects_total']}",
            "visible_tests_pass": scored["visible_tests_pass"],
            "execution_line": acceptance["execution_line"],
            "agent_launches": acceptance["agent_launch_count"],
            "parallel_overlap": acceptance["parallel_overlap"],
            "review_after_implementation": acceptance["review_after_implementation"],
            "warnings": warnings,
        }
        print(json.dumps(redact(summary), indent=2))
        return 0
    except PilotError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    finally:
        remove_tree(project)


if __name__ == "__main__":
    sys.exit(main())
