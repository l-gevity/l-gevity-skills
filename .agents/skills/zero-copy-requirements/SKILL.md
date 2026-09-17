---
name: zero-copy-requirements
description: >-
    Decides where a fact belongs so that no artifact exists whose content is
    fully reconstructable from another artifact already in the system. Use when
    adding, reviewing, or pruning documentation, when deciding whether a
    decision belongs in a document, an issue, a commit, or a requirement, when
    an architecture note, decision log, status page, or triage write-up is
    proposed, or when auditing a documentation tree for duplicated authority.
    Do not use to establish requirement meaning, normalize a requirement graph,
    or classify evidence state; hand those to requirements-grounding,
    requirements-topology, and requirements-traceability.
---

# Zero-Copy Requirements

Keep every fact in exactly one artifact. A second copy is not redundancy; it is
a second authority that will disagree with the first.

> **Purpose**: No artifact may exist whose content is fully reconstructable
> from another artifact already in the system.

> **Core Directives**
>
> 1. **One question, one authority.** Each fact has exactly one owning
>    artifact. Every other mention is a reference to it, never a restatement.
> 2. **Four authorities carry the system.** Behavior, history, decisions, and
>    specification. An artifact that is none of them is a generated report, a
>    bounded exception, or waste.
> 3. **Decisions close where they were raised.** Record a decision as a comment
>    or closing note on the tracker item that asked the question. Never write a
>    separate decision document for it.
> 4. **Sign-off is immutable.** Compliance-grade approval lands in a merged
>    commit or change request, not in a mutable comment or an editable page.
> 5. **Reports are compiled, never authored.** Anything assembled from the
>    authorities is regenerated from them and read-only.
> 6. **Reference by identifier.** A dependent artifact names the ID of what it
>    depends on; it does not copy that artifact's text.
> 7. **Frozen records are closed, not maintained.** A historical or migration
>    record is dated and never backfilled; the moment it is updated to stay
>    current it has become an unowned second authority.

## Boundary

`zero-copy-requirements` is a task-matched Alchemy companion, not a
qualification stage, gate, or acronym letter. It runs in a single pass, at any
point where an artifact's home is in question.

This skill decides *where* a fact lives. It does not decide what the fact means,
whether the work is worth doing, or whether evidence proves it.

- `requirements-grounding` owns requirement meaning, source authority, and
  evidence quality.
- `requirements-topology` owns identifiers, lineage, and graph semantics.
- `requirements-traceability` owns anchors and evidence state once a location
  exists; this skill decides the location it anchors into.
- `push-out` owns the general directive that executable sources beat prose
  duplicates, and the ladder that moves operational work outward; this skill
  names which artifact owns which question in the first place.

Apply a project profile for concrete paths, tracker names, schemas, identifier
formats, and validation commands. Keep none of those here.

## 1. The Four Authorities

| # | Authority | Sole owner of | Must not absorb |
| --- | --- | --- | --- |
| 1 | **Code and its tests** | What the system does now, and the conditions under which it is correct | Why a change was made, what is still undecided, what is merely planned |
| 2 | **Version-control history** | What changed, when, by whom, and — via the commit message — the immediate why of that specific change | Standing policy, open questions, the specification of unbuilt work |
| 3 | **Issue tracker** | Every open question; every decision, product or architectural; every planned-not-yet-built item | Current behavior, which the code already states; acceptance conditions, which the register already states |
| 4 | **Requirement / specification register** | What can or should be built, and the conditions that make it complete | The decision's rationale, which lives on the issue it cites; evidence state, which traceability owns |

Wiring between them:

- A requirement cites the issue or issues that decided it, and — when blocked or
  unbuilt — the issue that will unblock it. It restates neither.
- An issue's closing note is the decision record. A decision that outgrows a
  comment becomes a requirement plus the issue that decided it, not a document.
- A commit message carries the immediate why of its own change and references
  the issue or requirement that authorized it. It does not restate the standing
  rule.
- Code and tests carry requirement identifiers as anchors, not requirement
  prose.

## 2. The Generated-Report Layer

Anything compiled from the authorities is a report, not an authority.

- Regenerate it from a command; never hand-author or hand-patch it.
- Mark it read-only, and fail the build when a committed report differs from a
  fresh regeneration.
- A report may be an external-audience deliverable — a coverage matrix, a status
  board, a compliance pack assembled from requirements and issues — but its
  content still originates entirely in the authorities.
- If a report carries a fact that exists nowhere else, that fact is the defect:
  move it into the authority that owns the question, then regenerate.

## 3. Bounded Exceptions

Exactly three kinds of artifact may exist outside the authorities and the report
layer.

| Exception | Admission test | Guard |
| --- | --- | --- |
| **Onboarding / tooling meta-documentation** | Explains how to work *on* the system — setup, conventions, which command to run, which skill to route through — rather than what the system does or what was decided | Delete it when the tooling carries the instruction itself; see the documentation-pruning pattern in `push-out` |
| **Compliance-mandated external-audience deliverable** | An external obligation names the artifact and its audience, and the authorities are not a deliverable form for that audience | Restructure as a generated report as soon as its content is reconstructable; hand-authoring it each cycle is the anti-pattern |
| **Frozen historical or migration record** | Closed and dated; describes a completed transition, a superseded model, or a one-time import whose provenance is still cited | Never backfilled, never updated to stay current, never the authority for anything live |

An artifact that fits no exception and duplicates an authority is waste. Fold its
content into the owning authority and delete it.

## 4. Litmus Test

Run in order for any existing or proposed document. Stop at the first match.

```text
1. Is its content fully reconstructable from artifacts that already exist?
   → Yes: delete it, or replace it with a generated report.
2. Does it answer "what does the system do?"
   → Code and its tests.
3. Does it answer "what changed, when, and why that change?"
   → Version-control history.
4. Does it answer "what is undecided, what was decided, or what is planned
   but unbuilt?"
   → An issue; a decision closes as that issue's comment or closing note,
     unless it must later be proved unaltered — then it closes in a merged
     commit or change request (Directive 4).
5. Does it answer "what should be built, and when is it done?"
   → The requirement register, citing the deciding issue.
6. Is it compiled from 2-5?
   → A generated report, regenerated by command and read-only.
7. Does it pass exactly one exception admission test in section 3?
   → Keep it, and record the guard that ends or freezes it.
8. Otherwise
   → Waste. Fold and delete.
```

A document that needs two answers is two artifacts. Split it before keeping it.

## 5. Anti-Patterns

| Anti-pattern | Correction |
| --- | --- |
| A decision document or ADR file recording a decision already argued on an issue | Close the decision on that issue; cite the issue ID where the decision is needed |
| A decision log appended to a requirement | The requirement cites the deciding issue; it is not the decision record |
| Hand-maintained changelog, status page, or progress board | Generate it from history, the tracker, and the register |
| Architecture or design note narrating what the code already does | Point at the module, contract, or enforcement rule |
| Triage, investigation, or incident write-up committed as a repository file | It is an issue and its comments |
| Requirement text restating a dependency's acceptance conditions | Reference the criterion identifier |
| Compliance deliverable hand-authored every cycle | Compile it from the authorities; the deliverable is a report |
| Compliance sign-off recorded in an editable comment or page | Land it in a merged commit or change request |
| A frozen record edited to stay current | Either freeze it or promote its content into an authority; it cannot be both |
| "Documentation debt" resolved by writing more prose | Locate the owning authority first; prose that duplicates it increases the debt |

## 6. Output Contract

```text
Subject:              <document, tree, or proposed artifact>
Classification:       AUTHORITY | GENERATED-REPORT | EXCEPTION | DUPLICATE
Owning authority:     <code+tests | history | issues | requirements | none>
Reconstructable from: <artifacts that already carry the content, or none>
Decision:             Keep | Fold into <authority> | Generate | Freeze | Delete
Exception:            <onboarding/tooling | compliance deliverable | frozen record | none>
Guard:                <condition that ends or freezes the exception, or none>
Next action:          <one concrete action>
```

For an audit of several artifacts, emit one row per artifact:

```text
| Artifact | Classification | Owning authority | Reconstructable from | Decision | Guard |
| -------- | -------------- | ---------------- | -------------------- | -------- | ----- |
```

## 7. See Also

- **`push-out`** - executable sources beat prose duplicates; documentation-pruning pattern.
- **`requirements-traceability`** - anchors and evidence state once the location is decided.
- **`requirements-grounding`** - requirement meaning, source authority, and evidence.
- **`requirements-topology`** - stable identifiers, lineage, and generated views.
- **`continuous-improvement`** - promoting a recurring duplication finding into a check.
