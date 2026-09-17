# Dependency Lifecycle: The Code You Own But Did Not Write

A scanner is switched on and reports 47 vulnerabilities. The team spends a
week. Forty of them turn out to be in code paths the application never reaches
— a template engine bundled with a test helper, an XML parser in a library used
only for CSV. Four are real and upgrade cleanly. Three have no fix available,
so they get added to an ignore file with a comment saying "revisit", and the
number goes green.

Eleven months later the service has an outage. Not from any of the 47. The
runtime it runs on reached end of life, the platform stopped issuing patches
for it, and the base image was rebuilt from a tag that no longer existed. That
one was never in the report, because no scanner was looking for it: nothing had
changed, and that was precisely the problem.

This document explains dependency lifecycle: the idea that the decisions about
a dependency start rather than finish when you adopt it, and that most of them
are triggered by time rather than by anyone touching the code.

## Adoption is a transfer of maintenance, not of responsibility

Choosing a library is usually treated as the hard part, and it does get real
scrutiny — is it maintained, is it popular, does it fit. What that scrutiny
implies is that the decision is now over.

It isn't, because the decision was made about a snapshot. The library that was
maintained in March has a sole maintainer who stopped answering issues in
August. The license that was permissive was relicensed after an acquisition.
The version that was current is four majors behind. None of these involve
anybody on the team writing a line of code, and none of them will show up in a
pull request, because a pull request is the record of a change and nothing here
changed. The manifest is the same file it was a year ago. The world around it
is not.

That is the shape of the problem: **a dependency ages whether or not you touch
it**, and a process that only reviews what changes cannot see it. It needs a
trigger of its own — an advisory, drift, abandonment, an expiry date, or the
quiet moment when the last import of it gets deleted.

## A finding is not a decision

The scanner in the story did its job. It reported presence. What it could not
do was tell the team what to do about it, and the gap between those two things
is where most dependency work actually goes wrong.

Presence is cheap to establish: the package resolves, the version matches the
advisory. Exposure is the useful question, and it is a different one — does any
call path in *this* system actually reach the affected behavior? A parser
vulnerability in a library you only use to format dates is present and
unreached. The same vulnerability in the thing that handles inbound requests is
an emergency. The advisory cannot tell them apart, because the advisory does
not know your code.

Making that distinction explicit has a second benefit, which shows up later.
"We accepted it because it is unreachable" is a decision with evidence behind
it. "We ignored it because there was no fix" is a decision with a comment
behind it. Only the first one can be re-examined by someone who wasn't there,
and only the first one can be falsified when someone adds the call path that
makes it reachable.

## The honest version of "we will live with it"

Three of the 47 got an ignore entry. That is often the right answer — not every
finding is worth a migration, and a compensating control elsewhere may already
close the path. What made it go wrong was not the acceptance; it was that the
acceptance had no end.

An accepted risk that carries an owner, the grade it rests on, and a date or
condition that reopens it is a decision. The same acceptance with none of those
is an undecided finding wearing a decision's clothes: it looks settled, it
silences the alert, and nobody will ever look at it again, because nothing is
scheduled to make them. Suppression files accumulate exactly this way, one
reasonable entry at a time, until they are a list of things the team no longer
knows anything about.

The same logic covers the other responses. Pinning to an old version is fine if
something names the increment that unpins it. Carrying a local patch is fine if
it is submitted upstream and deleted when the release lands. Forking an
abandoned library is fine if the fork becomes real first-party code with an
owner and tests — and is abandonment with extra steps if it doesn't. Every
answer other than "upgrade" is an exception, and an exception without an end
condition is a permanent one that nobody chose.

## "Routine" describes the contract, not the number

Version numbers invite a shortcut: patch and minor are safe, major is not. It
is a useful convention and a poor rule, because it describes what the publisher
intended rather than what your code depends on.

The questions that decide whether a bump is routine are about contracts. Did a
symbol this system imports change meaning? Did a default change, even inside
the same version range? Did the floor rise on a runtime, an engine, or a
transitive package something else also constrains? Did the license change? Did
anything move in a shape that gets persisted or sent over a wire, where old and
new versions of your own code have to coexist during a rollout?

If none of those is true, the bump is a non-event and deserves none of your
attention. If any of them is true, the version number is irrelevant to the size
of the change, and treating it as routine is how a "minor" bump takes down a
service on a Friday. The distinction is worth making explicitly, because
automation is very good at producing bumps and very bad at knowing which kind
it just produced.

## Deferral compounds

The last piece is cadence, and it is the one that quietly decides how expensive
everything above will be.

Upgrading continuously means each upgrade is a small, independent decision
against a small diff, taken while someone still remembers why the code uses
that library. Deferring means the next upgrade spans several majors at once,
arrives with a deadline attached because it is now a security fix, and lands on
whoever is on call. The work was not avoided; it was accumulated, and interest
was charged in the form of having to do it all at once, urgently, later.

That is why the cheap, boring, scheduled version of this work is worth
protecting. It is not diligence for its own sake. It is the difference between
a decision you make and an emergency you receive.

## Asking the question

The question a lifecycle view adds is not "are we vulnerable?" — a scanner will
answer that, and the answer is usually a number nobody can act on. It is:
**does every dependency we own have a current decision, and does every
exception have an end?**

A dependency with no current decision is not safe; it is unexamined. An
acceptance with no expiry is not a risk taken; it is a risk forgotten. And a
date on a vendor's end-of-life page is not a surprise, however much it feels
like one on the morning it arrives.

---

*Dependency lifecycle picks up where [bring-down](READ-bring-down.md) leaves
off — bring-down decides whether to depend on something external at all, this
decides what to do about it for the years afterwards — and hands the placement
of its scans to [defect-shift-left](READ-defect-shift-left.md) and the gating of
their results to
[ci-cd-reliability-architecture](READ-ci-cd-reliability-architecture.md). The
full operational reference — ownership tiers, the five triggers, reachability
grading, the response ladder, and the bump classification — lives in
[SKILL.md](../.claude/skills/dependency-lifecycle/SKILL.md).*

<!-- skill-revision: f411539d3e13 -->
