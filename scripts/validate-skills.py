from pathlib import Path
import json
import re
import subprocess
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
ALCHEMY_DISPATCH_STATES = ("SKIP", "DIRECT", "ADAPTIVE", "FULL")
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
PYTHON_CACHE_SUFFIXES = {".pyc", ".pyo"}
PRIMER_REQUIRED_TERMS = {
    "alchemy": (
        "Requirements Qualification Phase",
        "Dispatch behavior",
        "do some alchemy",
        "companion skills",
        "requirements-grounding",
        "requirements-topology",
        "implementation-readiness",
        "requirements-traceability",
        "PARTLY-READY",
        "C₀",
        "L candidate → C measurement → L acceptance",
    ),
    "architecture-as-code": (
        "`architecture-guidelines` or `morphogenetic-architecture`",
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
    "morphogenetic-architecture": (
        "Declared topology",
        "Observed fields",
        "Rapid topology scan",
        "Rapid → Full",
        "Analysis mode:",
        "Selection reason:",
        "runtime feedback loops",
        "Reproducible graph analysis",
        "Decision policy:",
        "Graph analysis:",
        "Natural pattern atlas",
        "Nature may propose",
        "Reversibility:",
        "operational lens index",
        "Candidate baseline:",
        "held-out evidence window",
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
        "Dispatch Preflight",
        "Companion Skill Routing",
        "do some alchemy",
        "Dispatch:   <SKIP | DIRECT | ADAPTIVE | FULL>",
        "Core route:",
        "Companions:",
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
        "L candidate → C measurement → L acceptance",
        "Gate E remains blocked",
        "one candidate may re-enter Gate 3 only",
    ),
    "architecture-as-code": (
        "`architecture-guidelines` or `morphogenetic-architecture`",
    ),
    "architecture-as-code-javascript": (
        "no-restricted-syntax",
        "ImportExpression",
        "Production code must not import test-only code.",
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
    "morphogenetic-architecture": (
        "Declare before observing",
        "Keep projections distinct",
        "Transfer mechanisms, not silhouettes",
        "Select the Analysis Mode",
        "references/rapid-topology-scan.md",
        "Otherwise start in **Rapid**",
        "Escalate from Rapid to Full",
        "Once Full begins, do not downgrade",
        "boundary-pressure mismatch",
        "DECLARE-RUNTIME-CYCLE",
        "Always emit the summary block",
        "Decision:            PLACE",
        "references/evidence-fields.md",
        "references/graph-analysis.md",
        "references/natural-pattern-atlas.md",
        "retained executable output",
        "Decision policy:",
        "Graph analysis:",
        "Analysis mode:",
        "Selection reason:",
        "Natural lens:",
        "Candidate baseline:",
        "Lens contribution:",
        "Lens falsifier:",
        "unused independent field or a",
        "Transfer:",
        "Emit DEFER",
        "Scale proof to reversibility",
        "### Scale Proof to Reversibility",
        "Grade only when a boundary actually moves",
        "Reversibility:       <high | medium | low",
        "Unknown — Low bar applies",
    ),
    "requirements-traceability": (
        "Trace both directions",
        "Implementation is not verification",
        "Evidence States",
        "CI Enforcement",
        "TRACEABLE",
        "Stale references:",
    ),
    "structural-simplification": (
        "enforceable static constraints to `architecture-as-code`",
    ),
}
STRUCTURAL_REPORT_FIELDS = (
    "Subject",
    "Decision",
    "Component-kinds Δ",
    "Dependency-edges Δ",
    "Max-chain-depth Δ",
    "Module-count Δ",
    "Cycle",
    "Non-structural gates",
    "Trade-off",
    "Rationale",
    "Next action",
    "Verification",
)
MORPHOGENETIC_REPORT_FIELDS = (
    "Subject",
    "Mode",
    "Analysis mode",
    "Selection reason",
    "Decision",
    "Declared topology",
    "Observed fields",
    "Decision policy",
    "Graph analysis",
    "Candidate baseline",
    "Natural lens",
    "Lens contribution",
    "Lens falsifier",
    "Transfer",
    "Static cycle",
    "Runtime cycles",
    "Boundary evidence",
    "Reversibility",
    "Enforcement",
    "Measurement",
    "Next action",
    "Verification",
)
NATURAL_PATTERN_FAMILIES = (
    "### Pattern and Differentiation",
    "### Transport and Connection",
    "### Persistence and Renewal",
)
NATURAL_PATTERN_OPERATIONAL_LENSES = (
    "Cell differentiation",
    "Segmentation",
    "Convergent evolution",
    "Hierarchical branching",
    "Physarum",
    "Leaf venation",
    "Stigmergy",
    "Endosymbiosis",
    "Homeostasis",
    "Bone remodeling",
    "Quorum sensing",
    "Apoptosis",
)
NATURAL_PATTERN_NON_OPERATIONAL = (
    "Reaction–diffusion",
    "Phyllotaxis",
    "Cymatics",
    "Canalization",
)
MORPHOGENETIC_DECISIONS = (
    "PLACE",
    "KEEP",
    "MOVE",
    "SPLIT",
    "MERGE",
    "INTRODUCE-BOUNDARY",
    "DECLARE-RUNTIME-CYCLE",
    "DEFER",
)
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


def mirror_source_files(skill: Path) -> set[Path]:
    """Return authored skill files, excluding interpreter-generated caches."""
    files = set()
    for path in skill.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(skill)
        if "__pycache__" in relative.parts or relative.suffix in PYTHON_CACHE_SUFFIXES:
            continue
        files.add(relative)
    return files


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
        claude_files = mirror_source_files(claude[name])
        agent_files = mirror_source_files(agents[name])
        if claude_files != agent_files:
            fail(f"mirror file-set mismatch for {name}")
        for relative in sorted(claude_files):
            if (claude[name] / relative).read_bytes() != (
                agents[name] / relative
            ).read_bytes():
                fail(f"mirror mismatch for {name}/{relative.as_posix()}")


def validate_retired_skill_references() -> None:
    retired_terms = (
        "geometric-architecture",
        "geometric architecture",
        "geometric placement",
        "non-adjacent faces",
        "non-adjacent import",
        "face-adjacent",
        "spatial rationale",
        "spatial placement",
        "wormhole",
        "domain / tier / layer grid",
    )
    paths = [
        ROOT / "README.md",
        ROOT / "CLAUDE.md",
        ROOT / "ALCHEMY-PIPELINE-DESIGN.md",
        *DOCS.glob("*.md"),
        *DOCS.glob("*.svg"),
        *ROOT.glob("*.svg"),
        *(path / "SKILL.md" for path in skill_dirs(CLAUDE_SKILLS)),
        *(path / "SKILL.md" for path in skill_dirs(AGENT_SKILLS)),
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8").casefold()
        for retired in retired_terms:
            if retired.casefold() in text:
                fail(f"{path.relative_to(ROOT)} references retired term '{retired}'")


def markdown_section(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    start = text.find(heading)
    if start == -1:
        fail(f"{path.relative_to(ROOT)} missing section '{heading}'")
    next_heading = re.search(r"^##\s+", text[start + len(heading) :], re.M)
    end = (
        start + len(heading) + next_heading.start()
        if next_heading
        else len(text)
    )
    return text[start:end]


def validate_report_fields(
    path: Path, heading: str, required_fields: tuple[str, ...]
) -> None:
    section = markdown_section(path, heading)
    match = re.search(r"```(?:text)?\s*\r?\n(.*?)```", section, re.S)
    if not match:
        fail(f"{path.relative_to(ROOT)} section '{heading}' missing report block")
    report = match.group(1)
    for field in required_fields:
        if not re.search(rf"^{re.escape(field)}:\s*", report, re.M):
            fail(
                f"{path.relative_to(ROOT)} section '{heading}' "
                f"missing report field '{field}:'"
            )


def validate_sample_reports() -> None:
    path = DOCS / "sample-reports-verification.md"
    validate_report_fields(
        path,
        "## (a) Prospective complexity report",
        STRUCTURAL_REPORT_FIELDS,
    )
    validate_report_fields(
        path,
        "## (b) Retrospective audit report",
        STRUCTURAL_REPORT_FIELDS,
    )
    validate_report_fields(
        path,
        "## (c) Placement report",
        MORPHOGENETIC_REPORT_FIELDS,
    )
    validate_report_fields(
        path,
        "## (d) Escalated topology report",
        MORPHOGENETIC_REPORT_FIELDS,
    )


def validate_morphogenetic_public_vocabulary() -> None:
    contracts = (
        ROOT / "README.md",
        DOCS / "morphogenetic_architecture.svg",
    )
    for path in contracts:
        text = path.read_text(encoding="utf-8")
        for decision in MORPHOGENETIC_DECISIONS:
            if decision not in text:
                fail(
                    f"{path.relative_to(ROOT)} missing morphogenetic decision "
                    f"'{decision}'"
                )


def validate_morphogenetic_mode_selection() -> None:
    skill = AGENT_SKILLS / "morphogenetic-architecture" / "SKILL.md"
    rapid = (
        AGENT_SKILLS
        / "morphogenetic-architecture"
        / "references"
        / "rapid-topology-scan.md"
    )
    metadata = (
        AGENT_SKILLS
        / "morphogenetic-architecture"
        / "agents"
        / "openai.yaml"
    )

    if not rapid.is_file():
        fail(f"{rapid.relative_to(ROOT)} is missing")

    required_skill_terms = (
        "## Select the Analysis Mode",
        "Start in **Full**",
        "Otherwise start in **Rapid**",
        "Escalate from Rapid to Full",
        "MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY becomes a candidate",
        "A bare Alchemy `FULL` dispatch",
        "Once Full begins, do not downgrade",
        "Rapid may finish only with PLACE, KEEP, DECLARE-RUNTIME-CYCLE, or DEFER",
        "Analysis mode:       Rapid | Full | Rapid → Full",
        "Selection reason:",
    )
    skill_text = skill.read_text(encoding="utf-8")
    for term in required_skill_terms:
        if term not in skill_text:
            fail(f"{skill.relative_to(ROOT)} missing mode-selection term '{term}'")

    required_rapid_terms = (
        "Rapid must not evaluate weighted fields",
        "Do not emit MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY as a final Rapid",
        "Set `Analysis mode: Rapid → Full`",
        "Once escalated, remain in Full",
        "Missing evidence produces DEFER",
    )
    rapid_text = rapid.read_text(encoding="utf-8")
    for term in required_rapid_terms:
        if term not in rapid_text:
            fail(f"{rapid.relative_to(ROOT)} missing Rapid guard '{term}'")

    metadata_text = metadata.read_text(encoding="utf-8")
    for term in ("Rapid placement", "escalate to full evidence-driven analysis"):
        if term not in metadata_text:
            fail(f"{metadata.relative_to(ROOT)} missing mode metadata '{term}'")

    public_contracts = {
        ROOT / "README.md": (
            "Rapid placement/static-edge scan",
            "Rapid →",
            "restructure · non-static evidence · broad scope · ambiguity",
        ),
        ROOT / "CLAUDE.md": ("start in Rapid", "Rapid → Full", "`Selection reason`"),
        ROOT / "ALCHEMY-PIPELINE-DESIGN.md": (
            "starts in Rapid",
            "cannot bypass `Rapid → Full`",
            "`Analysis mode` plus `Selection reason`",
        ),
        DOCS / "READ-alchemy.md": (
            "starts in Rapid",
            "`Rapid → Full` escalation",
            "`Selection reason`",
        ),
        DOCS / "READ-morphogenetic-architecture.md": (
            "Rapid topology scan",
            "Rapid → Full",
            "Analysis mode:",
            "Selection reason:",
        ),
        DOCS / "morphogenetic_architecture.svg": (
            "RAPID BY DEFAULT",
            "FULL FOR RESTRUCTURING",
        ),
        CLAUDE_SKILLS / "alchemy" / "SKILL.md": (
            "starts in Rapid",
            "`Rapid → Full` escalation",
            "`Selection reason`",
            "Alchemy `FULL` is a traversal dispatch",
        ),
    }
    for path, terms in public_contracts.items():
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                fail(
                    f"{path.relative_to(ROOT)} missing morphogenetic mode "
                    f"contract '{term}'"
                )

    samples = DOCS / "sample-reports-verification.md"
    sample_text = samples.read_text(encoding="utf-8")
    for term in ("Analysis mode:       Rapid", "Analysis mode:       Rapid → Full"):
        if term not in sample_text:
            fail(f"{samples.relative_to(ROOT)} missing mode sample '{term}'")


def validate_morphogenetic_graph_analyzer() -> None:
    skill = AGENT_SKILLS / "morphogenetic-architecture"
    analyzer = skill / "scripts" / "analyze_evidence_graph.py"
    reference = skill / "references" / "graph-analysis.md"
    if not analyzer.is_file():
        fail(f"{analyzer.relative_to(ROOT)} is missing")
    if not reference.is_file():
        fail(f"{reference.relative_to(ROOT)} is missing")

    reference_text = reference.read_text(encoding="utf-8")
    required = (
        "Declare the decision policy before",
        "scripts/analyze_evidence_graph.py",
        "architecture_decision",
        "NOT_EVALUATED",
        "Never reconstruct SCCs",
    )
    for term in required:
        if term not in reference_text:
            fail(f"{reference.relative_to(ROOT)} missing required term '{term}'")

    try:
        completed = subprocess.run(
            [sys.executable, str(analyzer), "--self-test"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired:
        fail(f"{analyzer.relative_to(ROOT)} self-test timed out")
    if completed.returncode != 0 or "self-test: pass" not in completed.stdout:
        detail = (completed.stderr or completed.stdout).strip()
        fail(f"{analyzer.relative_to(ROOT)} self-test failed: {detail}")


def validate_morphogenetic_pattern_atlas() -> None:
    atlas = (
        AGENT_SKILLS
        / "morphogenetic-architecture"
        / "references"
        / "natural-pattern-atlas.md"
    )
    if not atlas.is_file():
        fail(f"{atlas.relative_to(ROOT)} is missing")

    atlas_text = atlas.read_text(encoding="utf-8")
    if "## Operational Lens Index" not in atlas_text:
        fail(f"{atlas.relative_to(ROOT)} missing '## Operational Lens Index'")
    for family in NATURAL_PATTERN_FAMILIES:
        if family not in atlas_text:
            fail(f"{atlas.relative_to(ROOT)} missing lens family '{family}'")

    primer = DOCS / "READ-morphogenetic-architecture.md"
    primer_text = primer.read_text(encoding="utf-8")
    index_start = atlas_text.index("## Operational Lens Index")
    index_end = atlas_text.find("\n## ", index_start + 3)
    index_text = atlas_text[index_start:index_end]

    for term in (
        "## Candidate-Contribution Test",
        "lens-free baseline candidate",
        "observable condition",
        "`explanation only`",
        "reused as prospective validation",
        "| Natural architecture | Transferable mechanism | Software use | Required evidence | Reject when |",
    ):
        if term not in atlas_text:
            fail(f"{atlas.relative_to(ROOT)} missing contribution guard '{term}'")

    for lens in NATURAL_PATTERN_OPERATIONAL_LENSES:
        if lens not in atlas_text:
            fail(f"{atlas.relative_to(ROOT)} missing lens '{lens}'")
        if lens not in primer_text:
            fail(f"{primer.relative_to(ROOT)} missing lens '{lens}'")
        if lens not in index_text:
            fail(f"{atlas.relative_to(ROOT)} operational index missing '{lens}'")

    for lens in NATURAL_PATTERN_NON_OPERATIONAL:
        if lens not in atlas_text:
            fail(f"{atlas.relative_to(ROOT)} missing non-operational lens '{lens}'")
        if lens not in primer_text:
            fail(f"{primer.relative_to(ROOT)} missing non-operational lens '{lens}'")
        if lens in index_text:
            fail(
                f"{atlas.relative_to(ROOT)} operational index must not route "
                f"non-operational lens '{lens}'"
            )


def validate_morphogenetic_reversibility() -> None:
    skill = AGENT_SKILLS / "morphogenetic-architecture"
    contracts = {
        skill / "references" / "rapid-topology-scan.md": (
            "**Grade reversibility, but only when a boundary would move.**",
            "`Reversibility`",
            "A Low grade or Unknown reversibility never lets Rapid accept",
        ),
        skill / "references" / "evidence-fields.md": (
            "## Field Authority",
            "Reversal cost",
            "dominant reversal-cost driver",
            "Use this authority mapping for the dominant driver",
        ),
        DOCS / "READ-morphogenetic-architecture.md": (
            "Reversibility sets the evidence bar",
            "It applies only where a boundary actually moves",
            "Reversibility: Unknown — Low bar applies",
            "separately specified precursor",
        ),
    }
    for path, terms in contracts.items():
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                fail(
                    f"{path.relative_to(ROOT)} missing reversibility contract "
                    f"'{term}'"
                )


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


def validate_overview_skill_count() -> None:
    path = ROOT / "alchemy-overview.svg"
    text = path.read_text(encoding="utf-8")
    expected = f"{len(skill_dirs(CLAUDE_SKILLS))} SKILLS"
    if expected not in text:
        fail(f"{path.relative_to(ROOT)} must report '{expected}'")


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


def validate_alchemy_dispatch_contract() -> None:
    path = CLAUDE_SKILLS / "alchemy" / "SKILL.md"
    text = path.read_text(encoding="utf-8")

    preflight = text.find("### Dispatch Preflight")
    qualification = text.find("## 2. Adaptive Requirements Qualification")
    if preflight == -1 or qualification == -1 or preflight > qualification:
        fail(f"{path.relative_to(ROOT)} must dispatch before qualification")

    for state in ALCHEMY_DISPATCH_STATES:
        if f"`{state}`" not in text:
            fail(f"{path.relative_to(ROOT)} missing dispatch state '{state}'")

    required = (
        "Classify before reading any sibling skill body",
        "Make dispatch the first observable checkpoint",
        "do not scan the repository",
        "Natural language stays adaptive",
        "`SKIP` skips only the Alchemy core",
        "never suppresses a matching companion",
        "only explicit full language selects `FULL`",
    )
    for term in required:
        if term not in text:
            fail(f"{path.relative_to(ROOT)} missing dispatch rule '{term}'")

    public_contracts = {
        ROOT / "README.md": ("do some alchemy", "Dispatch:", "Companions:"),
        ROOT / "CLAUDE.md": ("do some alchemy", "`SKIP` routine", "`FULL` only"),
        ROOT / "ALCHEMY-PIPELINE-DESIGN.md": (
            "Dispatch preflight",
            "do some alchemy",
            "companion skills",
        ),
        DOCS / "READ-alchemy.md": ("Dispatch behavior", "do some alchemy", "companion skills"),
    }
    for contract_path, terms in public_contracts.items():
        contract = contract_path.read_text(encoding="utf-8")
        for term in terms:
            if term not in contract:
                fail(
                    f"{contract_path.relative_to(ROOT)} missing Alchemy dispatch term '{term}'"
                )


def validate_alchemy_topology_handshake() -> None:
    handshake = "L candidate → C measurement → L acceptance"
    contracts = {
        CLAUDE_SKILLS / "alchemy" / "SKILL.md": "Gate E remains blocked",
        ROOT / "README.md": "Gate E cannot run before",
        ROOT / "CLAUDE.md": "E remains blocked until",
        ROOT / "ALCHEMY-PIPELINE-DESIGN.md": "blocks E until",
        DOCS / "READ-alchemy.md": "Gate E remains blocked until",
    }
    for path, blocking_term in contracts.items():
        text = path.read_text(encoding="utf-8")
        if handshake not in text:
            fail(
                f"{path.relative_to(ROOT)} missing bounded topology handshake "
                f"'{handshake}'"
            )
        if blocking_term not in text:
            fail(
                f"{path.relative_to(ROOT)} missing topology enforcement block "
                f"'{blocking_term}'"
            )
        if "once" not in text and "one L re-entry" not in text:
            fail(
                f"{path.relative_to(ROOT)} must bound topology acceptance "
                "to one L re-entry"
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
        "do some alchemy",
        "`SKIP` routine",
        "`FULL` only",
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
    validate_retired_skill_references()
    validate_morphogenetic_mode_selection()
    validate_morphogenetic_graph_analyzer()
    validate_morphogenetic_pattern_atlas()
    validate_morphogenetic_reversibility()
    validate_sample_reports()
    validate_morphogenetic_public_vocabulary()
    validate_primers()
    validate_readme_index()
    validate_overview_skill_count()
    validate_generic_requirements()
    validate_alchemy_pipeline()
    validate_alchemy_dispatch_contract()
    validate_alchemy_topology_handshake()
    validate_alchemy_root_guidance()
    validate_design_and_release_contracts()
    validate_contribution_contract()
    validate_public_doc_drift()
    print("Skills validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
