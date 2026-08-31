# The Standup That Cannot Lie

Every morning, in thousands of teams, the same three sentences are produced:
what I did yesterday, what I'll do today, what's blocking me. And in most of
those teams the ritual has quietly decayed into performance — a summary of
intent rather than a report of state, assembled from memory, delivered with
confidence, and correct only by coincidence.

The decay is not laziness. It's that a human recalling their own week is a
narrator, not an instrument. Memory smooths. "Nearly done" survives three
consecutive standups. A blocker mentioned on Monday is repeated on Thursday
because nobody rechecked whether it was still real. The report drifts away
from the system it describes, and the further it drifts the more comfortable
it becomes — because the uncomfortable facts are the ones that get rounded off.

An agent generating the same report has a property no human narrator has: it
can be *forbidden from knowing anything it did not just verify*. That single
constraint changes what a standup is. It stops being a summary of intent and
becomes a measurement of state.

## Verified-only is the whole idea

The rule is blunt: every line traces to a command output, a file, or an API
response observed in this run. Not "I believe CI is green" — the run was
listed. Not "the migration is nearly done" — the commits since the window
opened say what exists. Not "we're still waiting on the vendor" — the issue
was reopened and read today.

This costs something, and the cost is the point. A verified-only report is
shorter, less flattering, and occasionally embarrassing. It will say *not
run: coverage gate unavailable* where a narrator would have said *coverage is
looking fine*. The first is useful precisely because it admits a hole; the
second is a hole with a smooth surface painted over it.

The corollary matters as much: a check that could not run is reported as not
run, with the reason. Silence about a failed check is indistinguishable from
a passing check, and a reader who cannot tell those apart has been misled
without anyone lying.

## News is delta, not state

The second rule kills most of the length. Anything identical to yesterday is,
by definition, not news.

Standing facts — the architecture, the team, the long-running epic, the same
four open dependency-bot PRs — are context, and context repeated daily trains
readers to skim. Once they skim, the one line that *did* change goes past
unread, and the report has achieved the opposite of its purpose. A standup
that reliably contains only differences earns a kind of attention that a
standup padded with reassurance never gets.

This is also why carrying a finding forward is prohibited rather than
discouraged. An external blocker copied from last week's report is an
assertion about *today* backed by evidence from *last week*. Recheck it or
drop it.

## Six questions, in a deliberate order

The structure isn't arbitrary; each section constrains the next.

| Section | The question | Why here |
| ------- | ------------ | -------- |
| **Done** | What actually landed in the last two working days? | Git is the only honest record of what exists |
| **Blockers** | What is genuinely stopping work right now? | Failing gates, pending decisions, external dependencies — verified today |
| **Progress & risks** | How many days remain, and are we on track? | Only answerable once *done* and *blocked* are known |
| **Architectural debt** | What structural weight is accumulating? | The slow variable that never shows up in a sprint burndown |
| **Requirements drift** | Does the built system still match what was agreed? | The gate answers this; opinion does not |
| **Proposal for today** | What is the highest-risk next move? | A conclusion drawn from the five sections above, not a wish list |

Read top to bottom, it walks from hard evidence toward judgment, and every
judgment sits downstream of the facts that constrain it. A deadline assessment
made before checking blockers and drift is a guess wearing a schedule.

## The two slow variables

Most status reporting tracks fast variables — tickets closed, PRs merged —
because they move visibly each day. The two that actually decide whether a
deadline holds move slowly enough to be invisible daily and decisive
quarterly.

**Architectural debt** is structural, not featural: the shared component
nobody adopted, the infrastructure cost curve bending the wrong way, the model
with no screen, the data-model gap everyone routes around. Reporting the three
heaviest items with a single trend word — increasing, stable, decreasing —
does something a backlog cannot: it makes the *direction* visible. Nobody
argues about a specific issue's priority when the honest sentence is "this is
the third week of increasing."

**Requirements drift** is the distance between what was agreed and what was
built. It is measurable only when a gate measures it; where no gate exists,
the correct report is *drift is unmeasured*, which is information — it says
the team is flying without that instrument, rather than pretending the
instrument reads zero.

## Method generic, parameters local

The one structural trap in automating a standup: project facts leaking into
the method. Deadlines, the gate command, the path to the coverage artifact —
these are local and change per project. The six questions, the verified-only
rule, and the delta rule are not.

Keeping the parameters in a small profile beside the repository, and the
method in the skill, means the method can be updated for every project at once
and a project can set its own deadlines without forking anything. When a
parameter is absent, the report says so — *no deadlines configured* — instead
of inventing a plausible one. An invented deadline is worse than no deadline,
because someone will plan against it.

## What it's for

A standup built this way is not a ritual and not a status broadcast. It is a
daily instrument reading, and its value comes entirely from being trusted:
when it says a gate is red, the gate is red; when it says a section is empty,
the section is empty; when it says a check did not run, nobody assumes it
passed.

Teams over-invest in the ceremony and under-invest in that trust. Reverse the
ratio. A report nobody has to interpret is worth ten that sound good.

---

*Related concepts: [requirements-traceability](READ-requirements-traceability.md)
owns the drift evidence this report reads;
[system-optimization](READ-system-optimization.md) turns a recurring blocker
into a constraint analysis; and
[functionality-complexity-tradeoff](READ-functionality-complexity-tradeoff.md)
decides what to do about debt this report only counts. The full operational
reference — parameters, section rules, and the output contract — lives in
[SKILL.md](../.claude/skills/standup/SKILL.md).*
