# Documentation Sweep

Use this procedure when the mode selector starts in **Sweep**: no artifact is
named, and the task is to find every redundant document in a tree rather than
to place one. Sweep discovers candidates and ranks them; the litmus test in
SKILL.md §4 still decides each one.

## Scope Contract

Sweep may inspect:

- every prose artifact the subject tree tracks, and every documentation surface
  the project profile names — repository files, wiki spaces, exported pages;
- the four authorities, as the carriers a redundancy claim is proved against;
- a generated report's freshness, by comparing the committed copy with a fresh
  regeneration.

Sweep must not delete anything, edit an authority, or classify an artifact
`DUPLICATE` without naming the carrier of every claim in it. Sweep proposes;
the owner disposes.

The sweep's own result is a finding, not an artifact. Emit it in the response
or as an issue. A committed `documentation-audit.md` is the anti-pattern this
skill exists to remove.

## Procedure

1. **Enumerate from version control, not the filesystem.** List tracked
   artifacts, so untracked scratch is out of scope and a deleted document is
   not resurrected from a stale checkout. Record the count; it is the
   denominator every later claim is measured against.
2. **Scan the signatures.** Read each candidate's path, title, headings,
   and opening paragraph only. Assign a provisional classification from the
   signature table below, or `Unclassified`. The scan is cheap and covers the
   whole denominator.
3. **Decompose the candidates.** Open only the candidates whose provisional
   decision removes or folds content, and the `Unclassified` remainder, in rank
   order. Split the artifact into its distinct claims and route each claim
   through §4 independently. A document whose claims route to two authorities is
   two artifacts; report the split rather than a single verdict.
4. **Apply the evidence bar.** For each claim, name the artifact that already
   carries it: file and symbol, commit, issue ID, or requirement ID. A claim
   with a named carrier is **redundant** — fold and delete. A claim with no
   carrier is **unowned**, not redundant: its action is to move it into the
   authority that owns the question. Deleting an unowned claim destroys the only
   copy of a fact, which is the one failure this skill must never cause.
5. **Rank.** Order by evidence strength and reversibility, cheapest and safest
   first: fully carried duplicates, then hand-maintained reports that a command
   can regenerate, then partially carried artifacts, then exceptions whose guard
   has expired. Unowned content is last, because it is a move, not a prune.
6. **Emit and state the remainder.** Report one row per artifact reached, then
   state how many of the enumerated candidates were never opened. A sweep
   that stops early is a partial result and says so; a sweep that claims every
   redundant document while leaving candidates unopened is the failure this step
   prevents.

## Signature Table

Signatures are provisional. Each one is a reason to open the artifact,
never a verdict on its own.

| Signature | Provisional classification | Confirm when opened by |
| --- | --- | --- |
| ADR file, decision log, or decision record directory | DUPLICATE | Finding the issue that argued it |
| Hand-edited changelog, status page, roadmap, or progress board | GENERATED-REPORT | Finding a command that could compile it from history, tracker, and register |
| Architecture or design note describing a current module | DUPLICATE | Finding the module, contract, or enforcement rule it narrates |
| Triage, investigation, incident, or postmortem file | DUPLICATE | Finding the issue it belongs to, or creating one |
| Setup, contribution, or conventions guide | EXCEPTION (onboarding/tooling) | Checking whether the tooling now carries the instruction itself |
| Dated migration note, superseded model, or import record | EXCEPTION (frozen record) | Checking the history for edits after its date |
| Prose whose subject module churned while the prose did not | DUPLICATE | Comparing the claim against current behavior |
| Artifact named by an external obligation | EXCEPTION (compliance deliverable) | Naming the obligation and the audience |

## What Belongs in a Check

Parts of this sweep are mechanical and drift back the moment the sweep ends.
Per the root instruction file, encode them rather than repeating the sweep:
a committed report that differs from a fresh regeneration, a frozen record
edited after its date, a documentation path a rule forbids, and a link to a
requirement or issue identifier that no longer resolves. Hand the recurring
finding to `continuous-improvement`. What stays a judgment is whether two
artifacts carry the same claim; that is what the sweep is for.

## Stop Conditions

Stop and report rather than continuing when:

- the tracker or requirement register is unreachable, so no carrier can be
  named and every verdict would be `Defer`;
- the subject tree has no version-control history, so redundancy cannot be
  separated from a frozen record;
- more than one candidate in three lands on `Defer`, which means the sweep is
  guessing and the project profile is missing the paths, tracker, and
  identifier formats it needs.
