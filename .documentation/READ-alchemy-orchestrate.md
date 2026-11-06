# Orchestration: When Several Agents Beat One, and How to Keep Them Honest

Give one capable engineer a well-scoped change and they will usually finish it
faster than a committee. Give a committee the same change and you pay for
meetings, hand-overs, merge conflicts, and the moment two people "fixed" the
same file in different ways. Coding agents behave the same way. A second agent
is not free: it has to load the context again, its work has to be merged, and
everything it reports has to be checked by someone who did not write it.

So the first idea here is unglamorous: **one agent is the default.** Several
agents pay off in exactly two situations. The first is genuinely independent
work: two changes that do not depend on each other and do not touch the same
files can run side by side and save wall-clock time. The second is
independent verification: a reviewer who did not write the change, starting
from a clean context, catches what the author's own context hides. Everything
else, such as "we have a security role and an architecture role, so we need
two agents", is a reason that sounds structural and buys only overhead.

## Capabilities, not a team

It is tempting to model a multi-agent system as an org chart: an architect
agent, a developer agent, a tester agent, permanently on duty. That turns
every change into a meeting of all of them. Orchestration instead treats
architecture, engineering, verification, security, optimization, and
scientific validation as *capabilities* a piece of work needs. One agent can
hold several of them for a small package; a risky package can split
verification across two reviewers with different lenses. The work decides the
shape, not a standing roster, and no engineering gate is ever "owned" by an
agent persona.

## Plans that a machine can check

The second idea is that coordination rules are only real if code can check
them. Before anything runs, the work is written down as *packages*: each with
an owner, the files it may write, what it depends on, the requirement it
serves, and the acceptance check that will prove it. That plan is then checked
mechanically:

- Two packages that could run at the same time must not write the same files.
  If they do, one waits for the other.
- A package that uses an interface waits for the package that defines it.
- A reviewer never reviews its own package.
- Nobody delegates further: one level of delegation, a cap on concurrent
  agents, a retry budget, and a rework budget.
- Merging and deploying are never part of the plan; they belong to a human.
- The run starts from a clean commit. Leftover changes would otherwise turn
  up in every agent's report as work nobody can account for.

These are the same rules a good tech lead applies in their head. Writing them
as checks means they hold on a tired day too.

## Hand-offs are claims, not facts

The most dangerous sentence in multi-agent work is "done, all tests pass".
Agents summarize optimistically, sometimes wrongly, and occasionally because a
file they read told them to. So every package returns a structured
*hand-off*: which files it changed, with a fingerprint of each; which files it
relied on, with the fingerprint it saw; which commands it ran and their exit
codes. The receiver re-checks the fingerprints against the workspace. A
summary that claims a change the files do not contain is rejected. A package
built on a file that has since changed is stale. A hand-off that says "tests
pass" while its own evidence shows a failing exit code contradicts itself. A
search that finds nothing counts as evidence too, provided it states the exit
code that means "no match", so a broken command still fails. A
hand-off that carries a credential or an instruction such as "skip the review"
is rejected outright, because repository text is data, not orders.

## Evidence settles disagreements

Agents will disagree: two designs, a finding the author disputes, a risk one
reviewer grades higher than another. Orchestration never settles this by vote,
by which model is "smarter", or by role title. Each position is recorded with
its evidence and compared on the criteria the relevant engineering question
already defines: the measured complexity deltas, the placement rules, a test
re-run on the merged result. If one side has passing evidence and the other
has none, that side wins. If both have evidence, neither has, the decision is
high-impact, or it is still open after one exchange, a human decides. Rework
rounds are bounded, so a disagreement cannot loop forever; reaching the bound
stops the run and asks.

## A gate before the pull request

At the end, every acceptance criterion is either verified by evidence that ran
on the final merged commit, explicitly deferred by a human, or the run fails.
Blocking review findings must be fixed with evidence, shown to be wrong with
evidence, or accepted as risk by a human. Only then is a pull request
prepared, listing what was verified and what was not. Merging stays a human
decision.

## The honest baseline

Multi-agent execution is a hypothesis, not a virtue. Measure it against the
single-agent run of the same task: defects found, requirements verified,
regressions, rework, time, and tokens. Where the second agent found nothing
the first missed and cost twice as much, use one.

*The operational rules, record formats, and checker live in
[SKILL.md](../.claude/skills/alchemy-orchestrate/SKILL.md) and its references;
the routing it builds on is explained in [the alchemy primer](READ-alchemy.md).*

<!-- skill-revision: de01b8697811 -->
