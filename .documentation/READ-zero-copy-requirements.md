# Zero-Copy Requirements: Where Does the Truth Live?

A new engineer joins and asks why the export runs at 02:00. Four answers are
available. The cron expression says 02:00. The architecture document says
03:00, because it was written before a daylight-saving incident. The wiki page
says "overnight". And an issue from last spring explains that 02:00 was chosen
because the upstream feed lands at 01:40 — which is the only answer that tells
them anything they couldn't have read off the schedule itself.

Three of those four artifacts were written by people trying to be helpful. Two
of them are now wrong. Nobody was careless: the architecture document was
accurate the day it was written, and the wiki page was accurate for about a
year. What went wrong is structural. The same fact was recorded in four places,
and only one of them — the cron expression — is *forced* to stay true, because
the system reads it.

This document explains zero-copy requirements: the idea that every fact should
live in exactly one artifact, and that the number of documents a team maintains
is a much better predictor of how much of its documentation is lying than how
carefully the team writes.

## A second copy is not a backup

The intuition worth dismantling first is that writing something down twice is
belt-and-braces — redundancy, safety, helpfulness. In prose about a running
system, a second copy is not a backup. It is a second authority, and the moment
the system changes, exactly one of them gets updated.

Which one? The one the system reads. The cron expression changes because
changing it is how you change the schedule. The architecture document doesn't
change, because nothing breaks when it doesn't. So duplication doesn't produce
two true statements that reinforce each other; it produces one true statement
and a growing set of confidently-worded false ones, with no marker saying
which is which. The new engineer has no way to tell the live fact from the
fossil. That's the actual cost: not the wasted writing, but the reader who
can't distinguish.

Hence the rule the concept is named for: **no artifact may exist whose content
is fully reconstructable from another artifact already in the system.** If you
can derive it from something that already exists, deriving it is the only safe
way to have it.

## Four things, and only four

If duplication is the disease, the cure has to be an answer to "then where does
each fact go?" — because facts don't stop existing when you delete the page
that held them. There are exactly four homes, and each one answers a different
question:

| The authority | Answers | Because |
| --- | --- | --- |
| **Code and its tests** | *What does the system do?* | It is the system. It cannot be out of date with itself. |
| **Version-control history** | *What changed, when, and why that change?* | Each commit is welded to a diff and immutable afterwards. |
| **The issue tracker** | *What's undecided, what was decided, what's planned?* | It is the only one of the four that can hold a question. |
| **The requirement register** | *What should be built, and when is it done?* | It is the only one that can describe something not yet built. |

The division isn't arbitrary — it follows from what each medium is physically
capable of. Code can't record a question, because a question has no runtime
behavior. Git can't record a standing rule, because a commit describes one
moment. Issues can't reliably describe current behavior, because nothing forces
an issue to change when the code does. And a requirement register can describe
something that doesn't exist yet, which is precisely what code cannot do.

Two of the four are *immutable* — a commit and its diff never change — and two
are *live*. That matters when deciding where something belongs: an approval
that must still mean something in three years does not belong in a comment
anyone can edit.

## Decisions are the interesting case

Most teams place three of these correctly by instinct. Nobody argues that code
belongs in code. The one that goes wrong is decisions.

A decision starts as a question — *should the export run at 02:00 or 03:00?* —
and questions live in the issue tracker, because that's the only authority that
can hold one. The temptation, once it's settled, is to promote the answer into
a document: an ADR file, a decision log, a page in the wiki. It feels like
respect for the decision. What it actually does is separate the answer from the
question, so that the issue is closed with no reasoning and the document has
reasoning with no trace of what it was arguing against.

The alternative is to let the decision close where it was raised: as the
closing note on the issue that asked. The argument, the rejected options, and
the answer stay in one thread, in order, with the people who made it. Anything
downstream that needs the decision cites the issue ID rather than restating
the conclusion — which, conveniently, is also a link back to the reasoning.

There's one carve-out. A decision that must survive as *evidence* — a
compliance sign-off, a legal basis, a regulator-facing approval — should not
live in a comment that anybody can edit afterwards. That belongs in a merged
commit or change request, where it's welded to a diff and a timestamp. The test
isn't how important the decision feels; it's whether someone will later need
to prove it wasn't changed.

## Reports are compiled, never written

"Every fact in one place" seems to forbid the status page, the coverage
summary, the quarterly compliance pack. It doesn't. It forbids *writing* them.

A report that is assembled from the four authorities by a command is not a
second authority — it's a view, and it's as true as its inputs at the moment it
ran. The same document typed by hand is a second authority that was true once.
The distinction is not what the document contains; it's whether the document
can drift. Generate it, mark it read-only, and let the build fail when the
committed copy differs from a fresh run.

This gives a sharp diagnostic. If a generated report contains a fact that
exists nowhere else, that fact is a bug: someone hand-patched the output rather
than fixing the source. Move it into whichever authority owns the question, and
regenerate.

## Three documents that are allowed to exist

A rule with no exceptions gets ignored the first time reality doesn't fit, so
it's worth being explicit that exactly three kinds of standalone document
survive the rule.

**Onboarding and tooling documents** explain how to work *on* the system rather
than what the system does — which command to run, which conventions apply,
where things live. They're describing the team's practice, not the system's
behavior, so there's no authority they duplicate. They earn their keep until
the tooling says it itself, at which point delete them.

**Compliance deliverables for an external audience** exist because someone
outside the team requires a document in a particular shape. The authorities are
the source; the deliverable is the format. Generate it if you possibly can —
a hand-written one that gets re-typed every cycle is the anti-pattern, not the
exception.

**Frozen historical records** describe a completed migration, a superseded
model, a one-time import whose provenance still gets cited. They're safe
precisely because they're closed: dated, never backfilled, never the authority
for anything live. The moment someone edits one to keep it current, it has
stopped being a record and become an unowned second authority.

Notice what all three have in common: none of them is a live description of
current behavior. That's the actual boundary.

## Asking the question

The concept compresses to one question, asked before creating any document:
*can someone reconstruct this from what already exists?*

If yes, either delete it or generate it. If no, it answers exactly one of the
four questions above, and belongs in that authority. If it seems to answer two,
it's two artifacts wearing one filename, and splitting it is the whole job.

Asked across a whole documentation tree at once, the question needs one guard.
“Reconstructable” has to be shown, not assumed: point at the code, the commit,
the issue, or the requirement that already carries the claim. Where nothing
does, the claim is not redundant — it is *unowned*, and the tree you were about
to prune holds the only copy of it. Those two look identical from the outside,
and telling them apart is what stops a documentation cleanup from becoming a
data loss. Redundant content gets deleted; unowned content gets moved.

The signals that the question is overdue are easy to spot: two documents
describing the same subsystem, a decision document whose issue was closed
silently, a status page someone updates by hand every Friday, an architecture
diagram that gets "refreshed" before each audit. Each is a fact that has been
copied, and each copy is a promise to keep two things in sync that nobody can
keep.

---

*Zero-copy requirements is the placement rule that sits underneath the
documentation advice in [push-out](READ-push-out.md) — which prunes prose that
an executable source already covers — and ahead of
[requirements-traceability](READ-requirements-traceability.md), which anchors
evidence once a location exists. The full operational reference — the authority
table, the generated-report rules, the three exceptions, and the litmus test —
lives in [SKILL.md](../.claude/skills/zero-copy-requirements/SKILL.md).*

<!-- skill-revision: 01cfa6aadab5 -->
