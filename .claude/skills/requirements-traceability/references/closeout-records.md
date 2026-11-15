# Requirements Traceability — Closeout Records

The two records a closeout writes, in addition to the trace decision and any
outcome-evidence record in `SKILL.md`: the completion record on the issue or
change record, and the compact trace note.

## Completion Record

Close the record only when it preserves:

- the bounded canonical requirement and criterion IDs;
- the completion boundary, such as acceptance, release, or production;
- the exact revision, artifact, environment, and executed run evidence;
- implementation and verification anchors;
- evidence freshness when the operational proof can expire; and
- named gaps, deferrals, and owners without implying a broader completion state.

Use repository markers according to the repository's existing convention:

- an immutable checkpoint or tag is optional when the exact source snapshot
  matters; its name must not imply release, production, or outcome proof that
  the evidence does not establish;
- a milestone groups multiple work items toward a shared objective; do not
  invent one for a single closeout unless the project explicitly uses that
  convention; and
- keep unresolved release or production work separate from an accepted
  increment.

```text
Completion record:
- Subject: <capability or bounded increment>
- Decision: TRACEABLE | PARTIAL | BLOCKED
- Canonical scope: <requirement and criterion IDs>
- Completion boundary: <acceptance | release | production | other>
- Revision/artifact/environment: <immutable identities>
- Implementation: <stable anchors>
- Executed evidence: <run identities and results>
- Evidence freshness: <current through date, stale, or not applicable>
- Gaps/deferred: <gap, owner, and the issue or milestone check that carries it>
- Outcome status: <linked states or not assessed>
- Repository marker: <change record; optional checkpoint; aggregate milestone>
```

## Closeout Trace Note

For implementation or review closeout, append a compact note:

```text
Trace:
- Source: <requirement set, issue, or admitted increment>
- IDs: <requirement and criterion IDs>
- Implementation: <stable artifacts>
- Evidence: <executed tests or operational results>
- Outcomes: <hypothesis IDs, evidence states, freshness, and observation links>
- Gaps/deferred: <none or named gaps; representation gaps carry expiry>
```
