# Gate Lifecycle: The Check That Stopped Checking

A team writes a lint rule: nothing outside the auth package may import its
internals. The rule fires the day it is added, the team fixes the offenders, and
lint goes into the merge gate. Everyone moves on.

Months later somebody adds a second rule to the same configuration, for an
unrelated reason. It happens to use the same underlying lint rule, in a broader
block. The linter resolves that by keeping the last block's options, so the auth
restriction quietly stops existing. Nothing errors. Nothing warns. Lint stays
green on every pull request, and it would stay green forever, except that one
reviewer happens to read an import and asks why the gate allowed it.

The team had not been careless. The check was at the right stage, and it blocked.
It had simply stopped checking, and a gate that has stopped checking looks
exactly like a gate that found nothing.

This document explains gate lifecycle: the idea that a gate needs looking after
for as long as it exists, because the moment it is added is the moment people
stop paying attention to it.

## Green is not evidence until you have seen red

A passing check feels like information. It is only information if the check could
have failed. So the first question to ask of any gate is not "is it green?" but
"when did it last go red, and on what?"

That is why a gate needs a negative control: an input that is known to be bad and
must keep being rejected. It might be a fixture committed next to the rule, a
self-test that feeds the runner a fake failing report, or a copy of the tree with
a deliberate violation in it. What matters is that it runs through the gate as
actually configured. Testing the rule on its own would have passed in the story
above, because the rule itself was fine. The configuration around it was the
problem.

It also matters that the gate fails for the right reason. A crash is red too. In
fact a rule can be outright broken and nobody will know, because the block that
shadows it means it never runs. Check for the message you declared, not just for
a non-zero exit.

A gate that has never fired is not useless, and a long green history is not proof
that it works. It is unproven, which is a different and fixable thing.

## What a gate says and what it reaches

Every gate has two scopes. The declared scope is what it says it governs. The
effective scope is what it reaches once its configuration is resolved and its
results are added up. Those two drift apart in three ordinary ways.

A later block can replace an earlier rule's options, as in the story. A glob, an
ignore list, or a path filter can drop files, or a new directory can land outside
the pattern nobody revisited. And a summary can count skipped, retried, or flaky
results as passed. That last one is the easiest to miss, because the rule is
intact and the tests are real; the shrink is in the arithmetic at the end. How a
result is aggregated is part of what the gate checks.

The fix is to measure instead of read. Compare the declared rule with the resolved
configuration, require every rule to govern at least one file, and hand the
aggregator a report containing each awkward state to confirm that it fails.

## A baseline is debt

Adding a gate to a codebase that already breaks it usually means listing the
existing violations and blocking only new ones. That list is a reasonable tool. It
is also a debt register, and debt registers have one honest direction.

In one project the list of oversized modules was regenerated whenever the gate
went red. Thirty-four rewrites in twelve days. Each one was small, and none of
them was a decision, but together they turned the gate into a recording of
whatever happened to exist. It never failed, because anything that would have made
it fail was written into the list that defined failure.

A ratchet removes that option. Paying down debt needs no decision: entries shrink
or disappear on their own. Growing it does: the change that adds an entry has to
name it, or the gate refuses. A red run writes nothing. An entry that no longer
applies gets removed rather than left in place, since it is headroom for the next
regression.

## Failed and could-not-evaluate are different answers

One team's deploy gate started erroring on an identity problem. It had not
compared anything; it could not sign in. Someone removed the gate on the reasoning
that it was not doing anything useful, and three hours later it was back.

A gate that could not evaluate has said nothing about the code. That is not a pass,
and it is not a violation, and treating it as either leads somewhere bad. Reading
it as a violation sends people hunting a defect that does not exist. Reading it as
noise gets the gate deleted. So it is a third state: indeterminate. The gate keeps
blocking, the pipeline labels the result so nobody mistakes what happened, and the
work is to repair the evaluation. If it can never work where it is, because it
needs state from the target environment, it moves to a stage where that state
exists. Being unable to evaluate is never a reason to retire it.

## Every suspension needs an end something else enforces

Sometimes loosening a gate on purpose is right. A hook has become slow, nobody is
sure it earns its cost, and a short trial would settle it. That is a fine decision
with three parts: a criterion you can measure, an owner, and an expiry.

In one project a hook dropped a test suite as a one-week trial. The hook's own text
said so. Two months later it still said so; nobody had measured the criterion and
nobody had decided anything. Nothing went wrong on the day it expired, which is the
trouble. An expiry that lives in a comment is a hope.

So a suspension is written as data that a dated step reads and fails on, or better,
as a condition that lapses on its own so the gate returns with nobody acting. When
a trial expires undecided, the default is to put the gate back. Renewing it means a
new trial that cites what the last window measured. Moving the date is not a
decision.

Retirement is the same discipline at the other end. A gate leaves because what it
checks is gone, because a proven gate catches the same thing earlier, or because
the obligation behind it lapsed. It does not leave because it is annoying.

## The tooling is part of the gate

The script that regenerates a baseline, or the one that adds up a suite's results,
sits outside the gate's attention by default, and that is where these failures
hide. It is code the verdict depends on, so it gets a negative control of its own,
and it must not be able to loosen the gate as a side effect of running.

---

*Gate lifecycle starts where [shift-left](READ-defect-shift-left.md) stops:
shift-left decides where a check runs and makes it block, and this keeps that
check honest afterward.
[Reliable pipelines](READ-ci-cd-reliability-architecture.md) decide how a gate
blocks and what it records, and [test strategy](READ-test-strategy.md) owns what
it asserts. The full operational reference — triggers, proof forms, the seven
decisions, and the output contract — lives in
[SKILL.md](../.claude/skills/gate-lifecycle/SKILL.md); the reconcile algorithm and
the dated expiry step live in
[ratchet.md](../.claude/skills/gate-lifecycle/references/ratchet.md).*

<!-- skill-revision: 65d67352ce78 -->
