# alchemy-orchestrate runtime adapters

These files connect [alchemy-orchestrate](../SKILL.md) to three runtimes. They
carry no methodology. Packages, hand-offs, ledgers, and check codes are defined
in [contracts.md](../references/contracts.md). Authority, recovery, and
permissions are defined in [governance.md](../references/governance.md). Agent
descriptions and instructions are rendered at install time from the
`envelopes` of `alchemy-workspace.json`, so the profile stays their only
source.

## Install

```text
python <skills>/alchemy-orchestrate/scripts/init_workspace.py --runtime claude-code|codex|unstoppable|all [--root <project>] [--profile <file>] [--dry-run]
```

`<skills>` is `.agents/skills` or `.claude/skills`. The installer reads the
defaults from `../assets/alchemy-workspace.json`. The project profile
(`--profile`, or `alchemy-workspace.json` at the root) overrides them key by
key. The installer prints one line per file:

- `created`: the file did not exist.
- `unchanged`: the content is identical, line endings ignored.
- `kept (wrote <file>.l-gevity; merge manually)`: the file existed with other
  content. It is not touched, and the rendered version is written beside it.

It also writes `alchemy-workspace.json` from the defaults when the root has
none. It writes `<state_dir>/.gitignore` containing `*`, so run records are
never committed and your own `.gitignore` is left alone. A second run reports
`unchanged` for every file. Exit 0, or 2 on bad arguments or an unusable
profile. The profile is unusable if `execution.max_parallel_agents` is not a
positive integer. It is also unusable if a `skills.roots` entry is not a
relative path made of letters, digits, `.`, `_`, `-`, and `/` without `..`;
these entries are written into permission rules. `repository.state_dir` must
resolve strictly inside the project by both Windows and POSIX rules. It is
refused when empty, `.`, absolute, rooted, UNC, drive-prefixed (`C:\x`,
`D:x`), or when it contains `..` or `:`. The `alchemy-check` action applies
the same state_dir rule.

## Execution categories

| Category | Claude Code | Codex | Unstoppable Code |
|:--|:--|:--|:--|
| Native autonomous agent spawning | Agent tool with `subagent_type` `alchemy-implementer` or `alchemy-analyst`, from `.claude/agents/`. Verified: `claude -p` in a project holding only these definitions named both. | `spawn_agent` and `wait_agent`, with the custom agents in `.codex/agents/`. Verified with `codex exec` (codex-cli 0.159.0) in a fresh project, trusted and untrusted alike: asked to list spawnable agent types it named `alchemy-analyst` and `alchemy-implementer`, spawned `alchemy-analyst`, waited, and the agent answered with an `alchemy-handoff/1` record rendered from its envelope instructions. | A chat runs a Claude Code or Codex harness, so native spawning in a chat is that harness's mechanism, as in the two columns to the left. Observed: a Claude-harness chat exposes the Agent tool. |
| Delegation through supported runtime interfaces | `claude -p --agent alchemy-implementer` runs one whole session as that agent. The flag is in `claude --help`; not exercised. | `codex exec` runs one non-interactive session. Not exercised for delegation. | Chat tools observed in a Claude-harness chat: `DispatchAction` `chat.create` and `projects.create_task`, `StartForkedAgent`, `StartBranchedAgent`. Not exercised. |
| Preconfigured workflow execution | None shipped | None shipped | The `alchemy-multi-agent` pipeline, described below |
| Unsupported → explicit single-agent fallback | When the Agent tool is unavailable or the alchemy agents are denied (`execution.multi_agent: off`), the lead runs every package and reports that independent review was not performed. | When the spawn tools are unavailable, the same fallback applies. | The `execute` step tells the lead not to carry out another owner's package under that owner's label when its harness cannot launch sub-agents. It returns `BLOCKED` and reports that the plan must be re-planned as `single-agent`, which section 4 step 5 of the skill requires. |

`execution.multi_agent` (`auto` or `off`) is rendered where a runtime has a
setting for it. For Claude Code, `off` adds `Agent(alchemy-analyst)` and
`Agent(alchemy-implementer)` to `permissions.deny`. For Codex, `off` adds
`[features] multi_agent = false`. Codex reads that setting: `codex features
list` shows it in a trusted project. It is not verified to remove the spawn
tools, because Codex's model-visible prompt still carries the multi-agent role
text. In every runtime the router also honors `off` through its instructions,
and the plan check fails a multi-agent plan under `off` with `MODE_MISMATCH`.

## Capability matrix

| Capability | Claude Code | Codex | Unstoppable Code |
|:--|:--|:--|:--|
| Skill discovery | `.claude/skills/` through the Skill tool. The rendered agents fall back to reading `SKILL.md` under `skills.roots`. | Project `.agents/skills/`. Verified: listed as a skill root in `codex debug prompt-input`. | The harness's own discovery. Pipeline prompts read `SKILL.md` by path, because the Claude `read_only` preset allows only Read, Glob, Grep, and NotebookRead (read from the bundled `agent-prompt` action). |
| Agent definitions | `.claude/agents/alchemy-analyst.md` and `alchemy-implementer.md`. Loading verified. | `.codex/agents/alchemy-analyst.toml` and `alchemy-implementer.toml` with `name`, `description`, and `developer_instructions`. Loading verified (see above). | `builtin/agent-prompt` steps in the pipeline. In a chat, the harness's definitions. |
| Least-privilege envelope enforcement | The analyst gets `tools` without Edit, Write, or NotebookEdit, and `disallowedTools: Edit, Write, NotebookEdit, Agent`. Instruction-level only for shell writes (limitation: Bash stays available for running tests). The hand-off check's `SCOPE_VIOLATION` is the enforcement. | Instruction-level only (limitation: `sandbox_mode` and `approval_policy` cannot be set per agent, so every agent inherits the parent session's). `SCOPE_VIOLATION` is the enforcement. | `permission_preset` per step: `read_only` for planning and review, `dangerous_all` for the lead's execute, ledger, and correction steps. Sub-agents launched inside a step follow that harness's column. |
| Delegation-depth bound | `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` in `.claude/settings.json`, plus `Agent` in both agents' `disallowedTools`. | Instruction-level only (limitation: Codex's prompt tells agents that children can spawn their own sub-agents, and no depth key is documented). The plan check's `DELEGATION` code is the enforcement. | Fixed by the job graph. Inside a step, the harness's column applies. |
| Concurrency cap | `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` = `execution.max_parallel_agents`. | `[agents] max_concurrent_threads_per_session` = `execution.max_parallel_agents`. Verified in a trusted project: a value of n gives n+1 slots including the lead, matching the profile's "lead excluded". | The review matrix uses `max_parallel: 2`. Inside a step, the harness's column applies. |
| Workspace isolation | `alchemy-implementer` sets `isolation: worktree`. `worktree.baseRef: head` makes that worktree branch from the lead's current HEAD instead of the default branch. Committed state only. | None (limitation: Codex's prompt states that all agents share one working directory, and edits are visible at once). Disjoint write sets from the plan check are the only guard. | The pipeline runs in the worktree or directory it is dispatched in (`scope: [directory, worktree]`); dispatch it from an Unstoppable worktree for isolation. Sub-agents follow the harness's column. |
| Cross-provider review | Not native | Not native | The pipeline's `review` matrix runs `reviewer_claude` and `reviewer_codex`. The review track `alchemy-independent-review.md` adds `claude-opus-5` and `gpt-6.1-sol` to the bundled Code Review (Multi-Provider) pipeline. Verified: its `discover-review-tracks` action emits two reviewers from the track. |
| Human approval checkpoints | `permissions.ask` covers `git push`, `gh pr create`, and `git clean`. `permissions.deny` covers merge, force-push, `reset --hard`, and `branch -D`. | Instruction-level only (limitation: no per-command rule is rendered; the session's approval policy applies). | `builtin/request-input` at `approve_plan`, `approve_pr`, and `escalate` |
| PR creation | `gh pr create` asks first; `gh pr merge` is denied. | Instruction-level only: the implementer envelope forbids push and pull requests. | `builtin/github-create-pr`, only after `approve_pr`. It pushes the branch itself and refuses uncommitted changes (read from the bundled action). Nothing merges. |

## Installed files

| File | Purpose |
|:--|:--|
| `alchemy-workspace.json` | Project profile, written from the defaults when absent |
| `<state_dir>/.gitignore` | Keeps run records (`plan.json`, `handoffs/`, `ledger.json`) out of git |
| `.claude/agents/alchemy-analyst.md` | Read-only package agent, rendered from `envelopes.analyst` |
| `.claude/agents/alchemy-implementer.md` | Writing package agent in its own git worktree, rendered from `envelopes.implementer` |
| `.claude/settings.json` | Depth 1, the concurrency cap, `worktree.baseRef: head`, and the ask, deny, and allow rules |
| `.codex/agents/alchemy-analyst.toml`, `alchemy-implementer.toml` | The same two envelopes as Codex custom agents |
| `.codex/config.toml` | The concurrency cap, plus `[features] multi_agent = false` under `off` |
| `.unstoppable-code/actions/alchemy-check/` | Runs `check_orchestration.py` from the skills tree in `plan`, `preflight`, `handoff` (one file or a directory), or `gate` mode. Keeps the JSON report and outputs `verdict`, `summary`, and `report_file`. Fails unless the verdict is PASS or ACCEPT; `enforce: 'false'` only reports. It can extract the plan from a structured-output file (`plan_field`). `integrated` adds wave heads to the checked copy's `base.integrated`. `digests: 'false'` checks hand-offs structurally, without `--root`. In plan mode it can also require the plan's base (`expect_base`) and publish the plan to `<state_dir>/<run id>/plan.json` (`publish`), and it outputs `unattended` and the `plan_digest` a preflight record binds to. Preflight mode checks the record with `--root` at the repository root, so the repository must still be at the plan base. In gate mode, `preflight` names the preflight record, passed when the file exists; a gate on an unattended plan without a passing one fails. Commit prefixes match only when both sides have at least 7 hex characters. |
| `.unstoppable-code/actions/alchemy-snapshot/` | Outputs the head commit. Given a base, it writes the diff from that base to the working tree for reviewers that cannot run git. `require_clean` fails on uncommitted changes. |
| `.unstoppable-code/pipelines/alchemy-multi-agent.yaml` | The preconfigured workflow below |
| `.unstoppable-code/review-tracks/alchemy-independent-review.md` | Cross-provider review track for the bundled multi-provider review pipeline |

## The pipeline

Dispatch it with an `objective`. The `lead`, `reviewer_claude`, and
`reviewer_codex` model aliases can be retargeted. The jobs run in this order:

1. `start` records the head.
2. `plan` runs read-only. It routes with the `alchemy` skill and writes an
   `alchemy-plan/1` record as structured output.
3. `plan_check` extracts and checks the plan, requires its base to be the
   recorded head, and publishes it to the run directory.
4. `approve_plan` asks the human: continue or stop.
5. When the plan sets `execution.unattended`, `preflight` has the lead run a
   probe for every need the packages and the profile declare, at the base,
   and write `preflight.json` to the run directory, bound to the plan digest.
   `preflight_check` checks it and fails on any verdict but `PASS`. An
   attended plan skips both jobs.
6. `execute` runs only when the plan is attended or the preflight verdict is
   `PASS`. It has the lead run the packages through native sub-agents. It saves
   each hand-off to `handoffs/<package>.json` and checks it on receipt, digests
   included. It integrates and commits the accepted packages, records each
   wave's head in the run plan's `base.integrated`, and returns those heads as
   `integrated_heads`.
7. `handoff_check` re-checks every hand-off structurally and snapshots the
   diff from the base. It passes the returned heads as `integrated` and does
   not check digests, because later waves legitimately change files that
   earlier hand-offs relied on or changed. Each correction pass repeats this
   check, adding that pass's heads and the run plan's amendments.
8. `review` runs two read-only reviewers on different providers, in parallel.
   They see the plan, the diff, and the test commands, not the hand-offs.
9. `consolidate` has the lead re-run the checks and build `ledger.json`.
10. `gate` runs the ledger through the gate check, with the run's
    `preflight.json` when it exists, so unattended work without a passing
    preflight bound to the plan cannot pass (`PREFLIGHT_REQUIRED`). It is
    given the approved digest (`approved`) and the repository (`repository`),
    so the rework bound is the one committed at the plan base, and it outputs
    `correction_passes`: that bound, or an authorized extension's ceiling,
    minus the most cycles any origin chain has taken.
11. On `FAIL` with passes left, the `correction` job loops, at most
    `correction_passes` times (`max_iterations`). Each pass runs, in order:
    `amend`, where the lead appends amendments to the run plan and changes no
    code; `amend_check`, the plan check on the amended plan against the
    approved digest, which fails the job before anybody edits; `correct`,
    which carries out the new amendments by their owners; the structural
    hand-off check and a snapshot; `review` by one read-only reviewer, who
    records convergence links; `reconsolidate`; and `regate`, the gate check.
    `loop` restarts the job only when that gate says `FAIL` and passes are
    left. `ESCALATE` (`REWORK_LIMIT`, `NOT_CONVERGING`) ends the loop.
12. `escalate` follows `ESCALATE`, a `FAIL` with no passes left, a failed or
    blocked correction pass, a last re-gate that did not pass, or an
    execution that did not integrate. It asks the human, re-runs the gate,
    and ends the run failed unless the gate now passes. Its answer records no
    extension: a raised bound is a new approved plan.
13. After a `PASS`, `approve_pr` re-runs the gate and asks the human: open a
    pull request or stop. `create_pr` then opens it.

Every check after planning re-extracts the plan from the planning step's own
output, not from the copy the agents read, and adds the returned
`integrated_heads` as `base.integrated`. With `run_plan` it also adds the
run plan's `amendments` and `base.integrated`; nothing else is read from the
copy the agents write, so the approved part stays the planning step's. A job output
the run never produced interpolates as an empty string, and `join()` turns the
head list into one input; both rules were read from the CLI's expression
evaluator. A job with its own `if:` runs
whether or not the jobs it needs succeeded, so each such condition tests
`needs.<job>.result`. This rule was read from the CLI's scheduler.

## Limitations and cost

- **Deny rules are a guardrail, not a sandbox.** Claude Code matches the
  command text, so `git -C . push` is not matched by `Bash(git push *)`.
  Neither is `gh api` calling the merge endpoint.
- **`dangerous_all` steps do not prompt.** The pipeline's lead steps run
  under `dangerous_all`, which is Claude's `bypassPermissions` mode, and that
  mode skips permission prompts, so the `ask` rules do not stop them. Whether
  the `deny` rules still block there was not verified. In the pipeline, the
  human checkpoints are the `request-input` jobs.
- **Headless Claude Code stops background sub-agents.** Sub-agents start in
  the background; in `claude -p`, Claude Code stops them 10 minutes after the
  lead's last turn. A recorded run lost its verifier that way
  (`.pilot/results/claude-multi-parallel-1.json`). The settings set
  `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` to one hour; interactive sessions
  re-invoke the lead when a sub-agent finishes and are not affected.
- **The pipeline's lead step ends with its turn.** `builtin/agent-prompt` asks
  for its structured result when the lead's turn ends, so sub-agents still
  running in the background are abandoned. Runs e2e-3 and e2e-4 lost wave 2
  this way and correctly returned `ESCALATE`. The spawn instruction now has the
  lead launch each wave in the foreground (`run_in_background: false`) in
  Claude Code and wait with `wait_agent` in Codex.
- **Claude Code ignores the `allow` rules until the workspace is trusted.**
  In an untrusted temp project, `claude -p` printed: "Ignoring 4
  permissions.allow entries … this workspace has not been trusted".
- **Codex reads `.codex/config.toml` only in a trusted project.** Verified: an
  untrusted project's cap was ignored, and a trusted one's was applied.
- **Codex spawns sub-agents only on explicit instruction.** Its prompt says to
  spawn sub-agents only when the user, AGENTS.md, or a skill explicitly asks
  for it. An automatic multi-agent decision therefore needs the skill text to
  ask for sub-agents in so many words.
- **`worktree.baseRef: head` branches from the lead's last commit.** The lead
  must commit before it launches implementers. After it integrates a wave, it
  records the new head in the plan's `base.integrated`, which the hand-off
  check accepts as a base for later waves.
- **Claude reviewers under `read_only` cannot run commands.** They judge the
  diff and the tests and list what they could not run. The lead re-runs the
  checks when it builds the ledger.
- **One reviewer per correction pass.** The loop is one job, so its review
  is a step, not a matrix over both providers as in `review`; the second
  provider reviews only the planned work. The loop's bound is read from the
  checked gate, not from the prompt.
- **`pipelines validate` checks structure only.** It accepted a missing
  project action, an unknown model alias, and a malformed `if:`. The pipeline
  has been validated and its two actions run locally; the pipeline itself has
  not been executed end to end, and neither have its preflight jobs.
- **One run costs several context loads.** A run takes a planning context, a
  lead execution context with one context per sub-agent, two reviewer
  contexts, and a ledger context. Each correction pass adds three more:
  amend and correct for the lead, and one reviewer. Measure
  a run against the single-agent baseline as governance §6 describes before
  keeping the multi-agent mode.
