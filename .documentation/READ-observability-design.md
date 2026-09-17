# Observability Design: What You Cannot See, You Cannot Size

Confirmation emails stopped going out on a Tuesday. Nobody noticed until the
following week, when a customer asked why they had never received a receipt for
an order that had, in fact, gone through perfectly.

Every dashboard had been green the whole time. The worker process was up and
answering its health check. CPU was normal. The queue depth was zero — which
was the actual evidence of the failure, and which read on the dashboard as the
best possible number. Messages were being consumed and, because of a
configuration change in a downstream client, discarded. The system was
processing nothing, efficiently, and reporting excellent health while it did.

This document explains observability design: the idea that being able to detect
a failure is something you decide and build, not something a system has by
default — and that the signals you already have tend to describe the process's
opinion of itself rather than the user's experience.

## Absence of alerts is not evidence of health

The most expensive assumption in operations is that quiet means fine. It feels
like evidence. It is the same evidence you would have if the alerting pipeline
were broken, if the failure were in a code path nobody instrumented, or if the
thing that went wrong were the kind of thing nobody thought to measure.

The sharper way to say it: **a failure with no signal has no rate**. Not a low
rate — an unmeasured one. Every statement about how often it happens, how many
users it touched, or how long it lasted is unavailable, including after the
incident, when those are exactly the questions being asked. The email outage
lasted eleven days as far as anyone can prove, and the honest answer to "how
many customers?" was never recovered, because nothing was counting.

This is why detection is a design problem rather than a monitoring one. The
decision about what a failure looks like from outside has to be made by someone
who knows what the change can do wrong — which means while the change is being
built, not while it is being diagnosed.

## Health is a claim a process makes about itself

The green dashboard was not lying, exactly. It was answering a narrower
question than anyone was reading it as. "Is the worker running?" is a genuine
question with a genuine answer, and it is nearly useless as a proxy for "are
receipts arriving?"

Signals gathered from inside a process describe the process. Signals gathered
at the boundary where somebody consumes the output describe the outcome. When
those two diverge — and the whole family of silent failures lives in that gap —
the internal one stays green, because from the inside everything really is
fine. The worker consumed its messages. It did exactly what it was told.

The correction is to measure where the value is delivered: receipts sent per
order placed, not messages consumed per second. That number cannot be green
while the outcome is failing, because it is the outcome. It is also harder to
produce, which is why teams tend to end up with the easy signals instead and
then wonder why they only ever learn about outages from customers.

## Three jobs, easily confused

It helps to notice that signals do three unrelated jobs, and that conflating
them is why observability bills grow while outages still get discovered by
email.

**Detecting** answers "is something wrong right now?" It has to be cheap enough
to run always, for everything, which in practice means aggregates: rates,
ratios, latencies, an availability probe.

**Diagnosing** answers "which part, and why?" It is allowed to be expensive,
sampled, or switched on after the fact, because by the time it is needed
something has already told you where to look. Traces and logs live here.

**Verifying** answers "did the change do what it claimed?" — the question a
deploy is supposed to answer and usually doesn't, because "no new complaints
yet" is standing in for it.

Most instrumentation debt is a detection job being done by a diagnosis tool.
Alerting on the text of a log line is the classic case: it works, and it binds
paging to a message string that any refactor can reword without anyone
realising they have just turned off an alarm.

## The alert nobody can act on

The other half of the problem is the opposite of silence. A team that has been
burned adds alerts, and alerts are never removed, so the set only grows. After
a few years it contains a few things worth waking someone for and a great many
things that fire, get acknowledged, and change nothing.

That mix is worse than either extreme, because attention is a shared budget. An
alert that has cried wolf forty times has trained its recipients, and it trains
them about the *other* alerts too — the reflex to acknowledge and move on does
not check which one just fired. This is how a well-monitored system misses an
outage: not because the signal was absent, but because it arrived in a stream
that everyone had learned to dismiss.

Hence the test worth applying before any alert exists: who receives it, what do
they do in the first five minutes, what degrades for someone if they do
nothing, and where did the threshold come from? A threshold traced to an
objective defends something specific. A threshold someone eyeballed on a
Thursday is a guess with a pager attached, and it will be the first one ignored.

Anything that fails those questions is still useful — as a panel on a
dashboard, consulted when something else has already said to look. It is just
not a reason to wake a human being.

## Signals decay in one direction

Left alone, a signal set drifts one way: more alerts, more dashboards, more
retained telemetry, all of it defensible individually. Nothing removes anything,
because deleting an alert feels like accepting risk while adding one feels like
diligence.

So the pruning has to be explicit and routine, and the criteria are
unsentimental. An alert that fires and never leads to action is noise and
should be deleted or re-derived from the objective it was supposed to defend.
An alert that has never fired has never been proved capable of firing — an
untested alarm is not coverage. Two alerts that always fire together are one
failure billed twice. A dashboard nobody opens and a log field nobody queries
are costs with no reader.

None of that is achievable as a periodic cleanup project, which is why the
useful version attaches a review interval and a date of last useful fire to
each signal, so that pruning is a small recurring decision rather than a heroic
one.

## Asking the question

The question is not "do we have monitoring?" — the team in the story had a wall
of it. It is: **for each way this change can fail, what will tell us, who will
it tell, and what will they do?**

Ask it while building, and it costs a metric and a threshold. Ask it during the
incident, and you are designing instrumentation at the worst possible moment,
under the worst possible pressure, for a failure that has already had eleven
days to spread.

---

*Observability design consumes the residual risk left by
[test-strategy](READ-test-strategy.md) — the failure modes the test portfolio
deliberately does not catch — and hands every signal it creates back to
[defect-shift-left](READ-defect-shift-left.md), which asks whether that failure
could have been caught earlier and more cheaply instead. The full operational
reference — the three duties, signal-type selection, the alert admission test,
and the prune rule — lives in
[SKILL.md](../.claude/skills/observability-design/SKILL.md).*

<!-- skill-revision: d7f6b426b84e -->
