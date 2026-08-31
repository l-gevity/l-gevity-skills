---
name: standup
description: >-
    Composes a short daily standup from verified repository state only: recent
    commits, open pull requests, issues, CI runs, deadline risk, architectural
    debt, and requirements drift. TRIGGER when the user asks for a standup, a
    daily update, or "what is the status today", or invokes `/standup` (Claude)
    or `$standup` (Codex). SKIP for release notes, changelogs, sprint reports,
    retrospectives, incident reports, and any narrative allowed to contain
    unverified claims. Reads project parameters (deadlines, requirements gate,
    coverage artifact) from a project profile outside this skill; never invents
    them and never carries a finding over from an earlier standup without
    rechecking it.
---

# Daily Standup

> **Core Directives**
>
> - **Verified only**: every line traces to a command output, file, or API
>   response observed in this run. No inference, no memory, no carry-over.
> - **Delta only**: anything identical to yesterday is by definition not
>   standup news and stays out.
> - **Bounded**: the whole message fits in ~25 lines. Six sections, bullets,
>   no prose, no closing summary.
> - **Method is generic, parameters are local**: deadlines, gate commands, and
>   artifact paths live in the project profile, never in this file.

## 1. Trigger & Scope

Run when a standup or daily status update is requested. Reference date is
today; the report covers the last two working days.

Do not run this skill to produce release notes, sprint reviews, retrospectives,
or stakeholder narratives — those admit interpretation, this does not.

## 2. Project Parameters

Resolve in this order and stop at the first hit per parameter:

1. Parameters named in the invocation.
2. A project profile file: `standup.profile.md` in the repository root, or the
   path the user names.
3. Discovery: the project's script registry (`package.json`, `Makefile`, CI
   config) for the requirements gate, and the artifact that gate maintains for
   coverage totals.
4. Not found: report the parameter as not configured. Never invent one.

Profile shape — the only project-specific lines in the whole method:

```text
Deadline:           <product> <milestone> <YYYY-MM-DD>   (repeat per deadline; omit when none)
Requirements gate:  <command>                            (omit when the project has none)
Coverage totals:    <path to generated coverage artifact>
Working language:   <language>                           (optional; default: the user's working language)
```

Never copy a value out of the profile into this skill, and never edit this
skill per project — an update to the skill library overwrites it.

## 3. Method

Six sections, fixed order.

### 3.1 Done — last 2 working days

Run `git fetch origin --quiet` (refs only, does not touch the working tree),
then:

```text
git log --all --since="2 days ago" --pretty=format:"%ad|%an|%s" --date=short
```

Summarize the substance in max. 5 bullets. Do not copy commit subjects verbatim
when they are not self-explanatory. Leave out dependency-bot bumps unless one
fails or blocks something.

### 3.2 Blockers

- Check open pull requests, open issues, and the latest CI run on the default
  working branch (e.g. `gh pr list`, `gh issue list`, `gh run list`).
- Real blockers only: failing gates, pending decisions or signatures, external
  dependencies. Leave out routine PRs such as dependency bots.
- External dependencies surface as open issues. Carry one only after verifying
  it is still current; drop it once resolved.
- Mention only what this run actually verified.

### 3.3 Progress & risks against the deadlines

One line per deadline from the project parameters: remaining calendar days plus
an assessment (on track / at risk / late), grounded in 3.1, 3.2 and 3.5. No
deadlines configured: say so instead of inventing one.

### 3.4 Architectural debt

Check the open issues (reuse the 3.2 query) for structural debt — not
individual features: shared components with low adoption, performance or cost
problems in the infrastructure, a model or API without a screen, data-model
gaps. Usually labeled `enhancement`. Max. 3 bullets, only the heaviest per
theme, with issue number and link, freshly checked rather than carried over.
Close with one sentence: increasing, stable, or decreasing.

### 3.5 Requirements drift

- Run the requirements/traceability gate from the project parameters. Green:
  one line suffices. Red: name which gate and what is broken. No such gate
  exists: one line saying drift is unmeasured.
- Report the totals from the coverage artifact (or whatever coverage matrix or
  requirement register the gate maintains) in one line: requirements done x/y,
  admitted and tested criteria x/y, plus the one or two modules with the largest
  gap — admitted without an implementation anchor, or with untested criteria.
- Leave out static context (admission breakdowns, blocked-decision lists,
  tooling caveats) unless it changed. State a trend only when figures from an
  earlier standup are actually available.

### 3.6 Proposal for today

One to three concrete, actionable items, prioritized by the biggest risk.
Include one when debt or drift is increasing, or when a gate fails.

## 4. Evidence Rules

- A command that fails, is unavailable, or is not configured is reported as not
  run, with the reason. Never infer its result and never omit it silently.
- An empty section says so in one line rather than being padded or dropped.
- No praise, no recap of yesterday, no closing summary.
- Write in the user's working language.

## 5. Output Contract

Emit a coder-facing standup report:

```text
Standup — <YYYY-MM-DD>

Done
- <max 5 bullets | nothing merged in the window>

Blockers
- <verified blockers | none verified>

Progress & risks
- <one line per deadline | no deadlines configured>

Architectural debt
- <max 3 bullets with issue number + link | none found>
- Trend: increasing | stable | decreasing

Requirements drift
- Gate <name>: green | red (<what is broken>) | not configured — drift unmeasured
- Requirements done <x/y>, tested criteria <x/y>; largest gap: <module(s)>

Proposal for today
- <1-3 items, biggest risk first>

Not run: <check + reason | none>
```

## See also

- **`requirements-traceability`** — owns the coverage and drift evidence this
  report reads; it does not read this report.
- **`ci-cd-reliability-architecture`** — owns the release and pipeline states
  behind a failing gate reported as a blocker.
- **`system-optimization`** — turns a recurring blocker or a rising debt trend
  into a constraint analysis instead of a daily line item.
- **`functionality-complexity-tradeoff`** — decides what to do with debt this
  report only counts.
