from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_SKILLS = ROOT / ".claude" / "skills"
AGENT_SKILLS = ROOT / ".agents" / "skills"
DOCS = ROOT / ".documentation"
MAX_DESCRIPTION = 1024
OUTPUT_MARKERS = (
    "Output Contract",
    "Audit Output",
    "Emit one coder-facing",
    "Emit a coder-facing",
)
PRIMER_REQUIRED_TERMS = {
    "bring-down": (
        "L4 CODE",
        "L3 LIB",
        "L2 STD",
        "L1 PLP",
        "L0 SRVC",
        "same-team",
    ),
}
PUBLIC_DOC_FORBIDDEN = {
    "bring-down old public model": {
        "files": (
            ROOT / "README.md",
            DOCS / "READ-bring-down.md",
            DOCS / "READ-push-out.md",
        ),
        "patterns": (
            "reusable components, patterns",
            "components, patterns, platform primitives",
            "Componentized",
            "Patternized / templated",
            "Level 0",
            "Level 5",
        ),
    },
}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def skill_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.iterdir() if path.is_dir() and (path / "SKILL.md").exists())


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
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
    skill_file = path / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    fields = parse_frontmatter(skill_file)
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
    if not re.search(r"^#\s+\S", text, re.M):
        fail(f"{skill_file.relative_to(ROOT)} missing top-level heading")
    if not any(marker in text for marker in OUTPUT_MARKERS):
        fail(f"{skill_file.relative_to(ROOT)} missing coder-facing output marker")


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
    for name in sorted(skills):
        primer = DOCS / f"READ-{name}.md"
        text = primer.read_text(encoding="utf-8")
        expected_link = f"../.claude/skills/{name}"
        if expected_link not in text:
            fail(f"{primer.relative_to(ROOT)} missing canonical skill backlink")
        for term in PRIMER_REQUIRED_TERMS.get(name, ()):
            if term not in text:
                fail(f"{primer.relative_to(ROOT)} missing required term '{term}'")


def validate_readme_index() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for path in skill_dirs(CLAUDE_SKILLS):
        name = path.name
        skill_link = f"./.claude/skills/{name}/SKILL.md"
        primer_link = f"./.documentation/READ-{name}.md"
        if skill_link not in text:
            fail(f"README.md missing skill link for {name}")
        if primer_link not in text:
            fail(f"README.md missing primer link for {name}")


def validate_public_doc_drift() -> None:
    for rule, config in PUBLIC_DOC_FORBIDDEN.items():
        for path in config["files"]:
            text = path.read_text(encoding="utf-8")
            for pattern in config["patterns"]:
                if pattern in text:
                    fail(
                        f"{path.relative_to(ROOT)} contains stale public-doc "
                        f"pattern for {rule}: {pattern!r}"
                    )


def main() -> int:
    validate_root(CLAUDE_SKILLS)
    validate_root(AGENT_SKILLS)
    validate_mirrors()
    validate_primers()
    validate_readme_index()
    validate_public_doc_drift()
    print("Skills validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
