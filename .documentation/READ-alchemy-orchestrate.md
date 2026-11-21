# Orchestration: use more agents only when it pays

This skill decides whether one agent or several should do the work, then checks ownership, hand-offs, and completion. Use it for explicit delegation, independent review, or work split across agents.

## Core concepts

- **One agent is the default.** Add agents for independent work or a useful independent review.
- **Capabilities follow the task.** Architecture, implementation, and verification do not need permanent agent roles.
- **Contracts precede dependent work.** Packages name their owner, allowed files, prerequisites, and acceptance checks.
- **Evidence decides.** A hand-off saying “tests pass” needs commands, results, and file fingerprints the receiver can check.

Parallel packages must not write the same files. Reviewers do not review their own work. Delegation, retries, and corrections have explicit bounds, and each agent stops at its own budget of turns and tool calls.

```mermaid
flowchart LR
    C["Agreed contract"] --> B["Backend owner<br/>Separate files"]
    C --> F["Frontend owner<br/>Separate files"]
    B --> V["Independent check<br/>Combined revision"]
    F --> V
```

## Apply it

1. Describe the change and identify work that can proceed independently. Keep shared contracts ahead of their consumers.
2. Check that the runtime which will execute the plan can spawn and wait for agents before anyone approves a delegated plan, and never plan orchestration for a `SKIP` or `DIRECT` route. Then define and mechanically check the execution plan. For an unattended run, prove required tools, accounts, data, and escalation paths work before starting.
3. Start dependency-ready packages after their prerequisites are accepted and integrated; keep wave barriers when the runtime cannot safely stream completions or inputs are shared. Check hand-offs against actual files and verify acceptance criteria on the final combined revision. The lead runs each check once there and keeps its output; reviewers read that output instead of running the same checks again.

One integration reviewer covers what package reviews did not; a second provider is added only for a named, distinct risk. Correction reviewers receive a diff from the last reviewed head, the findings it answers, and current check evidence. Opt-in command reuse shares an execution only within one recorder invocation for repeat-safe checks with stable inputs; each criterion retains its own record.

Blocking findings need evidence of resolution or explicit human risk acceptance; a read-only audit instead reports them open, each with its evidence, and the gate checks the ledger kept every one the agents raised. Minor findings stay open for the pull request instead of costing another correction round. The skill's workflow requires human approval before merging.

## Project example

An export feature needs a backend endpoint and a frontend screen. Agree on the response contract first. Then assign separate files to each package and give the integrated flow to a reviewer who wrote neither part. If both packages need to edit the same contract, sequence that work.

> `$alchemy-orchestrate` Plan backend and frontend export work after the response contract is agreed. Name file ownership and the final integration check.

[Full skill](../.claude/skills/alchemy-orchestrate/SKILL.md)

<!-- skill-revision: 117da09a37a2 -->
