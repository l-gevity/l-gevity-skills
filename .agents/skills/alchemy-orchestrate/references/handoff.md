# Hand-off — `alchemy-handoff/1`

Returned by every package owner, read-only packages included. It links
artifacts; it never pastes them. A delegated agent reads this file and no
other part of this skill: the lead holds the rest.

```json
{
  "schema": "alchemy-handoff/1",
  "package": "P1",
  "owner": "agent-a",
  "status": "DONE",
  "attempt": 1,
  "base_commit": "3f9c2e1",
  "head_commit": "8a1d4b0",
  "requirements": ["REQ-12"],
  "decisions": [{"id": "D-4", "summary": "Validate at the HTTP boundary", "ref": "issue #42"}],
  "assumptions": ["Order totals are integers in cents"],
  "relied_on": [{"path": "src/orders/repository.js", "sha256": "<64 hex>"}],
  "changed_files": [{"path": "src/orders/validate.js", "sha256": "<64 hex>"}],
  "evidence": [{"id": "P1-E1", "criterion": "REQ-12-AC1", "command": "npm test -- orders", "exit_code": 0, "commit": "8a1d4b0", "summary": "14 passed"}],
  "claims": [{"text": "Order input is validated before persistence", "evidence": ["P1-E1"]}],
  "findings": [],
  "blockers": [],
  "next_owner": "lead",
  "integration_ready": true
}
```

Evidence and finding IDs start with the package ID and a hyphen, as `P1-E1`
and `P1-F1`, so the lead copies them into the ledger unchanged: the ledger
refuses a repeated evidence or finding ID (`SCHEMA`), and the gate's
`--review` matches a hand-off's findings to the ledger by ID and package.

`status` is `DONE`, `PARTIAL`, `BLOCKED`, or `FAILED`. A blocker is
`{"id", "text", "blocking": true|false}`; an evidence item needs `id`,
`command`, `exit_code`, and `commit`. A finding the package raises is
`{"id", "severity", "text", "evidence"}`, `severity` `blocking`, `major`, or
`minor`, citing evidence like a claim; the lead passes the saved hand-off to the
gate's `--review`, so a blocking or major one cannot leave the ledger.

`requirements` lists only the plan requirement IDs the package was assigned,
never finding IDs (`SCOPE_EXPANSION`). Every path in `relied_on` and
`changed_files` is relative to the root of the workspace the agent worked in,
with no commit suffix such as `@8a1d4b0`: the digest records the version seen
(`SCHEMA` otherwise). A deleted file is `{"path", "deleted": true}` with no
digest; the receiver checks it is gone. Each acceptance criterion of a `DONE`
package is named by the `criterion` of at least one evidence item
(`UNEVIDENCED_CRITERION`). For a `command` criterion that item ran the plan's
exact command and exited 0; put `criterion` on no other item, an absence search
included, because a tagged item that fails contradicts the claim. An item passes when `exit_code` equals its
optional `expect_exit`, 0 when absent: a search proving absence records the
code it returns on no match, such as `git grep` with `"expect_exit": 1`, so an
error code still fails. Evidence for a `command` criterion passes only on exit
0; its `expect_exit` is ignored. Commits match when one is a hex prefix
of the other and at least seven characters long. `relied_on` lists every
artifact the work depended on with the digest it saw, so a receiver detects a
context that moved underneath it. `changed_files` digests are taken after the
change, so a receiver detects a summary that does not match the workspace.

Every claim cites at least one evidence item, read-only findings included. A
claim resting on a file read cites the command that shows it, such as
`git grep -n <pattern> -- <path>` or `sed -n '<a>,<b>p' <path>`, so a receiver
can run it again; a file:line citation in prose is not evidence, and the claim
is `UNSUPPORTED_CLAIM`. `command` is the command exactly as it ran, never a
paraphrase or a placeholder: a paraphrase hides the flag or the default that
decided the result. `exit_code` is that command's own, never the exit code of a
later pipe stage or of a following `echo`. When a check's failure is itself
the finding, such as a test that fails on this host, record the code it
returned as `expect_exit` and say so in the claim; a `command` criterion still
passes only on exit 0.
