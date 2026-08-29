# Flow: Why Everyone Is Busy and Nothing Ships

A team of eight, all working flat out. The CI runners never idle. The
reviewers' queues are full. Utilization is magnificent. And a one-line
change still takes eleven days to reach production.

Ask where the eleven days went and you get an uncomfortable answer: the
change was *worked on* for about four hours. The rest was waiting — waiting
for review, waiting for a runner, waiting for the weekly release train,
waiting behind other changes in a big batch. The team isn't slow. The
*system* is slow, and the system is what nobody is looking at.

This document explains flow — the small set of results from manufacturing,
queueing theory, and delivery research that predict how fast work moves
through a software organization, and why the intuitive fixes ("work harder",
"keep everyone busy") make it worse.

![System Optimization](system_optimization.svg)

## Watch the work, not the workers

The unit of analysis is not a person or a machine but the **value stream**:
the full path a change travels from idea to running in production. Map any
real change along it and split every step into two kinds of time — time
being *worked on*, and time *waiting*. The ratio of work time to total time
is **flow efficiency**, and in most software organizations it lands below
15%. The eleven-day one-liner is normal.

That single measurement redirects all improvement effort: when flow
efficiency is low, the fix is never "do the steps faster." A step that takes
four hours inside eleven days of waiting could be done instantly and save
4% of the lead time. The fix is removing the *queues* — and queues obey
laws.

## Three laws of queues

**Little's Law.** For any stable process:

```
cycle time = work in progress / throughput
```

Read it backwards: at a fixed throughput, the *only* way to shorten cycle
time is to reduce work-in-progress. A team with thirty things in flight and
a throughput of three per week has an average cycle time of ten weeks —
regardless of talent, tooling, or effort. Halve the WIP and cycle time
halves. This is why WIP limits ("nobody starts a new ticket while two of
theirs are open") outperform exhortation, and why "start less, finish more"
is a law of arithmetic, not a slogan.

**The utilization curve.** Queue time doesn't grow linearly with how busy a
resource is — it explodes:

| Utilization | 50% | 80% | 90% | 95% |
| ----------- | --- | --- | --- | --- |
| Typical wait, as a multiple of service time | 1× | 4× | 9× | 19× |

A reviewer, CI pool, or on-call engineer running at 95% is not "efficient" —
they are a delay generator, imposing ~19 units of queueing on every unit of
work that touches them. Any system with variability needs headroom to absorb
it; past roughly 80% utilization, the wait curve goes vertical. Idle
capacity on a shared resource isn't waste. It's what fast response time is
made of.

**Batch size.** Work that travels in large batches — the quarterly release,
the 4,000-line PR — waits for the whole batch at every step, delays feedback
on every item in it, and concentrates risk into one big-bang event. Halving
batch size roughly halves queue time and makes each failure smaller and
easier to localize. Small PRs, frequent merges, and incremental deploys are
not stylistic preferences; they are batch-size controls.

## Waste, and the two things that manufacture it

Lean's contribution is a vocabulary for non-value-adding work — *waste* —
and software is full of it: stale PRs and long-lived branches (inventory),
sequential CI stages that could run in parallel (waiting), reports and logs
nobody consumes (overproduction), review gates on generated files
(overprocessing), bugs a linter could have caught (defects), constant
tool-hopping (motion).

But most waste is a *symptom*. It is manufactured by two deeper conditions:
**unevenness** — bursty, batch-and-queue arrival, like the end-of-sprint
merge crunch, which forms queues that then drain — and **overburden** — a
resource pinned past sustainable load, which the utilization curve punishes
directly. Cleaning up wastes one by one while the flow stays bursty and the
bottleneck stays saturated is mopping the floor with the tap running.

## Find the constraint; ignore almost everything else

At any moment, one step — the *constraint* — sets the throughput ceiling of
the whole system. If code review is the bottleneck, then faster builds,
better tooling, and heroic coding change *nothing* about delivery rate: the
work just piles up in front of review faster.

The Theory of Constraints turns this into a loop: **identify** the
constraint (largest queue, lowest throughput); **exploit** it (get maximum
output from it as-is — protect reviewers' review time before hiring more
reviewers); **subordinate** everything else to it (don't feed it faster
than it can drink — this is where WIP limits bite); **elevate** it (invest
in capacity only if it's still the bottleneck); then **repeat**, because
fixing one constraint reveals the next.

Two corollaries sting. First, improving a non-constraint is a form of waste,
however satisfying it feels. Second, most constraints are **policies, not
capacity**: a mandatory-approval rule, a single-designated-reviewer
convention, a "we deploy on Thursdays" tradition. A policy constraint costs
nothing to elevate but a meeting — check for one before buying hardware or
headcount.

## The order of operations

There is a fixed sequence for improving any process, and every step exists
to prevent a specific expensive mistake:

1. **Question the requirement.** The most upstream waste is a requirement
   that shouldn't exist. Distinguish the *obligation* (what outcome must
   truly hold) from the *mechanism* (the specific procedure someone once
   wrote down); mechanisms are negotiable in ways obligations are not.
2. **Delete.** Try removing the step behind something reversible — a flag, a
   dry run — and see what breaks. The fastest step is the one that no longer
   happens.
3. **Simplify** what survived deletion.
4. **Speed up** — parallelize, cache, batch — only what survived
   simplification, and measure: parallel speedup is capped by the serial
   fraction, and past a point more parallelism is *slower*.
5. **Automate last.** Automation locks a process in place. Automate an
   unnecessary or convoluted process and you have industrialized the waste.

The order matters because each step done out of order poisons the next:
optimizing a step that should be deleted is wasted work *plus* a new reason
to keep it.

## Measure — and don't chase noise

Delivery has a small standard instrument panel: how often you deploy, how
long a commit takes to reach production, what fraction of deploys cause a
failure, and how fast you recover when one does. Track them; treat a
regression in any of them as a bug, not weather. Note the panel's shape:
two speed metrics, two stability metrics — teams that are good are good at
*both*, because small batches and fast recovery serve both at once. When
speed and stability do genuinely compete, an **error budget** arbitrates:
set an explicit failure tolerance, spend the remaining budget on shipping
faster, and freeze feature risk to stabilize when the budget runs out. The
trade-off becomes a rule instead of a standoff.

One statistical discipline protects all of this. Every metric wiggles.
Some variation is **common cause** — the inherent noise of a stable process
— and some is **special cause** — an assignable, out-of-bounds event.
Reacting to common-cause noise as though it were signal ("build time was up
4% yesterday, who touched the pipeline?") is called *tampering*, and it
adds variance rather than removing it. Establish a baseline band first;
investigate only what leaves it. This is also why a flaky test is worse
than a nuisance: it destroys your ability to tell signal from noise at all.
An unstable process can't be measured, and what can't be measured can't be
meaningfully improved — stabilize first.

## The habit

Flow thinking compresses into a few reflexes: when delivery feels slow,
measure where the *waiting* is before blaming the *working*. Find the one
constraint and fix that, in order — question, delete, simplify, speed up,
automate. Prefer many small validated steps over one grand redesign, since
small steps compound and small bets fail cheaply. And keep one litmus test
for every "improvement": if it makes the system more complex without a
measured gain in flow, reliability, or cost, it isn't an optimization — it's
decoration.

---

*Related concepts: [shift-left](READ-defect-shift-left.md) is "build quality
in" made concrete — defects caught at the source are the cheapest waste to
remove; [push-out](READ-push-out.md) covers where recurring operational work
should live once flow is stable; and
[structural simplification](READ-structural-simplification.md) supplies the
complexity axes used to judge whether a change simplified anything. The full
operational reference for this concept — scan layers, waste tables, flow
levers, and the decision record — lives in
[SKILL.md](../.claude/skills/system-optimization/SKILL.md).*
