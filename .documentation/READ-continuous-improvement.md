# Fix the Rule, Not the Instance

The review comment appears for the third time this quarter: *"we don't call
the database from the UI layer — please route this through the service."*
Three different authors, same mistake, same patient correction. Each time,
the code gets fixed and everyone moves on.

Here's the uncomfortable reading: the third occurrence is not the third
author's failure. It's the system's. A mistake that recurs is no longer a
mistake — it's evidence that the rule which should have prevented it is
missing, ambiguous, contradicted, or unenforced. Correcting the *instance*
for the third time while leaving the *rule* untouched guarantees a fourth.

This document explains continuous improvement as engineers should practice
it: not a suggestion box or a quarterly retro ritual, but a specific
discipline for converting each recurring failure into a permanent change to
the system that produced it.

![Continuous Improvement](continuous_improvement.svg)

## Single-loop and double-loop learning

When something goes wrong there are two possible responses, and they operate
at different depths:

- **Single-loop:** fix the thing. The import is corrected, the outage is
  resolved, the typo is patched. Necessary, and entirely forgettable — the
  system that produced the error is unchanged, so the error's probability
  is unchanged.
- **Double-loop:** fix the thing, *then fix whatever allowed the thing*.
  The import is corrected — and a lint rule now fails the build for any
  UI-to-database import, forever, for every author, including ones not yet
  hired.

Most teams live almost entirely in the first loop, because the first loop
feels productive and the second requires stopping to ask an awkward
question: *why was this possible?* But only the second loop compounds. A
team that closes one rule-gap per week is, a year later, operating a system
with fifty fewer ways to fail — and that advantage persists through
turnover, growth, and busy quarters, because it lives in the system rather
than in anyone's memory.

## Diagnose before you legislate

The reflex after a failure is to write a new rule. Resist it until you know
*which kind* of gap you're looking at, because each kind has a different
correct fix:

| The gap | What happened | The fix |
| ------- | ------------- | ------- |
| **Missing rule** | Nothing ever said not to do this | Add the smallest rule that would have prevented it |
| **Ambiguous rule** | A rule exists but honestly permits both readings | Tighten the wording; add the concrete example that decides the case |
| **Conflicting rules** | Two rules disagree; the author obeyed one of them | Resolve the conflict; give one rule clear ownership |
| **Ignored rule** | The rule is clear, and nobody saw it | Improve its placement or enforcement — a rule's visibility is part of the rule |
| **Misunderstood system** | The rule was fine; the platform or framework behaves differently than believed | Document the actual behavior where the mistake was made |

Two of these deserve emphasis. An *ignored* rule is not a compliance
problem — a rule buried on page nine of a wiki nobody opens has failed as a
rule, and the remedy is moving it to where the mistake happens, not blaming
the person who never saw it. And a *misunderstood system* means the real
root cause is upstream of anyone's conduct entirely.

That's the blameless posture, and it's not politeness — it's accuracy. The
person who made the mistake is the least interesting variable, because they
were merely the first to walk through a door that was standing open. The
door is the defect. Five-whys the symptom down until you reach a cause you
can change *in the system*, and stop there.

## Automation before prose

Once you know what the rule should say, there's a hierarchy for where it
should live — and written guidance is the *last* resort, not the first:

1. **Make the mistake impossible**: a type, a schema, a template that
   doesn't contain the trap.
2. **Make it fail automatically**: a lint rule, a test, a build gate, a
   pre-commit hook.
3. **Make it visible at the point of use**: a scaffold, a checklist item in
   the PR template, an editor hint.
4. **Write it down** — only when none of the above is feasible, and then as
   the smallest useful sentence, with a note on *why* automation wasn't
   possible.

The reasoning is mechanical. Prose rules must be found, read, remembered,
and voluntarily obeyed by every person forever; they decay with staff
turnover and document rot, and their enforcement costs a human's attention
on every occasion. An encoded rule is found by nobody and obeyed by
everybody: it runs on every commit at zero marginal cost and never has a
tired day. "We agreed to stop doing X" is a wish. "The build fails when X
happens" is a fact about the world.

## Rules are a codebase — treat them like one

A team that takes double-loop learning seriously accumulates rules — lint
configs, working agreements, templates, guides. Left untended, this
accumulation becomes its own failure mode: the guideline document nobody
can find anything in, the contradictory conventions from different eras,
the checklist with forty items of which five matter. Three maintenance
disciplines keep the rulebook from rotting:

- **Density over volume.** Before adding a rule, try to *replace, merge, or
  tighten* an existing one. Every rule taxes every reader; a rulebook that
  only ever grows will eventually be skimmed rather than followed, at which
  point all of its rules have failed together.
- **One owner per rule.** Every rule lives in exactly one authoritative
  place; everything else links to it. The moment two documents both state
  the rule, they begin to drift, and the reader who finds the stale copy is
  worse off than the reader who found nothing.
- **Prune with evidence.** Delete rules that are obsolete, contradicted, or
  now enforced by automation (a prose rule duplicating a lint rule is pure
  overhead). But prune *proven* dead weight only — a rule that seems
  pointless may be the residue of an expensive lesson, so check its origin
  before removing it.

## Close the loop, or it didn't happen

An improvement isn't finished when the new rule is written. It's finished
when two more things are true.

First, **verification**: there is some demonstration that the original
mistake is now caught or prevented — the lint rule fires on the old bad
code, the test fails without the fix, the template no longer contains the
trap. A rule that has never been observed to catch anything is a hypothesis,
not a safeguard, and "this can never happen again" is only true when an
enforced gate makes it true.

Second, **notification**: the people affected hear one plain sentence —
*"such-and-such now fails the build, because of the incident last week"* —
so the change enters the team's shared model instead of ambushing the next
person as a mysterious new failure.

## The habit

The discipline compresses into one question, asked at a specific moment:
whenever you correct something — a bug, a review comment, a production
incident, your own repeated stumble — ask *"what would have to change so
this class of mistake can't recur?"* Then push the answer as far down the
hierarchy as it will go: impossible beats automatic, automatic beats
visible, visible beats written. One instance is an accident. The same
instance twice is a rule waiting to be written — and the second occurrence
is the system telling you exactly where.

---

*Related concepts: [shift-left](READ-defect-shift-left.md) supplies the
placement discipline — an encoded rule belongs at the earliest pipeline
stage that can enforce it; and
[push-out](READ-push-out.md) is the same instinct applied to operational
work — moving it out of memory into durable systems. The full operational
reference for this concept — triggers, root-cause analysis, and the update
protocol — lives in
[SKILL.md](../.claude/skills/continuous-improvement/SKILL.md).*
