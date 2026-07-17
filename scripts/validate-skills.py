from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_SKILLS = ROOT / ".claude" / "skills"
AGENT_SKILLS = ROOT / ".agents" / "skills"
DOCS = ROOT / ".documentation"
MAX_DESCRIPTION = 1024
ALCHEMY_PIPELINE_STAGES = (
    "Requirements Grounding",
    "M — Minimum",
    "Requirements Topology",
    "Implementation Readiness",
    "A — Architecture",
)
CI_CD_RELEASE_STATES = (
    "BUILD-VERIFIED",
    "RELEASE-READY",
    "DEPLOYING",
    "PRODUCTION-VERIFYING",
    "DEPLOYED-HEALTHY",
)
OUTPUT_MARKERS = (
    "Output Contract",
    "Audit Output",
    "Emit one coder-facing",
    "Emit a coder-facing",
)
PRIMER_REQUIRED_TERMS = {
    "alchemy": (
        "Requirements Qualification Phase",
        "requirements-grounding",
        "requirements-topology",
        "implementation-readiness",
        "requirements-traceability",
        "PARTLY-READY",
        "C₀",
    ),
    "bring-down": (
        "L4 CODE",
        "L3 LIB",
        "L2 STD",
        "L1 PLP",
        "L0 SRVC",
        "same-team",
    ),
    "ci-cd-reliability-architecture": (
        "Release and production promotion",
        "BUILD-VERIFIED",
        "PRODUCTION-VERIFYING",
        "DEPLOYED-HEALTHY",
    ),
    "continuous-improvement": (
        "consumer project",
        "canonical library",
        "repinning the consumer",
    ),
    "requirements-grounding": (
        "project profile",
        "canonical editable source",
        "generated registers",
    ),
    "requirements-topology": (
        "Repository enforcement",
        "Semantic checks",
        "blocking CI backstop",
    ),
    "implementation-readiness": (
        "Post-readiness traceability",
        "requirements-traceability",
        "independent",
    ),
    "requirements-traceability": (
        "bidirectional",
        "implemented",
        "verified",
        "CI enforcement",
    ),
}
SKILL_REQUIRED_TERMS = {
    "alchemy": (
        "Adaptive Requirements Qualification",
        "requirements-grounding",
        "requirements-topology",
        "implementation-readiness",
        "requirements-traceability",
        "PARTLY-READY",
        "NOT-GROUNDED",
        "NOT-READY",
        "Focused aliases never silently run requirements qualification",
        "Blocking stage:",
        "C₀",
    ),
    "ci-cd-reliability-architecture": (
        "Release and Production Promotion",
        "BUILD-VERIFIED",
        "PRODUCTION-VERIFYING",
        "DEPLOYED-HEALTHY",
        "Rollback:",
        "Owner handoff:",
    ),
    "continuous-improvement": (
        "Consumer-to-Library Promotion",
        "Promote Before Repinning",
        "consumer project",
    ),
    "requirements-grounding": (
        "requirements-topology",
        "GROUNDED",
        "PROVISIONAL",
        "NOT-GROUNDED",
        "Compose; do not fork",
        "canonical editable requirement source",
    ),
    "requirements-topology": (
        "requirements-grounding",
        "implementation-readiness",
        "requirements-traceability",
        "Repository Operationalization",
        "Semantic validation",
        "Generated views",
        "Cycle:             Pass | Fail | Not evaluated",
        "STABLE",
        "BLOCKED",
    ),
    "implementation-readiness": (
        "requirements-grounding",
        "requirements-topology",
        "requirements-traceability",
        "READY",
        "PARTLY-READY",
        "NOT-READY",
        "independent states",
    ),
    "requirements-traceability": (
        "Trace both directions",
        "Implementation is not verification",
        "Evidence States",
        "CI Enforcement",
        "TRACEABLE",
        "Stale references:",
    ),
}
GENERIC_REQUIREMENTS_SKILLS = (
    "requirements-grounding",
    "requirements-topology",
    "implementation-readiness",
    "requirements-traceability",
)
GENERIC_REQUIREMENTS_FORBIDDEN = (
    "PayQuality",
    "PayLens",
    "docs/requirements",
    "npm run requirements",
)
CONTRIBUTION_REQUIRED_TERMS = (
    "canonical source for generic skill method",
    "Consumer-to-library promotion loop",
    "Publish, then repin",
    "project overlay",
)
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
    for term in SKILL_REQUIRED_TERMS.get(name, ()):
        if term not in text:
            fail(f"{skill_file.relative_to(ROOT)} missing required term '{term}'")


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


def validate_generic_requirements() -> None:
    for name in GENERIC_REQUIREMENTS_SKILLS:
        path = AGENT_SKILLS / name / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        for term in GENERIC_REQUIREMENTS_FORBIDDEN:
            if term in text:
                fail(f"{path.relative_to(ROOT)} contains project-specific term '{term}'")


def validate_alchemy_pipeline() -> None:
    path = CLAUDE_SKILLS / "alchemy" / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"## 2\. Adaptive Requirements Qualification.*?```text\s+(.*?)```",
        text,
        re.S,
    )
    if not match:
        fail(f"{path.relative_to(ROOT)} missing adaptive pipeline block")

    pipeline = match.group(1)
    positions = [pipeline.find(stage) for stage in ALCHEMY_PIPELINE_STAGES]
    if -1 in positions or positions != sorted(positions):
        fail(
            f"{path.relative_to(ROOT)} adaptive pipeline must preserve order: "
            + " -> ".join(ALCHEMY_PIPELINE_STAGES)
        )


def validate_alchemy_root_guidance() -> None:
    path = ROOT / "CLAUDE.md"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"## 6\. Walk the adaptive pipeline in order(.*?)(?=\n## 7\.)", text, re.S)
    if not match:
        fail(f"{path.relative_to(ROOT)} missing adaptive pipeline guidance")

    guidance = match.group(1)
    positions = [guidance.find(stage) for stage in ALCHEMY_PIPELINE_STAGES]
    if -1 in positions or positions != sorted(positions):
        fail(
            f"{path.relative_to(ROOT)} adaptive pipeline must preserve order: "
            + " -> ".join(ALCHEMY_PIPELINE_STAGES)
        )

    required = (
        "Focused aliases stay focused",
        "PARTLY-READY",
        "NOT-GROUNDED",
        "BLOCKED",
        "NOT-READY",
        "C₀",
        "BUILD / KEEP / SIMPLIFY or stop",
    )
    for term in required:
        if term not in guidance:
            fail(f"{path.relative_to(ROOT)} missing Alchemy guidance term '{term}'")

    forbidden = ("Audits reverse", "PASS / DROP")
    for term in forbidden:
        if term in guidance:
            fail(f"{path.relative_to(ROOT)} contains stale Alchemy guidance '{term}'")


def validate_design_and_release_contracts() -> None:
    design = ROOT / "ALCHEMY-PIPELINE-DESIGN.md"
    text = design.read_text(encoding="utf-8")
    required = ("Status: Implemented", "Blocking stage: None", "## Acceptance Criteria")
    for term in required:
        if term not in text:
            fail(f"{design.relative_to(ROOT)} missing finalization term '{term}'")

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    if "ALCHEMY-PIPELINE-DESIGN.md" not in package.get("files", []):
        fail("package.json must publish ALCHEMY-PIPELINE-DESIGN.md")

    skill = CLAUDE_SKILLS / "ci-cd-reliability-architecture" / "SKILL.md"
    release = skill.read_text(encoding="utf-8")
    positions = [release.find(state) for state in CI_CD_RELEASE_STATES]
    if -1 in positions or positions != sorted(positions):
        fail(
            f"{skill.relative_to(ROOT)} must preserve release state order: "
            + " -> ".join(CI_CD_RELEASE_STATES)
        )


def validate_contribution_contract() -> None:
    path = ROOT / "CONTRIBUTING.md"
    text = path.read_text(encoding="utf-8")
    for term in CONTRIBUTION_REQUIRED_TERMS:
        if term not in text:
            fail(f"{path.relative_to(ROOT)} missing promotion term '{term}'")

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    if "CONTRIBUTING.md" not in package.get("files", []):
        fail("package.json must publish CONTRIBUTING.md")


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
    validate_generic_requirements()
    validate_alchemy_pipeline()
    validate_alchemy_root_guidance()
    validate_design_and_release_contracts()
    validate_contribution_contract()
    validate_public_doc_drift()
    print("Skills validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
