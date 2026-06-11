from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_SKILLS = ROOT / ".claude" / "skills"
AGENT_SKILLS = ROOT / ".agents" / "skills"
DOCS = ROOT / ".documentation"
MAX_DESCRIPTION = 1024


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def skill_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").exists())


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        fail(f"{path.relative_to(ROOT)} missing YAML frontmatter")

    fields: dict[str, str] = {}
    lines = match.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" not in line:
            i += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == ">-":
            block: list[str] = []
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                block.append(lines[i].strip())
                i += 1
            fields[key] = " ".join(block).strip()
            continue
        fields[key] = value.strip('"').strip("'")
        i += 1
    return fields


def validate_skill(path: Path) -> None:
    fields = parse_frontmatter(path / "SKILL.md")
    expected = path.name
    name = fields.get("name", "")
    description = fields.get("description", "")
    if name != expected:
        fail(f"{path.relative_to(ROOT)} name '{name}' does not match folder '{expected}'")
    if not description:
        fail(f"{path.relative_to(ROOT)} missing description")
    if len(description) > MAX_DESCRIPTION:
        fail(
            f"{path.relative_to(ROOT)} description too long "
            f"({len(description)} > {MAX_DESCRIPTION})"
        )


def validate_root(root: Path) -> None:
    for path in skill_dirs(root):
        validate_skill(path)


def validate_mirrors() -> None:
    claude = {path.name: path for path in skill_dirs(CLAUDE_SKILLS)}
    agents = {path.name: path for path in skill_dirs(AGENT_SKILLS)}
    if set(claude) != set(agents):
        missing_agents = sorted(set(claude) - set(agents))
        missing_claude = sorted(set(agents) - set(claude))
        if missing_agents:
            fail(f".agents missing mirrors: {', '.join(missing_agents)}")
        if missing_claude:
            fail(f".claude missing mirrors: {', '.join(missing_claude)}")

    for name in sorted(claude):
        claude_text = (claude[name] / "SKILL.md").read_text(encoding="utf-8")
        agent_text = (agents[name] / "SKILL.md").read_text(encoding="utf-8")
        if claude_text != agent_text:
            fail(f"mirror mismatch for {name}")


def validate_primers() -> None:
    skills = {path.name for path in skill_dirs(CLAUDE_SKILLS)}
    primers = {path.stem.removeprefix("READ-") for path in DOCS.glob("READ-*.md")}
    missing = sorted(skills - primers)
    orphan = sorted(primers - skills)
    if missing:
        fail(f"missing primers: {', '.join(missing)}")
    if orphan:
        fail(f"orphan primers: {', '.join(orphan)}")


def main() -> int:
    validate_root(CLAUDE_SKILLS)
    validate_root(AGENT_SKILLS)
    validate_mirrors()
    validate_primers()
    print("Skills validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
