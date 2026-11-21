#!/usr/bin/env python3
"""Install the alchemy-orchestrate runtime adapters into a project.

Usage:
    init_workspace.py --runtime claude-code|codex|unstoppable|all
                      [--root <project dir>] [--profile <alchemy-workspace.json>] [--dry-run]
                      [--uninstall]

Reads the defaults from this skill's assets/alchemy-workspace.json, overridden
key by key by the project profile (--profile, else alchemy-workspace.json at
--root when it exists), and renders the files under adapters/ to their runtime
locations. Agent descriptions and instructions come from the profile's
envelopes at render time; nothing here restates them.

An existing file is never overwritten. Identical content is reported
unchanged; different content is kept and the rendered version is written
beside it as <file>.l-gevity for a manual merge. A second run on an installed
project reports every file unchanged.

--uninstall removes what an install would write: each file, and its .l-gevity
sibling, that is byte-identical to its rendering now, line endings ignored. An
edited file is kept and reported. So are a profile that differs from the
defaults and a state directory that holds run records. Directories left empty
are removed. Exit 0, or 2 on bad arguments or an unusable profile.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

SKILL_DIR = Path(__file__).resolve().parent.parent
ADAPTERS = SKILL_DIR / "adapters"
DEFAULTS = SKILL_DIR / "assets" / "alchemy-workspace.json"
PROFILE_NAME = "alchemy-workspace.json"
PROFILE_SCHEMA = "alchemy-workspace/1"
SUFFIX = ".l-gevity"


@dataclass(frozen=True)
class Target:
    source: str  # relative to adapters/
    dest: str  # relative to the project root
    render: bool = True
    off_overlay: str = ""  # merged in when execution.multi_agent is "off"


RUNTIMES: dict[str, tuple[Target, ...]] = {
    "claude-code": (
        Target("claude-code/agents/alchemy-analyst.md", ".claude/agents/alchemy-analyst.md"),
        Target("claude-code/agents/alchemy-implementer.md", ".claude/agents/alchemy-implementer.md"),
        Target("claude-code/settings.json", ".claude/settings.json",
               off_overlay="claude-code/settings.multi-agent-off.json"),
    ),
    "codex": (
        Target("codex/agents/alchemy-analyst.toml", ".codex/agents/alchemy-analyst.toml"),
        Target("codex/agents/alchemy-implementer.toml", ".codex/agents/alchemy-implementer.toml"),
        Target("codex/config.toml", ".codex/config.toml", off_overlay="codex/config.multi-agent-off.toml"),
    ),
    "unstoppable": (
        Target("unstoppable/actions/alchemy-check/action.yml",
               ".unstoppable-code/actions/alchemy-check/action.yml", render=False),
        Target("unstoppable/actions/alchemy-check/check.py",
               ".unstoppable-code/actions/alchemy-check/check.py", render=False),
        Target("unstoppable/actions/alchemy-snapshot/action.yml",
               ".unstoppable-code/actions/alchemy-snapshot/action.yml", render=False),
        Target("unstoppable/actions/alchemy-snapshot/snapshot.py",
               ".unstoppable-code/actions/alchemy-snapshot/snapshot.py", render=False),
        Target("unstoppable/pipelines/alchemy-multi-agent.yaml",
               ".unstoppable-code/pipelines/alchemy-multi-agent.yaml", render=False),
        Target("unstoppable/review-tracks/alchemy-independent-review.md",
               ".unstoppable-code/review-tracks/alchemy-independent-review.md", render=False),
    ),
}

# A skills root is rendered into permission rules such as Bash(python <root>/...),
# so it may hold only characters that cannot change the rule's meaning.
ROOT_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][\w.]*?)(\[\*\])?\s*((?:\|\s*\w+\s*)*)\}\}")


class UsageError(Exception):
    """Bad arguments, an unusable profile, or a target that cannot be written; exit 2."""


# ------------------------------------------------------------------ profile

def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_bytes().decode("utf-8-sig"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise UsageError(f"{path}: {exc}") from exc


def deep_merge(base: dict[str, Any], override: dict[str, Any], concat: bool = False) -> dict[str, Any]:
    """Override key by key; with concat, lists are joined instead of replaced."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value, concat)
        elif concat and isinstance(value, list) and isinstance(merged.get(key), list):
            merged[key] = merged[key] + [item for item in value if item not in merged[key]]
        else:
            merged[key] = value
    return merged


def load_profile(overlay: Path | None) -> dict[str, Any]:
    profile = read_json(DEFAULTS)
    if overlay is not None:
        data = read_json(overlay)
        if not isinstance(data, dict):
            raise UsageError(f"{overlay}: a profile must be a JSON object")
        profile = deep_merge(profile, data)
    where = overlay or DEFAULTS
    if profile.get("schema") != PROFILE_SCHEMA:
        raise UsageError(f"{where}: schema must be {PROFILE_SCHEMA!r}")
    execution = profile.get("execution") or {}
    cap = execution.get("max_parallel_agents")
    if isinstance(cap, bool) or not isinstance(cap, int) or cap < 1:
        raise UsageError(f"{where}: execution.max_parallel_agents must be a positive integer")
    if execution.get("multi_agent", "auto") not in ("auto", "off"):
        raise UsageError(f"{where}: execution.multi_agent must be 'auto' or 'off'")
    roots = (profile.get("skills") or {}).get("roots")
    if not isinstance(roots, list) or not roots:
        raise UsageError(f"{where}: skills.roots must be a non-empty list of paths")
    profile["skills"]["roots"] = [skills_root(root, where) for root in roots]
    for name in ("analyst", "implementer"):
        envelope = (profile.get("envelopes") or {}).get(name) or {}
        for field in ("description", "instructions"):
            if not isinstance(envelope.get(field), str) or not envelope[field].strip():
                raise UsageError(f"{where}: envelopes.{name}.{field} must be a non-empty string")
    return profile


def skills_root(value: Any, where: Path) -> str:
    text = value.strip() if isinstance(value, str) else ""
    parts = text.split("/")
    if (not ROOT_RE.match(text) or text.startswith("/") or ".." in parts
            or not [part for part in parts if part not in ("", ".")]):
        raise UsageError(f"{where}: skills.roots entry {value!r} must be a relative path of letters, "
                         "digits, '.', '_', '-', and '/', with no '..' segment")
    return text.rstrip("/")


def inside(value: Any, label: str, root: Path, where: Path) -> PurePosixPath:
    """A path strictly inside root, refused by Windows or POSIX rules alike."""
    if not isinstance(value, str):
        raise UsageError(f"{where}: {label} must be a string, not {value!r}")
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
        problem = "names the project root itself"
    else:
        base = root.resolve()
        target = (base / "/".join(parts)).resolve()
        if base not in target.parents:
            problem = "does not resolve strictly inside the project"
    if problem:
        raise UsageError(f"{where}: {label} {value!r} {problem}")
    return PurePosixPath(*[part for part in parts if part not in ("", ".")])


# ---------------------------------------------------------------- rendering

def lookup(profile: dict[str, Any], dotted: str) -> Any:
    value: Any = profile
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(f"profile has no {dotted}")
        value = value[part]
    return value


def quote(value: Any) -> str:
    """A double-quoted scalar valid in JSON, YAML, and TOML."""
    text = json.dumps(str(value), ensure_ascii=False)
    return text.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029").replace("\x7f", "\\u007f")


def toml_ml(value: Any) -> str:
    """Body of a TOML multi-line basic string."""
    out = []
    for char in str(value):
        if char == "\\":
            out.append("\\\\")
        elif char == '"':
            out.append('\\"')
        elif char in "\n\t":
            out.append(char)
        elif ord(char) < 0x20 or ord(char) == 0x7F:
            out.append(f"\\u{ord(char):04x}")
        else:
            out.append(char)
    return "".join(out)


def code_list(value: Any) -> str:
    items = [f"`{item}`" for item in (value if isinstance(value, list) else [value])]
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " or " + items[-1]


FILTERS = {"quote": quote, "toml_ml": toml_ml, "code_list": code_list}


def apply_filters(value: Any, chain: str) -> str:
    for name in (part.strip() for part in chain.split("|") if part.strip()):
        if name not in FILTERS:
            raise KeyError(f"unknown filter {name!r}")
        value = FILTERS[name](value)
    return str(value)


def render_text(template: str, profile: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        if match.group(2):
            raise KeyError("[*] expands only inside a JSON list item")
        return apply_filters(lookup(profile, match.group(1)), match.group(3))

    return PLACEHOLDER_RE.sub(replace, template)


def render_json(value: Any, profile: dict[str, Any]) -> Any:
    if isinstance(value, dict):
        return {key: render_json(item, profile) for key, item in value.items()}
    if isinstance(value, list):
        rendered: list[Any] = []
        for item in value:
            match = PLACEHOLDER_RE.search(item) if isinstance(item, str) else None
            if match and match.group(2):
                for element in lookup(profile, match.group(1)):
                    text = item[:match.start()] + apply_filters(element, match.group(3)) + item[match.end():]
                    rendered.append(render_text(text, profile))
            else:
                rendered.append(render_json(item, profile))
        return rendered
    if isinstance(value, str):
        return render_text(value, profile)
    return value


def read_source(relative: str) -> str:
    return (ADAPTERS / relative).read_bytes().decode("utf-8").replace("\r\n", "\n")


def build(target: Target, profile: dict[str, Any]) -> bytes:
    text = read_source(target.source)
    off = profile["execution"].get("multi_agent", "auto") == "off" and target.off_overlay
    if target.render and target.source.endswith(".json"):
        data = render_json(json.loads(text), profile)
        if off:
            data = deep_merge(data, render_json(json.loads(read_source(target.off_overlay)), profile), concat=True)
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    elif target.render:
        text = render_text(text, profile)
        if off:
            text = text.rstrip("\n") + "\n" + render_text(read_source(target.off_overlay), profile)
    return text.encode("utf-8")


# ------------------------------------------------------------------- install

def plan_writes(runtimes: list[str], root: Path, overlay: Path | None, explicit_profile: bool,
                profile: dict[str, Any]) -> list[tuple[str, bytes | None, str]]:
    """(relative destination, content, policy) in print order. Policy: file, profile, or skip."""
    writes: list[tuple[str, bytes | None, str]] = []
    if explicit_profile:
        writes.append((PROFILE_NAME, None, "skip"))
    else:
        writes.append((PROFILE_NAME, DEFAULTS.read_bytes().replace(b"\r\n", b"\n"), "profile"))
    repository = profile.get("repository") if isinstance(profile.get("repository"), dict) else {}
    state = inside(repository.get("state_dir", ".alchemy/runs/"), "repository.state_dir", root,
                   overlay or DEFAULTS)
    writes.append(((state / ".gitignore").as_posix(), b"*\n", "file"))
    for runtime in runtimes:
        for target in RUNTIMES[runtime]:
            try:
                writes.append((target.dest, build(target, profile), "file"))
            except KeyError as exc:
                raise UsageError(f"adapters/{target.source}: {exc.args[0]}") from exc
    return writes


def same(path: Path, content: bytes) -> bool:
    return path.read_bytes().replace(b"\r\n", b"\n") == content


def write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def install(root: Path, writes: list[tuple[str, bytes | None, str]], dry_run: bool) -> list[str]:
    lines = []
    for relative, content, policy in writes:
        path = root / relative
        if policy == "skip":
            lines.append(f"{relative}: not written (profile given with --profile)")
            continue
        assert content is not None
        if path.is_dir():
            raise UsageError(f"{path} is a directory; cannot install a file there")
        if not path.exists():
            if not dry_run:
                write(path, content)
            lines.append(f"{relative}: {'would create' if dry_run else 'created'}")
        elif same(path, content):
            lines.append(f"{relative}: unchanged")
        elif policy == "profile":
            lines.append(f"{relative}: kept (project profile; overrides the defaults key by key)")
        else:
            beside = f"{relative}{SUFFIX}"
            if not dry_run:
                write(root / beside, content)
            verb = "would write" if dry_run else "wrote"
            lines.append(f"{relative}: kept ({verb} {beside}; merge manually)")
    return lines


def prune_empty(root: Path, start: Path) -> None:
    """Remove start and its parents while empty, never root or above it."""
    base = root.resolve()
    current = start
    while current != base and base in current.parents and current.is_dir() and not any(current.iterdir()):
        current.rmdir()
        current = current.parent


def uninstall(root: Path, writes: list[tuple[str, bytes | None, str]], dry_run: bool) -> list[str]:
    """Remove each planned file still identical to its rendering; keep the rest."""
    lines = []
    verb = "would remove" if dry_run else "removed"
    for relative, content, policy in writes:
        if policy == "skip":
            lines.append(f"{relative}: not removed (profile given with --profile)")
            continue
        assert content is not None
        candidates = [relative] if policy == "profile" else [relative, f"{relative}{SUFFIX}"]
        for name in candidates:
            path = root / name
            if not path.is_file():
                continue
            if not same(path, content):
                reason = ("project profile differs from the defaults" if policy == "profile"
                          else "edited since install; delete it by hand if unneeded")
                lines.append(f"{name}: kept ({reason})")
                continue
            if not dry_run:
                path.unlink()
                prune_empty(root, path.parent)
            lines.append(f"{name}: {verb}")
        if relative.endswith("/.gitignore") and policy == "file":
            state = (root / relative).parent
            if state.is_dir() and any(entry.name != ".gitignore" for entry in state.iterdir()):
                lines.append(f"{PurePosixPath(relative).parent.as_posix()}/: kept (holds run records)")
    return lines


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install the alchemy-orchestrate runtime adapters.")
    parser.add_argument("--runtime", required=True, choices=[*RUNTIMES, "all"])
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="project directory (default: cwd)")
    parser.add_argument("--profile", type=Path, help="project alchemy-workspace.json (default: <root>/"
                        f"{PROFILE_NAME} when present)")
    parser.add_argument("--dry-run", action="store_true", help="report what would change; write nothing")
    parser.add_argument("--uninstall", action="store_true",
                        help="remove the files an install would write, where still unedited")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        root = args.root.resolve()
        if not root.is_dir():
            raise UsageError(f"--root {args.root} is not a directory")
        overlay = args.profile.resolve() if args.profile else None
        if overlay is not None and not overlay.is_file():
            raise UsageError(f"--profile {args.profile} is not a file")
        if overlay is None and (root / PROFILE_NAME).is_file():
            overlay = root / PROFILE_NAME
        profile = load_profile(overlay)
        runtimes = list(RUNTIMES) if args.runtime == "all" else [args.runtime]
        writes = plan_writes(runtimes, root, overlay, args.profile is not None, profile)
        lines = (uninstall if args.uninstall else install)(root, writes, args.dry_run)
    except UsageError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
