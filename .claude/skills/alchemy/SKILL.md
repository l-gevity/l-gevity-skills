---
name: alchemy
description: >-
    Runs a lightweight change preflight, then routes non-trivial design,
    refactor, and audit work through only the needed requirements and
    A.L.C.H.E.M.Y. skills. Explicitly trigger with `/alchemy`, `$alchemy`, or
    natural phrases such as "do some alchemy", "run alchemy on this", "use
    alchemy", or "give this an alchemy pass". Use for architecture, complexity,
    enforcement, shift-left, optimization, subsystems, increments (vertical
    slices), abstractions, cross-boundary refactors, consolidation, and over-engineering
    audits. Explicit invocation on a local bug fix, content or CSS edit,
    dependency bump, or trivial rename returns a cheap `SKIP` or `DIRECT`
    dispatch instead of loading every gate. Defines no new domain rules; routes
    to core sibling skills and task-matched companion skills.
---

# Alchemy

Command entrypoint for the adaptive A.L.C.H.E.M.Y. gate system. Keep the
default response terse: resume from the latest trustworthy decision, route to
the smallest useful stage set, state the verdict, and name the next action.

## 1. Command Grammar

Invoke as `/alchemy <alias> <subject>` in Claude Code or `$alchemy <alias>
<subject>` in Codex; the alias is optional. Natural language is equivalent:
`do some alchemy`, `run alchemy on this`, `use alchemy`, and `give this an
alchemy pass` all request adaptive dispatch on the active subject.

The subject is the invocation arguments. Where commands expand arguments,
`$ARGUMENTS` is that string; if it is empty or literally unexpanded, use the
surrounding request text. A natural phrase with no explicit subject uses the
active request or most recent unresolved task; never ask the user to restate
context already in the conversation or worktree. `?`, `help`, `--help`, or an
empty command with no active subject returns only this table.

| Alias | Route |
|:--|:--|
| none | Run the dispatch preflight; infer Design, Refactor, or Audit mode |
| `audit` | Start at the read-only `C₀` structural baseline |
| `full`, `all`, `walk the gates`, `complete alchemy` | `FULL`: every justified stage, each skip recorded |
| `M`, `minimum`, `necessity`, `worth` | `functionality-complexity-tradeoff` — worth it? |
| `A`, `architecture`, `first-principles` | `architecture-guidelines` — sound design? |
| `L`, `locality`, `placement` | `morphogenetic-architecture` — where does it belong? |
| `C`, `complexity`, `simplify` | `structural-simplification` — simpler? |
| `E`, `enforcement`, `architecture-as-code` | `architecture-as-code`, plus its stack reference only when rule files are written or changed — rules as code? |
| `H`, `hermetic`, `shift-left` | `defect-shift-left`, plus `ci-cd-reliability-architecture` for pipeline reliability — catch earlier? |
| `Y`, `yield`, `optimize` | `system-optimization` — optimize flow? |
| `left` | `defect-shift-left` — detect defects earlier |
| `out`, `push-out` | `push-out` — move toil out of humans |
| `down`, `bring-down` | `bring-down` — move bespoke code down |
| `zero-copy`, `source-of-truth` | `zero-copy-requirements` |
| `deps`, `dependency` | `dependency-lifecycle` |
| `infra`, `infrastructure` | `infrastructure-fit` |
| `signal`, `observability` | `observability-design` |

`left`, `out`, and `down` form the DevOps improvement triad, outside the
seven-gate sequence: run a triad move only when the user names it. During
`/alchemy Y`, recommend `out` or `down` when the bottleneck is manual toil or
bespoke implementation, but do not run them unless the user asks.

### Dispatch Preflight

Classify before reading any sibling skill body. Make dispatch the first
observable checkpoint: decide from the request, already-loaded context, skill
metadata, and the latest trustworthy decision artifacts; do not scan the
repository merely to choose a dispatch. After emitting the dispatch, inspect
only the artifacts and skills the route selects.

| Dispatch | Select when | Core route |
|:--|:--|:--|
| `SKIP` | Local behavior stays inside one governed boundary and asks no Alchemy question: copy/CSS, trivial rename, contract-preserving dependency bump, isolated in-boundary fix | None: load no gate skill; continue with matching companions and normal verification |
| `DIRECT` | An alias, or one unambiguous gate question: worth, dead code, speculative abstraction, or "should this exist?" is M; a defect found late, check placement, or CI detection timing is H or `left` | Only that gate or triad skill |
| `ADAPTIVE` | Structure, responsibility, data flow, abstraction, multiple requirements, or boundaries may change | The smallest justified set: a structural refactor inside one boundary is M, C, plus A when responsibility or public contract changes and H when verification placement changes; a new subsystem/service/library, cross-boundary dependency, increment cut through every layer (vertical slice), consolidation, or an aspect added or changed across several subsystems (auth, audit, logging, retry, i18n) is qualification as needed, M, A, L, C, E, H; an existing-code over-engineering audit is Audit mode from `C₀` |
| `FULL` | The user explicitly says `full`, `all`, `walk the gates`, or `complete alchemy` | Every justified stage, with the reason for each conditional stage skipped |

Natural language stays adaptive: only explicit full language selects `FULL`,
and Alchemy `FULL` is a traversal dispatch, not a gate's analysis mode. Do not
convert uncertainty into `FULL`; select the smallest plausible route, state
the uncertain signal, and stop at the first missing prerequisite.

Gate and triad aliases are authoritative: use only that core gate or triad
move, even when the subject mentions subsystem boundaries, and expand the core
route only for `audit` or explicit full-traversal language. Focused aliases
never silently run requirements qualification. If a focused gate lacks a
prerequisite, report the missing decision artifact and stop at that gate
unless the user asked for a broader pass. The prerequisites:

- Gate E remains blocked until Gate 3 records final acceptance; a `MOVE`,
  `SPLIT`, `MERGE`, or `INTRODUCE-BOUNDARY` first runs the bounded
  `L candidate → C measurement → L acceptance` handshake, re-entering L once.
- Gate Y runs in iteration 2, the iteration after the increment ships, from its
  stable, measured baseline, unless the request is explicitly about an
  existing bottleneck.

### Companion Skill Routing

Alchemy owns the core qualification and gate route, not every task domain.
From skill metadata and project instructions, select any non-Alchemy skill
whose trigger independently matches the subject, and read only the selected
companion bodies. A project profile may require companions for its domain,
stack, UX, security, accessibility, API, release, or evidence rules.

- When the subject decides where a fact, decision, or document belongs — a
  proposed document, a decision record, an architecture note, a status page, or
  a documentation-tree audit — select `zero-copy-requirements`. It names the
  artifact that owns the question; `push-out` prunes prose already covered by an
  executable source, and `requirements-traceability` anchors evidence once the
  location exists. None of the three is a qualification stage, gate, or acronym
  letter.
- When an advisory, drift, abandonment, license change, or end-of-life date
  names an owned dependency, select `dependency-lifecycle`; it classifies the
  bump, and only a contract-preserving bump is `SKIP`.
- When a risk survives verification into production, or alerts or telemetry
  are under review, select `observability-design`.
- When infrastructure is chosen, inherited, or questioned, select
  `infrastructure-fit`.
- When a gate is added over violations, narrowed, suspended, or removed, passes
  on a known-bad input, or cannot evaluate, or a baseline churns, select
  `gate-lifecycle`; it never places a check or decides how it blocks.
- `test-strategy` and `evolutionary-database-design` are two-pass companions
  that bracket A/L/C/E; the route in §2 orders their passes.
- `SKIP` skips only the Alchemy core; it never suppresses a matching companion.
  `DIRECT` keeps the core route focused while allowing independently triggered
  companions.
- Report companions explicitly. Use `None` when no companion trigger matches,
  and name no companion whose trigger is unmet or unknown; write a selected
  companion whose `SKILL.md` was not read in this task as
  `<skill> — Not run (<reason>)`.

### Execution Strategy

Execution is a second decision after dispatch, never a fifth dispatch: it
decides whether one agent or several carry out the selected route, and the
user never names agents. `SKIP` and `DIRECT` run `single-agent` and never load
orchestration. `ADAPTIVE`, `FULL`, and `audit` stay `single-agent` unless the
route in §2 selects `multi-agent`, which loads `alchemy-orchestrate`.

### Change Primitives

Every stage describes change with four primitives: **Subsystem**, **Aspect**,
**Increment**, and **Iteration**. Each sibling term specializes exactly one
and never redefines it;
[references/change-primitives.md](references/change-primitives.md) defines
them and maps each sibling term.

---

## 2. Adaptive Requirements Qualification

```text
Requirements Grounding, when evidence or meaning is absent or stale
→ M — Minimum
→ Requirements Topology, when relationships are non-trivial
→ Implementation Readiness
→ A — Architecture → L → C → E → H → Y
```

Qualification stages are conditional and never become acronym letters. Before
selecting stages for `ADAPTIVE`, `FULL`, or `audit`, read
[references/adaptive-route.md](references/adaptive-route.md): routing rules,
hand-offs, the gates and their handshake, the two-pass companion order,
execution selection, and the decision-trail format. The default `SKIP` and
`DIRECT` never need it; a run that must emit the decision trail of §3 opens it
for that format alone.

Read [references/failure-modes.md](references/failure-modes.md) when a run's
result looks wrong, an audit shows a symptom, or a trail has an unexplained
skip; route the recovery to the named stage instead of rerunning every gate.

---

## 3. Output Contract

Default output for a single-gate or simple routed request:

```
Dispatch:   <SKIP | DIRECT | ADAPTIVE | FULL>
Core route: <None | M | A | L | C | E | H | Y | left | out | down | ordered set>
Companions: <None | task-matched skills>
Execution:  <single-agent | multi-agent> — <independence or risk fact>
Verdict:    Proceed | Redesign | Drop | Defer
Reason:     <one or two lines>
Next:       <one concrete action>
```

For `SKIP`, emit this compact output alone with `Core route: None`; do not
load a core sibling merely to justify the skip. When one stage ran, open its
record with the block's first four lines and omit `Verdict`, `Reason`, and
`Next`: the record states them once.

Multi-stage runs, non-trivial design/refactor passes, audits, and explicit
requests for detail emit one combined decision trail in execution order,
including every stage used and every conditional stage skipped, then the scope
block; the route in §2 gives both formats.

Lead every run except `SKIP` that reaches a verdict with the four report blocks
the root instruction file defines, What I found, Why it matters, Do this first,
and What I did not check, then emit the records unchanged: the trail and scope
block, then each stage that ran in execution order, with the decision record
its skill's output contract defines. The trail summarizes stages; it never
replaces a stage's record.

## 4. Discipline

- **Claim only what ran.** `Core route` and the trail name a stage's decision
  only when its `SKILL.md` was read in this task; a selected stage that did not
  run, or one resumed from an earlier record, appears in the trail as `Not run`
  with the reason.
- **When a gate is consistently skipped across tasks**, that's a signal for
  `continuous-improvement` to update THIS skill, not for case-by-case
  reminders.
