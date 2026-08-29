# Push-Out: Where Does the Work Live?

Every team has an Alice. Alice knows how to rotate the TLS certificates. It's
not written down anywhere — it's a sequence of eleven steps, two of which are
"wait about five minutes" and one of which is "ignore the error, it always
says that." Twice a year someone posts *"how do we rotate the certs?"* in the
team channel, and the answer is always the same: **ask Alice**.

Then Alice goes on holiday, the certificate expires on a Saturday, and the
company learns what its checkout flow is worth per hour.

The certificate rotation was never the problem. The problem was *where the
work lived*: inside one person's head. This document explains push-out — the
idea that every piece of recurring operational work has a home somewhere on a
ladder from "a human remembers it" to "the system does it and improves
itself," and that moving work up that ladder is what turns a fragile team
into a durable one.

## The ladder of homes

Ask of any recurring task — deploys, cert rotations, onboarding a new service,
provisioning a database, granting access — *where does this work currently
live?* There are only six answers:

| Rank | The work lives in… | You can tell because… |
| ---- | ------------------ | --------------------- |
| **0** | **A person's memory** | "Ask Alice." No document survives her holiday. |
| **1** | **A team procedure** | There's a runbook or checklist; any teammate can follow it, by hand. |
| **2** | **A repo standard** | A script, CI job, template, or config convention does the mechanical part. |
| **3** | **A shared platform** | Several teams consume one maintained capability instead of each rolling their own. |
| **4** | **A self-service control** | Developers trigger it themselves — no ticket, no waiting for the ops team — inside guardrails. |
| **5** | **An adaptive system** | Metrics and feedback loops change the system without a human deciding each time. |

Each rung up is more durable than the one below. Memory evaporates with
turnover. Runbooks survive turnover but rot and get misexecuted at 3am.
Scripts don't misexecute, but every team writes its own. Platforms unify the
scripts, but become bottlenecks if humans sit in the request path. Self-service
removes the humans from the path. And an adaptive system notices its own
degradation before a human does.

"Pushing out" a piece of work means moving it one rung up this ladder — out of
fragile human execution, into more durable system capability. One important
nuance: what moves is the *execution*, never the *responsibility*. When cert
rotation becomes a pipeline, someone still owns certificates. Automation
without an owner is how systems rot silently.

## The moves, one rung at a time

The ladder isn't just a diagnosis — each gap between rungs is a specific,
familiar move:

- **0 → 1: Write it down.** Owner, inputs, outputs, steps, how to roll back.
  Unglamorous, and it's the move that fixes the Alice problem.
- **1 → 2: Make the machine do the steps.** The runbook that gets followed
  monthly becomes a script or CI job. Humans decide *whether*; the machine
  does *how*.
- **2 → 3: Stop copying the script between repos.** When five teams each
  maintain a slightly-divergent copy of the same deploy workflow, extract one
  shared, maintained version — a "golden path."
- **3 → 4: Get the humans out of the request path.** If the platform team
  spends its days executing other people's tickets ("please provision a
  database"), turn the ticket into a button, API, or CLI the requester runs
  themselves.
- **4 → 5: Close the loop.** Add the thresholds, alerts, and reviews that let
  the system trigger its own improvement — error budgets that halt deploys,
  autoscaling, dependency-update bots.

Skipping rungs is where this goes wrong, which brings us to the failure modes.

## Automating chaos industrializes confusion

The most tempting shortcut is jumping straight from rank 0 to automation:
nobody has written the process down, but someone volunteers to "just script
it." What gets scripted is one person's *recollection* of the process —
including the accidental parts, the steps that only exist because of a server
decommissioned in 2021, and none of the judgment calls.

An ad-hoc process executed by a human at least has a human noticing when
something looks off. The same process automated executes its own confusion
perfectly, every time, at machine speed. So the order is fixed:

1. **Delete first.** The cheapest work to automate is work that stops being
   done. Before pushing anything up the ladder, ask whether the task still
   serves a purpose. Reports nobody reads and approvals that rubber-stamp
   100% of requests are not automation candidates — they're deletion
   candidates.
2. **Standardize second.** Write it down; get the team agreeing on what the
   process even *is*.
3. **Automate third**, once there's a known-good procedure to encode.

## A button without guardrails just moves the toil

Self-service (rank 4) has its own trap. Giving every developer a
"provision a database" button is not progress if the button can silently
create an unencrypted, unbackuped, unmonitored instance in the wrong region.
You haven't removed the toil — you've exported it to the person pressing the
button, who now needs the platform team's expertise without having it, and
to the security team, who find out at audit time.

Real self-service is the button *plus* the guardrails: input validation,
policy enforced in code (encryption on, backups on, allowed regions only),
scoped permissions, an audit trail, observability, and a rollback path. The
guardrails are what let a non-expert press the button safely — they *are* the
product. A platform without them is a foot-gun vending machine.

The same skepticism applies one rung up: a dashboard is not an improvement
loop. A dashboard is rank-5 *scenery* until a threshold, a review cadence, or
an automated action hangs off it. If the graph going red doesn't change
anyone's behavior, the work of watching the graph is itself toil.

## Prose is where truth goes to drift

There's a quieter corollary about documentation. Once work has been pushed
into executable form — CI config, infrastructure-as-code, policy-as-code,
tests, schemas — any prose that re-describes the same mechanics becomes a
second source of truth. And second sources of truth don't stay true: the
pipeline changes, the wiki page doesn't, and six months later the
documentation is a well-formatted lie that new hires trust.

The fix isn't "keep docs updated" (nobody does); it's dividing the labor by
what each medium is good at. The executable source owns the *what* and
*how* — it can't drift from reality, because it *is* the reality. Prose keeps
only what code can't express: why this exists, who owns it, which external
constraint or trade-off shaped it, what to know when rolling back — plus a
link to the executable source. A ten-line README pointing at the pipeline
beats a three-page runbook describing it.

## Higher is not always better

The ladder has six rungs, but not every task should climb to the top. A
migration performed once a year by one team belongs in a runbook — building
it a self-service platform is over-engineering with extra steps. What
justifies climbing higher is frequency, risk, blast radius, and how many
teams depend on the task: a rare, low-risk chore earns a checklist; a daily,
high-risk, many-team path earns guardrailed self-service and a feedback
loop. The goal is not maximal automation; it's each piece of work living at
the rung that matches its cost.

## The habit

The concept compresses to one question, asked whenever you notice recurring
work: *where does this live, and what would move it one rung up?*

The signals that the question is overdue are easy to spot: the same
how-do-I question recurring in chat, the same ticket type recurring in the
platform team's queue, the same incident recurring each quarter, the deploy
that requires a specific person to be awake. Each is a piece of work
announcing that it lives too low on the ladder — and each has a
one-rung move waiting: write it down, script it, share it, make it
self-service, or wire it into a loop. Then, once the new path is proven,
retire the manual one — a runbook kept "just in case" alongside its
automation is the documentation-drift problem all over again.

---

*Push-out is one of three related "move it along the axis" ideas:
[shift-left](READ-defect-shift-left.md) moves defect detection earlier in
time, push-out moves recurring operational work out of human hands into
durable systems, and [bring-down](READ-bring-down.md) moves bespoke code down
into maintained, reusable capability. The full operational reference for this
concept — the complete ladder, target-rank heuristics, and move patterns —
lives in [SKILL.md](../.claude/skills/push-out/SKILL.md).*
