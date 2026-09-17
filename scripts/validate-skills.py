from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_SKILLS = ROOT / ".claude" / "skills"
AGENT_SKILLS = ROOT / ".agents" / "skills"
DOCS = ROOT / ".documentation"
INSTALL = ROOT / ".install"
MAX_DESCRIPTION = 1024
# Size budget, in whitespace-split words, for the two tiers an agent pays for
# on every load: the root instruction file on every turn of every consumer
# session, and each SKILL.md on every invocation. references/*.md load on
# demand and are the intended destination for moved sections, so they carry no
# budget. The ceiling is a ratchet, granular to 100 words: a file may not grow
# past its entry, and an entry may not sit 100 or more words above its file,
# so a trim lowers the entry in the same change and a growth raises it only
# with the rationale in the commit message.
SIZE_BUDGET_GRAIN = 100
SIZE_BUDGET_WORDS = {
    "CLAUDE.md": 1200,
    "alchemy": 4600,
    "architecture-as-code": 2700,
    "architecture-as-code-javascript": 2200,
    "architecture-as-code-python": 1500,
    "architecture-guidelines": 1900,
    "bring-down": 2800,
    "ci-cd-reliability-architecture": 3500,
    "continuous-improvement": 1300,
    "defect-shift-left": 2100,
    "evolutionary-database-design": 3300,
    "functionality-complexity-tradeoff": 4500,
    "implementation-readiness": 1900,
    "morphogenetic-architecture": 4700,
    "push-out": 1300,
    "requirements-grounding": 3100,
    "requirements-topology": 2000,
    "requirements-traceability": 2500,
    "structural-simplification": 2600,
    "system-optimization": 2600,
    "test-strategy": 2100,
    "zero-copy-requirements": 1700,
}
# The always-on description tier summed over every skill, same ratchet in
# characters: MAX_DESCRIPTION caps one skill, this caps the listing every
# session carries whether or not a skill is invoked.
DESCRIPTION_BUDGET_CHARS = 13500
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
# Every decision report leads with these, in this order -- CLAUDE.md section 14.
REPORT_BLOCKS = ("What I found", "Why it matters", "Do this first", "What I did not check")
PYTHON_CACHE_SUFFIXES = {".pyc", ".pyo"}
# Primers (.documentation/READ-*.md) are concept explainers for non-architect
# developers, not mirrors of skill operational contracts. Operational-contract
# terms are validated in SKILL.md, README.md, CLAUDE.md, and
# ALCHEMY-PIPELINE-DESIGN.md only; primers are checked structurally
# (existence, canonical backlink, README index links, forbidden legacy
# vocabulary) in validate_primers() and PUBLIC_DOC_FORBIDDEN, and for
# attention in validate_primer_revisions(): a primer carries the revision of
# the skill it was last re-read against and fails until restamped.
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
        "When current outcome evidence reaches a revisit trigger",
        "Gate E remains blocked",
        "one candidate may re-enter Gate 3 only",
        "predecessor is retired or marked lapsing",
        "### Change Primitives",
        "**Subsystem**",
        "**Aspect**",
        "**Increment**",
        "**Iteration**",
        "Decomposition and aspect extraction are different cuts",
        "select `zero-copy-requirements`",
    ),
    "architecture-as-code": (
        "`architecture-guidelines` or `morphogenetic-architecture`",
        "Coverage is two independent gates",
        "A file-existence rule is what catches an undeclared directory",
        "The same catch-all at the repository root inverts",
        "Forward EVERY field the subsystem schema defines",
        "The emitted rule block's file scope equals the linted source set.",
        "Every file at repository root belongs to a declared subsystem.",
        "A passing lint is not evidence of coverage.",
        # Expand step of the components -> subsystems key rename: the alias
        # rule stays documented until the contract step removes it.
        "`components` is accepted as a deprecated alias for `subsystems`",
        "rejects a file that carries both",
    ),
    "architecture-as-code-javascript": (
        "no-restricted-syntax",
        "ImportExpression",
        "Production code must not import test-only code.",
        "files: ['**/*.{js,jsx,mjs,ts,tsx}'],",
        "'boundaries/no-unknown-files': 'error',",
        "'boundaries/dependencies': ['error', { default: 'allow', rules }],",
        "a dependency rule at `warn` is a report rather than a boundary",
        "The broad glob is the point, not an accident",
        "second, independent gate",
        "decides what a pattern matches, and the default is",
        "partialMatch: false",
        "Confine a provider SDK to its adapter",
        "A provider SDK is an **npm package, not an element**",
        "to: { module: { origin: 'external', source: x.package } }",
        "Without `checkAllOrigins: true` the policy never fires",
        "subjects every package to the block's `default`",
        "Prove it red first",
        "`boundaries/external` still works and is deprecated in v7",
        "m.default.subsystems ?? m.default.components ?? []",
    ),
    "architecture-as-code-python": (
        "The graph root is the coverage gate",
        "root_package",
        'data.get("subsystems", data.get("components", []))',
    ),
    "architecture-guidelines": (
        "## 8. Layer Self-Sufficiency",
        "must hold with the endpoint publicly reachable",
        "are additional layers, never the control",
        "does this still hold when the layer below it disappears?",
        "## 9. Integration Discipline",
        "Smart endpoints, dumb pipes",
        "consumers transform",
        "No peer internals",
        "| atomicity | integration | layer-self-sufficiency |",
        "every rule above needs a question",
        "after the caller's own write",
        "Aspects are extracted, not interleaved",
        "Principle:   aspect coverage",
    ),
    "ci-cd-reliability-architecture": (
        "Release and Production Promotion",
        "BUILD-VERIFIED",
        "PRODUCTION-VERIFYING",
        "DEPLOYED-HEALTHY",
        "Rollback:",
        "Owner handoff:",
        "Choose the delivery strategy first",
        "Decouple deployment from release",
        "production-only",
        "never whether it runs",
        "Strategy:       <permanent | ephemeral | production-only progressive exposure>",
        "Environment parity / permanent stages only",
        "Representativeness:",
        "in-place subsystem replace",
        "Zero-downtime:  <yes | no + why>",
    ),
    "defect-shift-left": (
        "Aspect coverage gap",
        "a check nobody runs has zero shift-left value",
        "Use this only when the user asks for tooling recommendations",
        "A tool that does not map to a rung on the ladder has no place in the output",
    ),
    "bring-down": (
        "Bring down to the lowest responsible level",
        "A move that keeps the same maintenance owner is not bring-down",
        "no bring-down landing found",
        "Do not emit `L4 CODE to L4 CODE` moves",
    ),
    "push-out": (
        "Push work, not responsibility",
        "Standardize before automating",
        "Emit one action that advances exactly one rank",
        "Prose repeats an executable source of truth",
    ),
    "system-optimization": (
        "Question the requirement",
        "Most constraints are **policy**, not physical capacity",
        "cycle time = WIP / throughput",
        "Stabilize Before Optimizing",
        "is an iteration: its Check or Control",
    ),
    "continuous-improvement": (
        "Consumer-to-Library Promotion",
        "Promote Before Repinning",
        "consumer project",
        "a hypothesis, not a safeguard",
        "the observed failure without the rule",
    ),
    "requirements-grounding": (
        "requirements-topology",
        "GROUNDED",
        "PROVISIONAL",
        "NOT-GROUNDED",
        "Compose; do not fork",
        "canonical editable requirement source",
        "Completion is not impact",
        "## Outcome Hypothesis Shape",
        "Hypothesis confidence:",
        "Evidence state: unmeasured | supported | rejected | inconclusive | stale",
        "Evidence reference:",
        "Outcome hypotheses:",
        "M alone",
        "assess evidence state and freshness",
        "Supersedes:",
        "references/quality-model.md",
        "coverage finding, not evidence that none apply",
        "Quality coverage:",
        "Holds across:",
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
        "never retired",
        "Two active records for one obligation",
        "lapsing",
        "Retired:",
        "holds_across",
        "Aspect coverage:",
    ),
    "implementation-readiness": (
        "requirements-grounding",
        "requirements-topology",
        "requirements-traceability",
        "READY",
        "PARTLY-READY",
        "NOT-READY",
        "independent states",
        "carries the lapsing criteria",
        "Riskiest assumption first",
        "## Assumption Vehicles",
        "parallel-ready",
        "Parallel-ready: yes | no + missing criterion",
        "only on criteria readable from the artifacts",
        "An assumption invalidatable by inspection is resolved, not scheduled",
        "- Aspects:",
        "Aspects touched:",
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
        "Candidate baseline:",
        "generator's name, mechanism, or analogy may never appear in",
        "satisfy its Candidate-Contribution Test before the candidate counts",
        "Emit DEFER",
        "Scale proof to reversibility",
        "### Scale Proof to Reversibility",
        "Grade only when a boundary actually moves",
        "Reversibility:       <high | medium | low",
        "Unknown — Low bar applies",
        "Generate a Second Candidate",
        "Second candidate:",
        "### Probationary Acceptance",
        "Prediction:",
        "### Close the Loop",
        "declared-vs-observed",
        "cannot be measured within the decision window",
        "Unknown reversibility never accepts probationarily",
        "Probation covers absent evidence only",
        "Absent means unobtainable, not unfetched",
        "### Position Legality",
        "design-time check on a proposed or changed",
        "**layer inversion**",
        "**Inbound interface**",
        "| Ownership / authority | Directed, acyclic per aspect |",
        "Authority is acyclic **per aspect**, not per subsystem",
        "position-legality clauses first",
        "Position legality:   Pass | Fail",
        "durable register that the standing",
        "Seven fields form the **restructuring set**",
        "is never eligible for probation; measure it first",
        "The path exists only in Full",
        "Record **Prediction** for every accepted MOVE, SPLIT, MERGE, or",
        "Before accepting a Medium- or Low-reversibility restructuring",
        "must name which generators were attempted",
        "| Positions an aspect binds | **Holds across**",
    ),
    "requirements-traceability": (
        "Trace both directions",
        "Implementation is not verification",
        "Completion Evidence States",
        "Outcome Evidence States",
        "Completion is not outcome evidence",
        "Hypothesis version:",
        "Threshold evaluation:",
        "Freshness: current | stale",
        "Do not issue BUILD, KEEP, SIMPLIFY, DROP",
        "do not create an outcome-evidence record",
        "Formal Completion Records",
        "Completion record:",
        "CI Enforcement",
        "TRACEABLE",
        "Stale references:",
        "Every representation gap names its expiry condition",
        "`representation-aggregated`",
        "`representation-derived`",
        "`representation-projected`",
        "reject a representation gap that names no expiry condition",
        "domain and data model views",
        "| Domain or data model view |",
        "Representation gaps: <class, artifact, and expiry condition, or none>",
        "representation gaps carry expiry",
        "lapsing",
        "`aspect-uncovered`",
    ),
    "functionality-complexity-tradeoff": (
        "Outcome evidence informs worth; it is not the verdict",
        "`requirements-grounding`",
        "`requirements-traceability`",
        "Outcome evidence:",
        "no hypothesis state automatically",
        "Authoritative floors",
    ),
    "structural-simplification": (
        "enforceable static constraints to `architecture-as-code`",
    ),
    "test-strategy": (
        "Risk before test type",
        "Oracle before harness",
        "Minimum sufficient fidelity",
        "references/technique-selection.md",
        "references/portfolio-governance.md",
        "ADEQUATE | PARTIAL | NOT-ADEQUATE | DEFER",
        "`test-strategy` is a task-matched Alchemy companion",
        "Obligation pass — after readiness, before A",
        "Portfolio pass — after final A/L/C and E when applicable, before H",
        "System under test | exercised dependencies | environment | stimulus | oracle",
        "An Obligation pass is provisional by design and cannot emit `ADEQUATE`",
        "pipeline execution triggers",
        "quarantined test cannot count as verified evidence",
    ),
    "evolutionary-database-design": (
        "Every change is a refactoring, not an edit",
        "Compatible with every live version",
        "Expand before contract",
        "Meaning changes are new elements",
        "Absence of an import is not absence of a reader",
        "Compatibility pass — after readiness, before A",
        "Transition pass — after final A/L/C and E when applicable, before H",
        "COMPATIBLE | STAGED | BREAKING | DEFER",
        "`evolutionary-database-design` is a task-matched Alchemy companion",
        "A Compatibility pass is provisional by design",
        "the Transition pass precedes its Portfolio pass",
        "Expand and contract never ship in the same deployable",
        "The contract trigger is evidence",
        "A down-migration is a development convenience, not a rollback path",
        "Reversibility input:",
        "reversible data change",
        "irreversible data migration",
        "Do not infer absence of readers from absence of imports",
        "Coexisting clients:",
        "The coexistence window does not end where the deployment ends",
        "names the consumers it covers",
    ),
    "zero-copy-requirements": (
        "No artifact may exist whose content is fully reconstructable",
        "One question, one authority",
        "Decisions close where they were raised",
        "Sign-off is immutable",
        "Reports are compiled, never authored",
        "Frozen records are closed, not maintained",
        "`zero-copy-requirements` is a task-matched Alchemy companion",
        "PRIMITIVE | GENERATED-REPORT | EXCEPTION | DUPLICATE",
        "A document that needs two answers is two artifacts",
        "An artifact that fits no exception and duplicates a primitive is waste",
    ),
}
STRUCTURAL_REPORT_FIELDS = (
    "Subject",
    "Decision",
    "Subsystem-kinds Δ",
    "Dependency-edges Δ",
    "Max-chain-depth Δ",
    "Subsystem-count Δ",
    "Cycle",
    "Non-structural gates",
    "Trade-off",
    "Rationale",
    "Next action",
    "Verification",
)
MORPHOGENETIC_CORE_FIELDS = (
    "Subject",
    "Mode",
    "Analysis mode",
    "Selection reason",
    "Decision",
    "Declared topology",
    "Position legality",
    "Static cycle",
    "Runtime cycles",
    "Observed fields",
    "Boundary evidence",
    "Enforcement",
    "Next action",
    "Verification",
)
# Emitted only when a boundary actually moves or a DEFER withholds one.
MORPHOGENETIC_RESTRUCTURING_FIELDS = (
    "Decision policy",
    "Graph analysis",
    "Candidate baseline",
    "Second candidate",
    "Reversibility",
    "Prediction",
    "Measurement",
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
# The installers diverged once into four copies of the Claude script that
# differed only in the instruction filename, so three of them wrote skills to a
# tree their own agent never reads. The profile block is the ONLY licensed
# difference; everything else must stay byte-identical across the family.
INSTALLER_PROFILES = {
    "claude": ("CLAUDE.md", ".claude/skills"),
    "codex": ("AGENTS.md", ".agents/skills"),
    "gemini": ("GEMINI.md", ".agents/skills"),
    "grok": ("GROK.md", ".agents/skills"),
}
INSTALLER_PROFILE_RE = re.compile(
    r"# --- agent profile ---\n(.*?)# --- end agent profile ---", re.S
)
INSTALLER_HEADER_RE = re.compile(
    r"(?m)^# l-gevity-skills installer \(.*\)$|^# Usage: .*$"
)
CONSUMER_FORBIDDEN = (
    "PayQuality",
    "PayLens",
    "docs/requirements",
    "npm run requirements",
)
# Pinned phrases that live in a skill's references/*.md rather than SKILL.md.
# A reference file is loaded on demand, so the rule it carries is pinned to
# that file, and SKILL.md must link the file (validate_reference_links).
REFERENCE_REQUIRED_TERMS = {
    "alchemy": {
        "references/failure-modes.md": (
            "| Symptom | Skipped gate | Recovery |",
            "then re-enter Gate 3 once for final acceptance",
            "Split the deployable; gate the contract step on evidence and a snapshot",
            "DROP unless second use is named and probable",
            "a second authority cannot be kept in sync by discipline",
        ),
    },
    "morphogenetic-architecture": {
        "references/position-legality.md": (
            "Auditing a\nwhole codebase from three axes is an explicit non-goal",
            "Same tier, or a higher tier calling a lower tier",
            "can never orchestrate, so it cannot violate this clause",
            "unless either endpoint is the declared adapter",
            "**Re-export module**",
            "**External SDK**",
            "Containment is not distance",
            "None of this is sliceable",
            "**composition root**",
            "the domain clause needs a",
            "record it as **Not applicable** with the reason",
            "Domain is categorical",
        ),
        "references/graph-analysis.md": (
            "Never reconstruct SCCs, Fiedler vectors, cuts, or sensitivity results by prose",
            "`architecture_decision` is always `NOT_EVALUATED`",
        ),
        "references/rapid-topology-scan.md": (
            "Rapid must not evaluate weighted fields",
            "Do not emit MOVE, SPLIT, MERGE, or INTRODUCE-BOUNDARY as a final Rapid",
        ),
        "references/evidence-fields.md": (
            "Never let a field decide outside its",
            "When two fields disagree, do not average them",
            "Low confidence is never eligible for probation",
        ),
        "references/natural-pattern-atlas.md": (
            "## Candidate-Contribution Test",
            "A symbolic form never supplies the domain",
            "Mark them `inspiration only`",
        ),
    },
    "functionality-complexity-tradeoff": {
        "references/worth-signals.md": (
            "**Churn × complexity is a strong empirical signal**",
            "Usage silence and zero-everything signature look identical from",
        ),
        "references/common-patterns.md": (
            "Assertion that documents an invariant nothing else captures",
            "Compliance / audit / accessibility path",
        ),
        "references/forcing-questions.md": (
            "Answers MUST be written, not",
            "**Construct one concrete real-world sequence**",
            "this is a **one-way door**",
        ),
        "references/asymmetric-tradeoffs.md": (
            "**Raise the required `V` by one tier**",
            "**fixed-high `U`**",
            "**§8e is the inverse of the necessity gate.**",
        ),
    },
    "defect-shift-left": {
        "references/shift-patterns.md": (
            "### 6.6 Hand-checked aspect coverage",
            "The shift completes only when the strict typecheck is a **blocking gate**",
            "Two hand-written sources checking the same shape are the same-scope duplication",
            "This skill places the check; it does not design the oracle.",
        ),
        "references/tooling-survey.md": (
            "fitness-function runner",
            "Find specific options only on request",
            "Do not propose a tool without naming the stage it staffs",
        ),
    },
    "ci-cd-reliability-architecture": {
        "references/pipeline-patterns.md": (
            "never copy verbatim",
            "Always hash/checksum the definition",
            "Delete-before-create is an exception for provider constraints, not the default",
        ),
    },
    "requirements-grounding": {
        "references/quality-model.md": (
            "ISO/IEC 25010:2023",
            "Close an `open` characteristic by recording the measurement it needs",
        ),
    },
    "test-strategy": {
        "references/technique-selection.md": (
            "A sophisticated harness cannot repair an",
            "Human does not mean informal; automated does not mean objective",
            "Do not prescribe a universal unit/integration/E2E ratio",
        ),
        "references/portfolio-governance.md": (
            "A green result obtained after enough retries is not reliability",
            "Do not choose a universal coverage or mutation threshold",
            "| Aspect coverage result |",
        ),
    },
}
CONTRIBUTION_REQUIRED_TERMS = (
    "canonical source for generic skill method",
    "Consumer-to-library promotion loop",
    "Publish, then repin",
    "project overlay",
    "SIZE_BUDGET_WORDS",
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
    "parallel-ready assignee criterion": {
        "files": (DOCS / "READ-implementation-readiness.md",),
        "patterns": (
            "unassigned to anyone in particular",
            "unassigned to a specific person",
        ),
    },
}


def flatten(value: str) -> str:
    """Collapse line wrapping so a pinned phrase is not hostage to reflowing.

    Blockquote continuation markers are dropped, whitespace runs inside a block
    become one space, and blank-line boundaries are preserved so a phrase cannot
    match across two unrelated blocks.
    """
    value = re.sub(r"(?m)^[ \t]*>[ \t]?", "", value)
    blocks = re.split(r"\n\s*\n", value)
    return "\n\n".join(re.sub(r"\s+", " ", block).strip() for block in blocks)


def contains(text: str, phrase: str) -> bool:
    """True when `phrase` appears in `text`, ignoring how either is wrapped."""
    return flatten(phrase) in flatten(text)


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


MATCHER_SELF_TEST = (
    # (text, phrase, expected) — contains() is load-bearing for every
    # contract check below, so a regression there would silently pass them all.
    ("alpha beta\n   gamma delta", "beta gamma", True),
    ("one\n\ttwo", "one two", True),
    ("> quoted line\n>    wrapped on", "line wrapped", True),
    ("alpha beta gamma", "beta omega", False),
    ("ends here\n\nstarts there", "here starts", False),
    ("| A | B |\n| C | D |", "| A | B |", True),
    ("Dispatch:   <SKIP>", "Dispatch: <SKIP>", True),
    ("foo bar", "foobar", False),
)


def validate_matcher() -> None:
    for text, phrase, expected in MATCHER_SELF_TEST:
        if contains(text, phrase) is not expected:
            fail(
                f"contains({text!r}, {phrase!r}) returned {not expected}, "
                f"expected {expected}"
            )


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
    if not any(contains(text, marker) for marker in OUTPUT_MARKERS):
        fail(f"{skill_file.relative_to(ROOT)} missing coder-facing output marker")
    for term in SKILL_REQUIRED_TERMS.get(name, ()):
        if not contains(text, term):
            fail(f"{skill_file.relative_to(ROOT)} missing required term '{term}'")
    for relative, terms in REFERENCE_REQUIRED_TERMS.get(name, {}).items():
        reference = path / relative
        if not reference.is_file():
            fail(f"{path.relative_to(ROOT)}/{relative} is required")
        reference_text = reference.read_text(encoding="utf-8")
        for term in terms:
            if not contains(reference_text, term):
                fail(f"{reference.relative_to(ROOT)} missing required term '{term}'")


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


def validate_pin_coverage() -> None:
    # Aspect coverage for "rules pinned so drift fails the build": the pinned
    # phrases themselves are checked per file by validate_skill(), but a skill
    # or reference with no entry passes that check vacuously. This walks the
    # registry and fails on every uncovered cell, which a green pin check can
    # never report.
    for path in skill_dirs(AGENT_SKILLS):
        name = path.name
        if not SKILL_REQUIRED_TERMS.get(name):
            fail(f"{name}/SKILL.md has no pinned phrases; add a SKILL_REQUIRED_TERMS entry")
        references_dir = path / "references"
        if not references_dir.is_dir():
            continue
        pinned = REFERENCE_REQUIRED_TERMS.get(name, {})
        for reference in sorted(references_dir.glob("*.md")):
            key = f"references/{reference.name}"
            if not pinned.get(key):
                fail(f"{name}/{key} has no pinned phrases; add a REFERENCE_REQUIRED_TERMS entry")


def word_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split())


def check_budget(label: str, key: str, actual: int, budget: int, unit: str) -> None:
    if actual > budget:
        fail(f"{label} is {actual} {unit}, over its size budget of {budget}")
    if budget - actual >= SIZE_BUDGET_GRAIN:
        floor = -(-actual // SIZE_BUDGET_GRAIN) * SIZE_BUDGET_GRAIN
        fail(
            f"{label} is {actual} {unit} but its size budget is {budget}, "
            f"which is slack; lower {key} to {floor} in the same change"
        )


def validate_size_budget() -> None:
    """Growth is silent: a section added to a skill fails no pin, no mirror,
    and no link check, so the only thing that can report it is a ceiling.
    Mirrors are proven identical before this runs, so one tree is measured.
    A skill without an entry is unbudgeted, which the per-file check can
    never report, so coverage fails first."""
    check_budget(
        "CLAUDE.md",
        'SIZE_BUDGET_WORDS["CLAUDE.md"]',
        word_count(ROOT / "CLAUDE.md"),
        SIZE_BUDGET_WORDS["CLAUDE.md"],
        "words",
    )
    skills = skill_dirs(AGENT_SKILLS)
    for path in skills:
        name = path.name
        if name not in SIZE_BUDGET_WORDS:
            fail(f"{name}/SKILL.md has no size budget; add a SIZE_BUDGET_WORDS entry")
        check_budget(
            f"{name}/SKILL.md",
            f'SIZE_BUDGET_WORDS["{name}"]',
            word_count(path / "SKILL.md"),
            SIZE_BUDGET_WORDS[name],
            "words",
        )
    stale = sorted(set(SIZE_BUDGET_WORDS) - {"CLAUDE.md"} - {path.name for path in skills})
    if stale:
        fail(f"SIZE_BUDGET_WORDS budgets skills that do not exist: {', '.join(stale)}")
    descriptions = sum(
        len(parse_frontmatter(path / "SKILL.md").get("description", "")) for path in skills
    )
    check_budget(
        "the skill description listing",
        "DESCRIPTION_BUDGET_CHARS",
        descriptions,
        DESCRIPTION_BUDGET_CHARS,
        "chars",
    )


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
        # Vocabulary retired by the change-primitives rename: the structure
        # unit is a subsystem, the unit of change an increment, and a
        # property holding across subsystems an aspect.
        "cross-cutting concern",
        "cross-cutting constraint",
        "Component-kinds Δ",
        "Module-count Δ",
        "implementation slice",
        "admitted slice",
        "migration unit",
    )
    paths = [
        ROOT / "README.md",
        ROOT / "CLAUDE.md",
        ROOT / "ALCHEMY-PIPELINE-DESIGN.md",
        *DOCS.glob("*.md"),
        *DOCS.glob("*.svg"),
        *ROOT.glob("*.svg"),
        # Every markdown file in a skill directory, references included: a
        # retired term inside references/*.md is loaded on demand and drifts
        # just as silently as one in SKILL.md.
        *(md for path in skill_dirs(CLAUDE_SKILLS) for md in sorted(path.rglob("*.md"))),
        *(md for path in skill_dirs(AGENT_SKILLS) for md in sorted(path.rglob("*.md"))),
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8").casefold()
        for retired in retired_terms:
            if contains(text, retired.casefold()):
                fail(f"{path.relative_to(ROOT)} references retired term '{retired}'")


# Fenced report block inside a sample section, tolerant of CRLF checkouts.
REPORT_BLOCK_RE = re.compile(r"```(?:text)?\s*\r?\n(.*?)```", re.S)


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
    match = REPORT_BLOCK_RE.search(section)
    if not match:
        fail(f"{path.relative_to(ROOT)} section '{heading}' missing report block")
    report = match.group(1)
    for field in required_fields:
        if not re.search(rf"^{re.escape(field)}:\s*", report, re.M):
            fail(
                f"{path.relative_to(ROOT)} section '{heading}' "
                f"missing report field '{field}:'"
            )


def validate_absent_report_fields(
    path: Path, heading: str, forbidden_fields: tuple[str, ...]
) -> None:
    """A non-restructuring report must not carry the restructuring set."""
    section = markdown_section(path, heading)
    match = REPORT_BLOCK_RE.search(section)
    if not match:
        fail(f"{path.relative_to(ROOT)} section '{heading}' missing report block")
    report = match.group(1)
    for field in forbidden_fields:
        if re.search(rf"^{re.escape(field)}:\s*", report, re.M):
            fail(
                f"{path.relative_to(ROOT)} section '{heading}' "
                f"must omit restructuring field '{field}:'"
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
        MORPHOGENETIC_CORE_FIELDS,
    )
    validate_absent_report_fields(
        path,
        "## (c) Placement report",
        MORPHOGENETIC_RESTRUCTURING_FIELDS,
    )
    validate_report_fields(
        path,
        "## (d) Escalated topology report",
        MORPHOGENETIC_CORE_FIELDS + MORPHOGENETIC_RESTRUCTURING_FIELDS,
    )
    validate_report_fields(
        path,
        "## (e) Probationary acceptance report",
        MORPHOGENETIC_CORE_FIELDS + MORPHOGENETIC_RESTRUCTURING_FIELDS,
    )


def validate_morphogenetic_public_vocabulary() -> None:
    contracts = (
        ROOT / "README.md",
        DOCS / "morphogenetic_architecture.svg",
    )
    for path in contracts:
        text = path.read_text(encoding="utf-8")
        for decision in MORPHOGENETIC_DECISIONS:
            if not contains(text, decision):
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
        if not contains(skill_text, term):
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
        if not contains(rapid_text, term):
            fail(f"{rapid.relative_to(ROOT)} missing Rapid guard '{term}'")

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
            if not contains(text, term):
                fail(
                    f"{path.relative_to(ROOT)} missing morphogenetic mode "
                    f"contract '{term}'"
                )

    samples = DOCS / "sample-reports-verification.md"
    sample_text = samples.read_text(encoding="utf-8")
    for term in ("Analysis mode:       Rapid", "Analysis mode:       Rapid → Full"):
        if not contains(sample_text, term):
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
        if not contains(reference_text, term):
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
    if not contains(atlas_text, "## Operational Lens Index"):
        fail(f"{atlas.relative_to(ROOT)} missing '## Operational Lens Index'")
    for family in NATURAL_PATTERN_FAMILIES:
        if not contains(atlas_text, family):
            fail(f"{atlas.relative_to(ROOT)} missing lens family '{family}'")

    index_start = atlas_text.index("## Operational Lens Index")
    index_end = atlas_text.find("\n## ", index_start + 3)
    index_text = atlas_text[index_start:index_end]

    for term in (
        "## Candidate-Contribution Test",
        "Freeze this record before inspecting the validation surface",
        "supplies no second candidate",
        "lens-free baseline candidate",
        "observable condition",
        "`explanation only`",
        "reused as prospective validation",
        "| Natural architecture | Transferable mechanism | Software use | Required evidence | Reject when |",
    ):
        if not contains(atlas_text, term):
            fail(f"{atlas.relative_to(ROOT)} missing contribution guard '{term}'")

    for lens in NATURAL_PATTERN_OPERATIONAL_LENSES:
        if not contains(atlas_text, lens):
            fail(f"{atlas.relative_to(ROOT)} missing lens '{lens}'")
        if not contains(index_text, lens):
            fail(f"{atlas.relative_to(ROOT)} operational index missing '{lens}'")

    for lens in NATURAL_PATTERN_NON_OPERATIONAL:
        if not contains(atlas_text, lens):
            fail(f"{atlas.relative_to(ROOT)} missing non-operational lens '{lens}'")
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
    }
    for path, terms in contracts.items():
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if not contains(text, term):
                fail(
                    f"{path.relative_to(ROOT)} missing reversibility contract "
                    f"'{term}'"
                )


def validate_morphogenetic_probation() -> None:
    """Probation guards also live in evidence-fields.md, outside SKILL.md terms."""
    evidence = (
        AGENT_SKILLS
        / "morphogenetic-architecture"
        / "references"
        / "evidence-fields.md"
    )
    text = evidence.read_text(encoding="utf-8")
    for term in (
        "is measured contradiction, which always blocks probation",
        "Low confidence is never eligible for probation",
    ):
        if not contains(text, term):
            fail(
                f"{evidence.relative_to(ROOT)} missing probation guard "
                f"'{term}'"
            )


def validate_topology_report_checker() -> None:
    """The report checker proves emitted reports obey SKILL.md, not just that
    SKILL.md states the rule. Its self-test guards the rules themselves; the
    sample sweep guards the samples against the rules."""
    checker = ROOT / "scripts" / "check_topology_report.py"
    if not checker.is_file():
        fail(f"{checker.relative_to(ROOT)} is missing")

    samples = DOCS / "sample-reports-verification.md"
    for args, description in (
        (["--self-test"], "self-test"),
        (["--samples", str(samples)], "sample sweep"),
    ):
        try:
            completed = subprocess.run(
                [sys.executable, str(checker), *args],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except subprocess.TimeoutExpired:
            fail(f"{checker.relative_to(ROOT)} {description} timed out")
        if completed.returncode != 0:
            detail = (completed.stdout or completed.stderr).strip()
            fail(f"{checker.relative_to(ROOT)} {description} failed: {detail}")


def validate_report_blocks() -> None:
    """One report shape for one audience: the four plain-language blocks are
    defined once in the root instruction file, named by the router, and shown
    in a sample whose record still passes its own checker unchanged."""
    root = ROOT / "CLAUDE.md"
    text = root.read_text(encoding="utf-8")
    match = re.search(r"## 14\. Report(.*)", text, re.S)
    if not match:
        fail(f"{root.relative_to(ROOT)} missing '## 14. Report'")
    section = match.group(1)
    positions = [section.find(f"**{block}**") for block in REPORT_BLOCKS]
    if -1 in positions or positions != sorted(positions):
        fail(
            f"{root.relative_to(ROOT)} report blocks must appear in order: "
            + ", ".join(REPORT_BLOCKS)
        )
    if not contains(section, "(the record calls this QUARANTINE)"):
        fail(f"{root.relative_to(ROOT)} report rule must show the verdict callout")
    if not contains(section, "Fill the record first"):
        fail(f"{root.relative_to(ROOT)} report rule must put the record before the blocks")

    alchemy = AGENT_SKILLS / "alchemy" / "SKILL.md"
    router = alchemy.read_text(encoding="utf-8")
    for block in REPORT_BLOCKS:
        if not contains(router, block):
            fail(f"{alchemy.relative_to(ROOT)} output contract must name report block '{block}'")

    samples = DOCS / "sample-reports-verification.md"
    sample = markdown_section(samples, "## (f) Summary-led report")
    heads = re.findall(r"^\*\*([^*]+?)\.\*\*", sample, re.M)
    heads = [head for head in heads if head != "Scenario"]
    if heads != list(REPORT_BLOCKS):
        fail(f"{samples.relative_to(ROOT)} sample (f) blocks are {heads}, expected {list(REPORT_BLOCKS)}")
    if not re.search(r"\(the\s+record\s+calls\s+this\s+PLACE\)", sample):
        fail(f"{samples.relative_to(ROOT)} sample (f) never teaches its verdict word")
    record = REPORT_BLOCK_RE.search(sample)
    if record is None or not re.search(r"^Decision:\s+PLACE", record.group(1), re.M):
        fail(f"{samples.relative_to(ROOT)} sample (f) must end with the unchanged PLACE record")
    last_block = sample.find(f"**{REPORT_BLOCKS[-1]}.**")
    if record.start() < last_block:
        fail(f"{samples.relative_to(ROOT)} sample (f) record must follow the four blocks")
    unchecked = sample[last_block + len(f"**{REPORT_BLOCKS[-1]}.**") : record.start()].strip()
    if not unchecked:
        fail(f"{samples.relative_to(ROOT)} sample (f) 'What I did not check' is empty")


REFERENCE_LINK_RE = re.compile(r"\]\((references/[^)\s]+\.md)\)")


def validate_reference_links() -> None:
    """A reference file is progressive disclosure only if SKILL.md points at
    it; a link that resolves to nothing is a rule the agent can never read."""
    for skill in skill_dirs(AGENT_SKILLS):
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        linked = set(REFERENCE_LINK_RE.findall(text))
        present = {
            path.relative_to(skill).as_posix()
            for path in (skill / "references").glob("*.md")
        } if (skill / "references").is_dir() else set()
        for missing in sorted(linked - present):
            fail(f"{skill.relative_to(ROOT)}/SKILL.md links {missing}, which does not exist")
        for orphan in sorted(present - linked):
            fail(f"{skill.relative_to(ROOT)}/{orphan} is not linked from SKILL.md")


PRIMER_STAMP_RE = re.compile(r"<!-- skill-revision: ([0-9a-f]{12}) -->")
ASSET_SUFFIXES = {".svg", ".png"}
SCRATCH_IGNORE = (".git", "__pycache__", "node_modules", "*.pyc", "settings.local.json")


def read_raw(path: Path) -> tuple[str, bool]:
    """Return text with line endings normalized to LF, plus whether the file
    was CRLF, so a rewrite can put the same endings back."""
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    return (raw.replace("\r\n", "\n") if crlf else raw), crlf


def write_raw(path: Path, text: str, crlf: bool) -> None:
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))


def skill_revision(skill: Path) -> str:
    """Content hash of a skill's authored files, line endings normalized so a
    CRLF working copy and an LF checkout agree."""
    digest = hashlib.sha256()
    # Sort by the posix string, not the Path: Path ordering is case-insensitive
    # on Windows and case-sensitive elsewhere, so SKILL.md and references/
    # would hash in a different order per platform.
    for relative in sorted(mirror_source_files(skill), key=lambda path: path.as_posix()):
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update((skill / relative).read_bytes().replace(b"\r\n", b"\n"))
        digest.update(b"\0")
    return digest.hexdigest()[:12]


def validate_primer_revisions() -> None:
    """A primer is an explainer, not a contract mirror, so its content is not
    pinned. What is pinned is attention: each primer carries the revision of
    the skill it was last re-read against, and this fails until someone
    re-reads the primer and restamps it with --stamp-primers."""
    for skill in skill_dirs(AGENT_SKILLS):
        primer = DOCS / f"READ-{skill.name}.md"
        found = PRIMER_STAMP_RE.findall(primer.read_text(encoding="utf-8"))
        expected = skill_revision(skill)
        if len(found) != 1:
            fail(
                f"{primer.relative_to(ROOT)} must carry exactly one skill-revision "
                "stamp; re-read it against the skill, then run --stamp-primers"
            )
        if found[0] != expected:
            fail(
                f"{primer.relative_to(ROOT)} was last reviewed against skill-revision "
                f"{found[0]}, but {skill.name} is now {expected}; re-read the "
                "primer against the skill diff, then run --stamp-primers"
            )


def stamp_primers() -> int:
    """Rewrite every primer's stamp to the current skill revision. Run only
    after re-reading the primer against the skill change; the stamp records
    that the reading happened, it does not replace it."""
    changed = 0
    for skill in skill_dirs(AGENT_SKILLS):
        primer = DOCS / f"READ-{skill.name}.md"
        text, crlf = read_raw(primer)
        stamp = f"<!-- skill-revision: {skill_revision(skill)} -->"
        if PRIMER_STAMP_RE.search(text):
            new = PRIMER_STAMP_RE.sub(stamp, text, count=1)
        else:
            new = text.rstrip("\n") + "\n\n" + stamp + "\n"
        if new != text:
            write_raw(primer, new, crlf)
            changed += 1
            print(f"stamped {primer.relative_to(ROOT)}")
    print(f"{changed} primer(s) restamped")
    return 0


def validate_asset_references() -> None:
    """An image nobody links is dead weight in every install archive."""
    def in_scope(path: Path) -> bool:
        return ".git" not in path.parts and "node_modules" not in path.parts

    corpus = "\n".join(
        path.read_text(encoding="utf-8")
        for path in ROOT.rglob("*.md")
        if in_scope(path)
    )
    orphans = [
        path.relative_to(ROOT).as_posix()
        for path in sorted(ROOT.rglob("*"))
        if path.is_file()
        and path.suffix.lower() in ASSET_SUFFIXES
        and in_scope(path)
        and path.name not in corpus
    ]
    if orphans:
        fail(
            "unreferenced assets, delete them or link them from a markdown file: "
            + ", ".join(orphans)
        )


def mutation_test() -> int:
    """Prove the checks bite. In a scratch copy of the repository, break one
    thing per rule family and require the validator to fail on it. A check
    never observed failing is a hypothesis, not a safeguard."""
    scratch = Path(tempfile.mkdtemp(prefix="l-gevity-mutation-"))
    copy = scratch / "repo"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(*SCRATCH_IGNORE))
    validator = copy / "scripts" / "validate-skills.py"

    def run() -> tuple[int, str]:
        result = subprocess.run(
            [sys.executable, str(validator)],
            cwd=copy,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.returncode, (result.stdout + result.stderr).strip()

    def phrase_pattern(phrase: str) -> "re.Pattern[str]":
        # Tokens may be separated by wrapping or blockquote markers; mirror flatten().
        return re.compile(r"(?:\s|>)+".join(re.escape(token) for token in phrase.split()))

    class Case:
        def __init__(self, label: str, files: list[Path], expected: tuple[str, ...]):
            self.label, self.files, self.expected = label, files, expected
            self.snapshot = {path: path.read_bytes() for path in files if path.exists()}

        def restore(self) -> None:
            for path in self.files:
                if path in self.snapshot:
                    path.write_bytes(self.snapshot[path])
                elif path.exists():
                    path.unlink()

    cases: list[tuple[Case, "callable"]] = []

    for name, terms in SKILL_REQUIRED_TERMS.items():
        phrase = terms[0]
        pattern = phrase_pattern(phrase)
        files = [copy / tree / "skills" / name / "SKILL.md" for tree in (".agents", ".claude")]

        def remove_phrase(files=files, pattern=pattern, name=name):
            for path in files:
                text, crlf = read_raw(path)
                if not pattern.search(text):
                    raise RuntimeError(f"{name}: pinned phrase not found in {path.name}")
                write_raw(path, pattern.sub("", text), crlf)

        cases.append((Case(f"{name}: pinned phrase {phrase[:40]!r} removed", files, (name, phrase[:20])), remove_phrase))

    mirror = copy / ".claude" / "skills" / "alchemy" / "SKILL.md"

    def drift_mirror(path=mirror):
        path.write_bytes(path.read_bytes() + b"\ndrift\n")

    cases.append((Case("mirror: one byte differs between trees", [mirror], ("mirror mismatch",)), drift_mirror))

    primer = copy / ".documentation" / "READ-alchemy.md"

    def strip_stamp(path=primer):
        text, crlf = read_raw(path)
        write_raw(path, PRIMER_STAMP_RE.sub("", text), crlf)

    cases.append((Case("primer: skill-revision stamp removed", [primer], ("skill-revision",)), strip_stamp))

    def stale_stamp(path=primer):
        text, crlf = read_raw(path)
        write_raw(path, PRIMER_STAMP_RE.sub("<!-- skill-revision: 000000000000 -->", text), crlf)

    cases.append((Case("primer: stamp older than the skill", [primer], ("skill-revision",)), stale_stamp))

    orphan = copy / ".documentation" / "orphan-asset.svg"

    def add_orphan(path=orphan):
        path.write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")

    cases.append((Case("asset: unreferenced svg added", [orphan], ("orphan-asset.svg",)), add_orphan))

    package = copy / "package.json"

    def drop_cache_exclusion(path=package):
        text, crlf = read_raw(path)
        write_raw(path, text.replace('    "!**/__pycache__/",\n', ""), crlf)

    cases.append((Case("package: __pycache__ exclusion removed", [package], ("__pycache__",)), drop_cache_exclusion))

    legality = [copy / tree / "skills" / "morphogenetic-architecture" / "references" / "position-legality.md" for tree in (".agents", ".claude")]
    moved_term = next(iter(REFERENCE_REQUIRED_TERMS["morphogenetic-architecture"].values()))[0]

    def remove_reference_term(files=legality, pattern=phrase_pattern(moved_term)):
        for path in files:
            text, crlf = read_raw(path)
            if not pattern.search(text):
                raise RuntimeError(f"reference term not found in {path.name}")
            write_raw(path, pattern.sub("", text), crlf)

    cases.append((Case("reference: pinned phrase removed from position-legality.md", legality, ("position-legality.md",)), remove_reference_term))

    pruner = [copy / tree / "skills" / "functionality-complexity-tradeoff" / "SKILL.md" for tree in (".agents", ".claude")]

    def unlink_reference(files=pruner):
        for path in files:
            text, crlf = read_raw(path)
            link = "[references/common-patterns.md](references/common-patterns.md)"
            if link not in text:
                raise RuntimeError(f"reference link not found in {path}")
            write_raw(path, text.replace(link, "the common-patterns table"), crlf)

    cases.append((Case("reference: file left unlinked from SKILL.md", pruner, ("common-patterns.md",)), unlink_reference))

    # Both trees get the same text so the mirror check cannot fire first.
    retired = [copy / tree / "skills" / "push-out" / "SKILL.md" for tree in (".agents", ".claude")]

    def reintroduce_retired_term(files=retired):
        for path in files:
            text, crlf = read_raw(path)
            write_raw(path, text + "\nA cross-cutting concern belongs to one layer.\n", crlf)

    cases.append((Case("vocabulary: retired term reintroduced", retired, ("retired term",)), reintroduce_retired_term))

    # An appended pin is proven only by the case that removes it: the automatic
    # cases above remove each skill's first pin, never a later one.
    guidelines = [copy / tree / "skills" / "architecture-guidelines" / "SKILL.md" for tree in (".agents", ".claude")]
    aspect_rule = phrase_pattern("Aspects are extracted, not interleaved")

    def remove_aspect_rule(files=guidelines, pattern=aspect_rule):
        for path in files:
            text, crlf = read_raw(path)
            if not pattern.search(text):
                raise RuntimeError(f"aspect rule not found in {path}")
            write_raw(path, pattern.sub("", text), crlf)

    cases.append((Case("vocabulary: aspect extraction rule removed", guidelines, ("architecture-guidelines", "Aspects are extracted")), remove_aspect_rule))

    # Pin coverage is a property of the registry, so the mutation lives in the
    # copied validator: rename one skill's entry and that skill has no pins.
    validator_copy = [copy / "scripts" / "validate-skills.py"]

    def unpin_skill(files=validator_copy):
        for path in files:
            text, crlf = read_raw(path)
            needle = '    "push-out": ('
            if needle not in text:
                raise RuntimeError("push-out pin entry not found in the validator copy")
            write_raw(path, text.replace(needle, '    "push-out-unpinned": (', 1), crlf)

    cases.append((Case("coverage: skill left without pinned phrases", validator_copy, ("no pinned phrases",)), unpin_skill))

    # Renaming the key would make validate_skill() demand a file by the new
    # name first; deleting the whole entry leaves only the coverage failure.
    entry = re.compile(r'        "references/graph-analysis\.md": \(\n(?:.*\n)*?        \),\n')

    def unpin_reference(files=validator_copy, pattern=entry):
        for path in files:
            text, crlf = read_raw(path)
            if not pattern.search(text):
                raise RuntimeError("graph-analysis pin entry not found in the validator copy")
            write_raw(path, pattern.sub("", text, count=1), crlf)

    cases.append((Case("coverage: reference left without pinned phrases", validator_copy, ("graph-analysis.md has no pinned phrases",)), unpin_reference))

    # The expand step of the components -> subsystems key rename must keep the
    # alias readable until the contract step; dropping the JS fallback is the
    # premature contract this case guards against.
    js_skill = [copy / tree / "skills" / "architecture-as-code-javascript" / "SKILL.md" for tree in (".agents", ".claude")]

    def drop_alias_fallback(files=js_skill):
        for path in files:
            text, crlf = read_raw(path)
            needle = "m.default.subsystems ?? m.default.components ?? []"
            if needle not in text:
                raise RuntimeError(f"alias fallback not found in {path}")
            write_raw(path, text.replace(needle, "m.default.subsystems ?? []"), crlf)

    cases.append((Case("schema: components alias dropped before the contract step", js_skill, ("architecture-as-code-javascript",)), drop_alias_fallback))

    # The size ratchet has four failure paths, and each is proven on its own:
    # a file grows past its entry, a skill has no entry, an entry sits a grain
    # or more above its file, and an entry outlives its skill. Filler words
    # trip no pin, mirror, or retired-term check, so the ceiling is the only
    # check that can report the growth; both trees grow so the mirror check
    # cannot fire first.
    grown = [copy / tree / "skills" / "push-out" / "SKILL.md" for tree in (".agents", ".claude")]

    def grow_skill(files=grown):
        for path in files:
            text, crlf = read_raw(path)
            write_raw(path, text + "\n" + " ".join(["filler"] * (2 * SIZE_BUDGET_GRAIN)) + "\n", crlf)

    cases.append((Case("size: skill grown past its budget", grown, ("over its size budget",)), grow_skill))

    def unbudget_skill(files=validator_copy):
        for path in files:
            text, crlf = read_raw(path)
            needle = '    "push-out": 1300,\n'
            if needle not in text:
                raise RuntimeError("push-out size budget not found in the validator copy")
            write_raw(path, text.replace(needle, "", 1), crlf)

    cases.append((Case("size: skill left without a budget", validator_copy, ("no size budget",)), unbudget_skill))

    def slacken_budget(files=validator_copy):
        for path in files:
            text, crlf = read_raw(path)
            needle = '    "push-out": 1300,\n'
            if needle not in text:
                raise RuntimeError("push-out size budget not found in the validator copy")
            write_raw(path, text.replace(needle, '    "push-out": 1500,\n', 1), crlf)

    cases.append((Case("size: budget left slack after a trim", validator_copy, ("which is slack",)), slacken_budget))

    def budget_ghost_skill(files=validator_copy):
        for path in files:
            text, crlf = read_raw(path)
            needle = '    "push-out": 1300,\n'
            if needle not in text:
                raise RuntimeError("push-out size budget not found in the validator copy")
            write_raw(path, text.replace(needle, needle + '    "retired-skill": 1300,\n', 1), crlf)

    cases.append((Case("size: budget kept for a skill that no longer exists", validator_copy, ("do not exist",)), budget_ghost_skill))

    try:
        code, output = run()
        if code != 0:
            print(f"ERROR: the unmutated copy must validate first: {output.splitlines()[0] if output else code}")
            return 1
        failures = []
        for case, mutate in cases:
            mutate()
            try:
                code, output = run()
            finally:
                case.restore()
            first = output.splitlines()[0] if output else ""
            if code == 0:
                failures.append(f"{case.label}: validator still passed")
            elif not any(token in output for token in case.expected):
                failures.append(f"{case.label}: failed for another reason: {first}")
            else:
                print(f"caught  {case.label}")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    for line in failures:
        print(f"ERROR: {line}")
    if failures:
        return 1
    print(f"{len(cases)} deliberate violations, all caught")
    return 0


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
        if not contains(text, expected_link):
            fail(f"{primer.relative_to(ROOT)} missing canonical skill backlink")


def validate_readme_index() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for path in skill_dirs(CLAUDE_SKILLS):
        name = path.name
        skill_link = f"./.claude/skills/{name}/SKILL.md"
        primer_link = f"./.documentation/READ-{name}.md"
        if not contains(text, skill_link):
            fail(f"README.md missing skill link for {name}")
        if not contains(text, primer_link):
            fail(f"README.md missing primer link for {name}")


def validate_overview_skill_count() -> None:
    path = ROOT / "alchemy-overview.svg"
    text = path.read_text(encoding="utf-8")
    expected = f"{len(skill_dirs(CLAUDE_SKILLS))} SKILLS"
    if not contains(text, expected):
        fail(f"{path.relative_to(ROOT)} must report '{expected}'")


def validate_test_strategy_contract() -> None:
    skill = AGENT_SKILLS / "test-strategy"
    for relative in (
        Path("references") / "technique-selection.md",
        Path("references") / "portfolio-governance.md",
    ):
        if not (skill / relative).is_file():
            fail(f"{(skill / relative).relative_to(ROOT)} is required")

    contracts = {
        ROOT / "CLAUDE.md": (
            "test-strategy",
            "two-pass task-matched companion",
            "Obligation pass",
            "Portfolio pass",
            "pipeline execution triggers",
        ),
        AGENT_SKILLS / "alchemy" / "SKILL.md": (
            "`test-strategy`",
            "two-pass task-matched companion",
            "Obligation pass before A",
            "Portfolio pass after final A/L/C/E and before H",
            "earliest capable stage",
            "executed-evidence state",
        ),
        ROOT / "ALCHEMY-PIPELINE-DESIGN.md": (
            "`test-strategy`",
            "independently matched two-pass companion",
            "TS1",
            "TS2",
            "H owns placement",
        ),
    }
    for path, terms in contracts.items():
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if not contains(text, term):
                fail(
                    f"{path.relative_to(ROOT)} missing test-strategy "
                    f"ownership term '{term}'"
                )

    test_strategy_text = (skill / "SKILL.md").read_text(encoding="utf-8")
    if "environment | trigger | oracle" in test_strategy_text:
        fail(
            ".agents/skills/test-strategy/SKILL.md uses ambiguous 'trigger' "
            "for a test stimulus"
        )

    alchemy_text = (AGENT_SKILLS / "alchemy" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    ordered_terms = (
        "Readiness — READY or bounded reversible PARTLY-READY before Architecture",
        "Test strategy — Obligation pass before A",
        "Gate 2 — Smallest correct design",
        "Gate 5 — eslint.architecture.mjs in the SAME PR as the code",
        "Test strategy — Portfolio pass after final A/L/C/E and before H",
        "Gate 6 — Every error path mapped to earliest catchable stage",
    )
    positions = [alchemy_text.find(term) for term in ordered_terms]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        fail(
            ".agents/skills/alchemy/SKILL.md must preserve the Test Strategy "
            "Obligation → A/L/C/E → Portfolio → H checklist order"
        )


def validate_requirements_grounding_contract() -> None:
    skill = AGENT_SKILLS / "requirements-grounding"
    reference = skill / "references" / "quality-model.md"
    if not reference.is_file():
        fail(f"{reference.relative_to(ROOT)} is required")
    text = reference.read_text(encoding="utf-8")
    # Pin the 2023 revision of the product quality model, not the 2011 names.
    for term in (
        "ISO/IEC 25010:2023",
        "Interaction capability",
        "Flexibility",
        "Safety",
        "coverage finding",
        # 2011 -> 2023 renames, not additions; a project profile maps by these.
        "accessibility to inclusivity",
        "maturity to faultlessness",
    ):
        if not contains(text, term):
            fail(f"{reference.relative_to(ROOT)} missing quality-model term '{term}'")
    skill_text = (skill / "SKILL.md").read_text(encoding="utf-8")
    if not contains(skill_text, "references/quality-model.md"):
        fail(
            ".agents/skills/requirements-grounding/SKILL.md must link "
            "references/quality-model.md"
        )


def validate_evolutionary_database_design_contract() -> None:
    contracts = {
        ROOT / "CLAUDE.md": (
            "evolutionary-database-design",
            "two-pass",
            "Compatibility pass",
            "Transition pass",
            "Expand and contract never ship in one deployable",
            "gated on evidence, not a date",
        ),
        AGENT_SKILLS / "alchemy" / "SKILL.md": (
            "`evolutionary-database-design`",
            "two-pass task-matched companion",
            "Compatibility pass",
            "Transition pass",
            "grades reversibility from before A",
            "before the Test Strategy Portfolio pass and H",
            "Expand and contract never ship in one deployable",
        ),
        ROOT / "ALCHEMY-PIPELINE-DESIGN.md": (
            "`evolutionary-database-design`",
            "independently matched two-pass companion",
            "DS1",
            "DS2",
            "precedes the Test Strategy Portfolio pass and H",
        ),
    }
    for path, terms in contracts.items():
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if not contains(text, term):
                fail(
                    f"{path.relative_to(ROOT)} missing evolutionary-database-"
                    f"design ownership term '{term}'"
                )

    # The reversibility vocabulary this skill hands to L must be the vocabulary
    # L's reversibility table actually grades from; a drift on either side
    # silently breaks the handshake.
    morphogenetic = (
        AGENT_SKILLS / "morphogenetic-architecture" / "SKILL.md"
    ).read_text(encoding="utf-8")
    for term in ("reversible data change", "irreversible data migration"):
        if not contains(morphogenetic, term):
            fail(
                ".agents/skills/morphogenetic-architecture/SKILL.md no longer "
                f"grades from '{term}', which evolutionary-database-design emits"
            )

    alchemy_text = (AGENT_SKILLS / "alchemy" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    ordered_terms = (
        "Test strategy — Obligation pass before A",
        "Data shape — Compatibility pass before A",
        "Gate 2 — Smallest correct design",
        "Gate 5 — eslint.architecture.mjs in the SAME PR as the code",
        "Data shape — Transition pass after final A/L/C/E",
        "Test strategy — Portfolio pass after final A/L/C/E and before H",
        "Gate 6 — Every error path mapped to earliest catchable stage",
    )
    positions = [alchemy_text.find(term) for term in ordered_terms]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        fail(
            ".agents/skills/alchemy/SKILL.md must preserve the Evolutionary "
            "Database Design Compatibility -> A/L/C/E -> Transition -> Test "
            "Strategy Portfolio -> H checklist order"
        )


def validate_outcome_hypothesis_contract() -> None:
    skill_path = AGENT_SKILLS / "requirements-grounding" / "SKILL.md"
    skill_text = skill_path.read_text(encoding="utf-8")
    requirement_shape = re.search(
        r"## Requirement Shape.*?```text\s+(.*?)```",
        skill_text,
        re.S,
    )
    if not requirement_shape:
        fail(f"{skill_path.relative_to(ROOT)} missing requirement shape")
    if contains(requirement_shape.group(1), "Outcome hypothesis:"):
        fail(
            f"{skill_path.relative_to(ROOT)} must keep outcome hypotheses "
            "outside the requirement record"
        )

    contracts = {
        ROOT / "CLAUDE.md": (
            "problem outcome, requirement completion, and linked outcome",
            "working capability, not downstream",
            "authoritative obligation",
        ),
        AGENT_SKILLS / "alchemy" / "SKILL.md": (
            "linked outcome hypotheses as value evidence",
            "kept separate",
            "acceptance passed is reported as outcome success",
        ),
        ROOT / "ALCHEMY-PIPELINE-DESIGN.md": (
            "linked outcome hypotheses",
            "completion criteria or worth verdicts",
            "authoritative obligations",
        ),
        ROOT / "README.md": (
            "decision-relevant outcome hypotheses",
            "confusing impact with completion",
        ),
    }
    for path, terms in contracts.items():
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if not contains(text, term):
                fail(
                    f"{path.relative_to(ROOT)} missing outcome-hypothesis "
                    f"contract term '{term}'"
                )


def validate_outcome_evidence_lifecycle() -> None:
    trace_path = AGENT_SKILLS / "requirements-traceability" / "SKILL.md"
    trace_text = trace_path.read_text(encoding="utf-8")
    record = re.search(
        r"## Outcome Evidence States.*?```text\s+(.*?)```",
        trace_text,
        re.S,
    )
    if not record:
        fail(f"{trace_path.relative_to(ROOT)} missing outcome-evidence record")
    for field in (
        "Outcome evidence:",
        "Hypothesis version:",
        "Observation identity:",
        "Cohort and exposure:",
        "Measurement window:",
        "Threshold evaluation:",
        "Guardrail results:",
        "Comparison or attribution:",
        "Freshness:",
        "Evidence state:",
    ):
        if not contains(record.group(1), field):
            fail(
                f"{trace_path.relative_to(ROOT)} outcome-evidence record "
                f"missing field '{field}'"
            )
    if contains(record.group(1), "not-applicable"):
        fail(
            f"{trace_path.relative_to(ROOT)} must summarize authoritative "
            "not-applicable reasons without creating an outcome-evidence record"
        )

    worth_path = AGENT_SKILLS / "functionality-complexity-tradeoff" / "SKILL.md"
    worth_text = worth_path.read_text(encoding="utf-8")
    worth_output = re.search(
        r"## 9\. Output Contract.*?```(?:text)?\s+(.*?)```",
        worth_text,
        re.S,
    )
    if not worth_output or not contains(
        worth_output.group(1), "Outcome evidence:"
    ):
        fail(
            f"{worth_path.relative_to(ROOT)} worth output must cite "
            "outcome evidence"
        )

    contracts = {
        ROOT / "CLAUDE.md": (
            "Grounding owns meaning, Traceability owns measurement links",
            "route only the bounded",
            "do not restart the pipeline",
        ),
        AGENT_SKILLS / "alchemy" / "SKILL.md": (
            "new worth decision",
            "not a backward pipeline edge",
            "rerun only M in Retrospective mode",
        ),
        ROOT / "ALCHEMY-PIPELINE-DESIGN.md": (
            "outcome-evidence state",
            "re-enters only M in Retrospective",
            "Stale or inconclusive evidence cannot silently justify",
        ),
        ROOT / "README.md": (
            "versioned outcome measurements and freshness",
            "Revisiting value after release",
        ),
    }
    for path, terms in contracts.items():
        text = path.read_text(encoding="utf-8")
        for term in terms:
            if not contains(text, term):
                fail(
                    f"{path.relative_to(ROOT)} missing outcome-evidence "
                    f"lifecycle term '{term}'"
                )


def validate_generic_library() -> None:
    """No consumer name, path, or command may appear in the published library."""
    paths = [
        *ROOT.glob("*.md"),
        *DOCS.rglob("*.md"),
        *AGENT_SKILLS.rglob("*.md"),
        *CLAUDE_SKILLS.rglob("*.md"),
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for term in CONSUMER_FORBIDDEN:
            if contains(text, term):
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
        if not contains(text, f"`{state}`"):
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
        if not contains(text, term):
            fail(f"{path.relative_to(ROOT)} missing dispatch rule '{term}'")

    public_contracts = {
        ROOT / "README.md": ("do some alchemy", "Dispatch:", "Companions:"),
        ROOT / "CLAUDE.md": ("do some alchemy", "`SKIP` routine", "`FULL` only"),
        ROOT / "ALCHEMY-PIPELINE-DESIGN.md": (
            "Dispatch preflight",
            "do some alchemy",
            "companion skills",
        ),
    }
    for contract_path, terms in public_contracts.items():
        contract = contract_path.read_text(encoding="utf-8")
        for term in terms:
            if not contains(contract, term):
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
    }
    for path, blocking_term in contracts.items():
        text = path.read_text(encoding="utf-8")
        if not contains(text, handshake):
            fail(
                f"{path.relative_to(ROOT)} missing bounded topology handshake "
                f"'{handshake}'"
            )
        if not contains(text, blocking_term):
            fail(
                f"{path.relative_to(ROOT)} missing topology enforcement block "
                f"'{blocking_term}'"
            )
        if not contains(text, "once") and not contains(text, "one L re-entry"):
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
        # The four change primitives, pinned by their defining fragments: the
        # bare words already occur elsewhere in the section and prove nothing.
        "where change lands",
        "which dimension is touched",
        "what changes",
        "starting from that measured baseline",
        "runs in the iteration after the increment ships",
    )
    for term in required:
        if not contains(guidance, term):
            fail(f"{path.relative_to(ROOT)} missing Alchemy guidance term '{term}'")

    forbidden = ("Audits reverse", "PASS / DROP")
    for term in forbidden:
        if contains(guidance, term):
            fail(f"{path.relative_to(ROOT)} contains stale Alchemy guidance '{term}'")


def validate_design_and_release_contracts() -> None:
    design = ROOT / "ALCHEMY-PIPELINE-DESIGN.md"
    text = design.read_text(encoding="utf-8")
    required = (
        "Status: Implemented",
        "Blocking stage: None",
        "## Acceptance Criteria",
        "defines the four change primitives",
    )
    for term in required:
        if not contains(text, term):
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
        if not contains(text, term):
            fail(f"{path.relative_to(ROOT)} missing promotion term '{term}'")

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    files = package.get("files", [])
    if "CONTRIBUTING.md" not in files:
        fail("package.json must publish CONTRIBUTING.md")
    # A directory in the allow-list is walked without the root ignore rules,
    # so a compiled cache under scripts/ ships unless excluded here.
    if "!**/__pycache__/" not in files:
        fail("package.json files must exclude '!**/__pycache__/' or npm pack ships .pyc caches")


def validate_public_doc_drift() -> None:
    for rule, config in PUBLIC_DOC_FORBIDDEN.items():
        for path in config["files"]:
            text = path.read_text(encoding="utf-8")
            for pattern in config["patterns"]:
                if contains(text, pattern):
                    fail(
                        f"{path.relative_to(ROOT)} contains stale public-doc "
                        f"pattern for {rule}: {pattern!r}"
                    )


def installer_body(text: str) -> str:
    """The script with its per-agent profile and header comments removed."""
    return INSTALLER_HEADER_RE.sub("", INSTALLER_PROFILE_RE.sub("", text))


# Counting the target tree instead of the source is what made the installer
# report a consumer's 40 mirrored directories as 40 freshly installed skills.
INSTALLER_BODY_REQUIRED = {
    "sh": ("--force-local", "$SRC_SKILL_NAMES", "$SRC_FILES", "sha256_of",
           "previous_files", "KNOWN_MEMFILES", "KNOWN_SKILL_DIRS"),
    "ps1": ("$SrcSkillNames.Count", "$SrcFiles.Count", "Get-FileHash",
            "Get-PreviousFiles", "KnownMemFiles", "KnownSkillDirs"),
}
INSTALLER_BODY_FORBIDDEN = {
    "sh": ('find "$TARGET',),
    "ps1": ("Get-ChildItem $SkillsDest -Directory",),
}


def validate_installers() -> None:
    for suffix in ("sh", "ps1"):
        bodies = {}
        for agent, (memfile, primary) in INSTALLER_PROFILES.items():
            path = INSTALL / f"install-{agent}.{suffix}"
            if not path.is_file():
                fail(f"missing installer {path.relative_to(ROOT)}")
            text = path.read_text(encoding="utf-8")

            match = INSTALLER_PROFILE_RE.search(text)
            if match is None:
                fail(f"{path.relative_to(ROOT)} has no agent profile block")
            profile = match.group(1)
            for value in (agent, memfile, primary):
                if f"'{value}'" not in profile and f'"{value}"' not in profile:
                    fail(f"{path.relative_to(ROOT)} profile must declare '{value}'")
            for other_primary in {p for _, p in INSTALLER_PROFILES.values()}:
                if other_primary != primary and (
                    f"'{other_primary}'" in profile or f'"{other_primary}"' in profile
                ):
                    fail(
                        f"{path.relative_to(ROOT)} installs into "
                        f"'{other_primary}', which is not its agent's tree"
                    )
            bodies[agent] = installer_body(text)

        reference = bodies["claude"]
        for term in INSTALLER_BODY_REQUIRED[suffix]:
            if term not in reference:
                fail(f"install-*.{suffix} must keep '{term}'")
        for term in INSTALLER_BODY_FORBIDDEN[suffix]:
            if term in reference:
                fail(
                    f"install-*.{suffix} must not derive reported counts from "
                    f"the target tree: '{term}'"
                )
        for agent, body in bodies.items():
            if body != reference:
                fail(
                    f"install-{agent}.{suffix} differs from "
                    f"install-claude.{suffix} outside its agent profile block"
                )


def validate_ci_wiring() -> None:
    """A test nothing runs is documentation. Keep the workflow pointed at all."""
    for name in ("test-installers.sh", "test-installers.ps1"):
        tests = ROOT / "scripts" / name
        if not tests.is_file():
            fail(f"missing {tests.relative_to(ROOT)}")

    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    if not workflow.is_file():
        fail(f"missing {workflow.relative_to(ROOT)}")
    text = workflow.read_text(encoding="utf-8")
    for command in (
        "npm run validate",
        "npm run validate:mutation",
        "bash scripts/test-installers.sh",
        "./scripts/test-installers.ps1",
    ):
        if command not in text:
            fail(f"{workflow.relative_to(ROOT)} must run '{command}'")
    for platform in ("ubuntu-latest", "macos-latest", "windows-latest"):
        if platform not in text:
            fail(f"{workflow.relative_to(ROOT)} must cover {platform}")

    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    scripts = package.get("scripts", {})
    expected_scripts = {
        "validate:mutation": "python scripts/validate-skills.py --mutation-test",
        "test:installers": "bash scripts/test-installers.sh",
        "test:installers:ps": "pwsh -NoProfile -File scripts/test-installers.ps1",
    }
    for name, command in expected_scripts.items():
        if scripts.get(name) != command:
            fail(f"package.json must expose {name} as '{command}'")

    # Under a bare `* text=auto` a shell script checks out CRLF on Windows and
    # bash dies on the carriage return. Pin both script families explicitly.
    # Match whole lines: '.install/*.ps1 text eol=crlf' contains the general
    # pin as a substring, so a substring test would pass without it.
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
    for pin in ("*.sh text eol=lf", "*.ps1 text eol=crlf"):
        if pin not in [line.strip() for line in attributes]:
            fail(f".gitattributes must pin '{pin}' for every path")


def main() -> int:
    if "--stamp-primers" in sys.argv[1:]:
        return stamp_primers()
    if "--mutation-test" in sys.argv[1:]:
        return mutation_test()
    validate_matcher()
    validate_installers()
    validate_ci_wiring()
    validate_root(CLAUDE_SKILLS)
    validate_root(AGENT_SKILLS)
    validate_mirrors()
    validate_reference_links()
    validate_pin_coverage()
    validate_size_budget()
    validate_retired_skill_references()
    validate_morphogenetic_mode_selection()
    validate_morphogenetic_graph_analyzer()
    validate_morphogenetic_pattern_atlas()
    validate_morphogenetic_reversibility()
    validate_morphogenetic_probation()
    validate_sample_reports()
    validate_topology_report_checker()
    validate_report_blocks()
    validate_morphogenetic_public_vocabulary()
    validate_primers()
    validate_primer_revisions()
    validate_asset_references()
    validate_readme_index()
    validate_overview_skill_count()
    validate_test_strategy_contract()
    validate_requirements_grounding_contract()
    validate_evolutionary_database_design_contract()
    validate_outcome_hypothesis_contract()
    validate_outcome_evidence_lifecycle()
    validate_generic_library()
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
