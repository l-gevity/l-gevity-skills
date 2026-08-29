# Traceability: Where Is It, and How Do We Know It Works?

A new tech lead joins and asks two innocent questions about a contractual
requirement: *"Where is report approval implemented, and what proves it
works?"* The team's answers, reconstructed over two days: the
implementation is "mostly in the workflow module, probably," the proof is
"the tests pass" (which tests? for which criteria?), and along the way
someone discovers that one acceptance criterion was never implemented at
all — it fell out during a refactor eight months ago, and nothing noticed.

Traceability is the discipline that makes those two questions answerable
in minutes instead of days: maintained, checkable links between what was
promised, where it's built, and what evidence proves it. This document
explains the concept — and the two or three distinctions that separate
real traceability from its decorative imitation.

## The ladder of proof

The core of the concept is refusing to let "done" be one blurry state.
For each acceptance criterion of each requirement, the honest question is
*which rung of this ladder are we on?*

| State | What it means | What it does **not** mean |
| ----- | ------------- | ------------------------- |
| **Unmapped** | No known implementation or verification | — |
| **Implemented** | A stable anchor points at code or a test *definition* | That it passes, or ever ran |
| **Verified** | An **executed, passing** result exists for this revision | That it still passes after later changes |
| **Blocked** | A named missing dependency or decision, with an owner | That it can be quietly skipped |
| **Not applicable** | An explicit, scoped, owner-approved rationale | A general waiver |

The rung that gets faked most is the middle one. **Implementation is not
verification.** A test *definition* proves someone wrote a check; only an
*executed run* of that check, passing, against an identified revision,
proves the behavior. Related: claimed evidence must be **reproducible** —
"it worked in staging" without the revision, environment, and run identity
attached is an anecdote. Evidence you can't trace to *what ran, where,
when, with what result* isn't evidence; it's a memory.

And verification is perishable: "verified" attaches to a revision, not to
the requirement forever. The refactor that silently dropped a criterion is
what happens when a past green run is treated as a permanent state.

## Both directions, or it's half a system

Traceability that only points one way answers only half the audit.

**Forward** (requirement → code → evidence) answers: *is everything we
promised implemented and proven?* This is the direction people usually
mean, and it catches the dropped criterion.

**Reverse** (change → requirement) asks, of every non-trivial change:
*what authorized this?* The answer is either a requirement ID or an
explicit named rationale — platform work, operations, technical debt, a
spike. What reverse tracing catches is different and just as important:
scope creep entering as unlabeled diffs, speculative features nobody asked
for, and the quiet accumulation of behavior that no requirement covers —
which is precisely the code that, years later, nobody dares delete because
nobody knows why it exists. The rationale tags aren't bureaucracy; they're
the difference between "unjustified" and "justified as maintenance,
deliberately."

One rule keeps the links themselves trustworthy: **a stale reference is a
defect, not noise.** An anchor pointing at a renamed requirement, a
removed criterion, an ID that no longer resolves — each is a broken link
in the chain of proof, and tolerated broken links teach everyone to stop
trusting the links at all. Validity is mechanically checkable (does every
referenced ID exist? does every claimed test result have a matching test?),
which makes it exactly the kind of thing a build gate should enforce.

## Anchors live where the work lives

The tempting implementation of all this is The Spreadsheet — a central
matrix mapping every requirement to every file and test. It's also the
implementation that guarantees decay: the matrix lives far from the code,
gets updated on a different rhythm by different people, and within months
is a well-organized fiction.

The durable alternative: put small, stable **anchors in the artifacts
themselves**, in the place a maintainer would look first. The requirement
ID in the contract's metadata and the contract test. The criterion tag on
the behavior test that checks it. The requirement IDs in the decision
record's context. The runbook check that carries revision and run identity
in its output. Registries and matrices can then be *generated* from the
anchors — derived views, rebuildable at any time — instead of being a
second, hand-maintained source of truth that drifts from the first.
(Restraint applies here too: an ID next to a well-named test is an anchor;
three paragraphs of duplicated requirement prose in a source comment is a
fork of the requirement, and forks drift.)

## Links carry proof, never meaning

A boundary that keeps the whole system honest: trace links are
**evidence**, not **authority**. The canonical requirements own what
should be true; the links only record where it's built and what proves it.
Two corruptions follow from crossing that line. A trace entry can't
*authorize* behavior — "the code does X and we linked it to requirement Y"
doesn't make X required; if X is right, the requirement gets updated
through its own process, and if the code and requirement disagree, that's
a finding, not a link. And an evidence record can't *edit* a claim to fit
the data — if the measured result misses the declared threshold, the state
is "missed," not a quietly relaxed threshold. Traceability is the
bookkeeping of promises; bookkeeping that adjusts the promise to match
the ledger isn't bookkeeping.

The same discipline separates **completion from impact**. Executed tests
can prove the capability works as specified. Whether it produced the
hoped-for downstream outcome — faster closes, fewer support tickets — is a
different claim, provable only by real measurement of real use, tracked
separately with its own freshness ("supported *as of* that cohort and
window", going stale when the world changes). Deployment, adoption, even
glowing anecdotes are not outcome evidence, and a traceability system
that lets "we shipped it and people log in" stand in for "it worked" has
laundered the distinction the whole system exists to keep.

## The habit

The concept compresses into the two questions from the opening, asked
continuously rather than during audits: for any requirement, *where is it,
and what executed evidence proves it — at which revision?* For any change,
*what authorized this?* When both are answerable from anchors and
generated views in minutes, you have traceability. When answering takes a
two-day archaeology project, you have a codebase and a requirements
document waving at each other from a distance — and the gap between them
is where the dropped criterion, the scope creep, and the "verified"
feature nobody can prove are all quietly living.

---

*Traceability is the follow-through stage of a requirements discipline:
[grounding](READ-requirements-grounding.md) owns what requirements mean,
[topology](READ-requirements-topology.md) owns their IDs and lineage,
[implementation readiness](READ-implementation-readiness.md) defines the
evidence obligations that traceability then tracks, and
[worth evaluation](READ-functionality-complexity-tradeoff.md) consumes
outcome evidence to decide what stays. The full operational reference —
evidence states, anchor placement, gap taxonomy, and build-gate checks —
lives in
[SKILL.md](../.claude/skills/requirements-traceability/SKILL.md).*
