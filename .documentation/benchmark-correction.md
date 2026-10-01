# Weekly-email benchmark correction

Declared 2026-09-30 before recording the fixture-backed version.

This is historical evidence from the withdrawn experiment. Replay paths below
are the original paths inside the verified experimental ZIP, not live active
scenario directories. Copies of this fixture, definition and transcript are
inside `.refactor-evidence/evidence.zip` at `worth-design-minimal-first/`; the full frozen inputs,
raw logs and earlier attempts remain in the archive documented by
[the evidence layout](../.refactor-evidence/README.md).

The earlier `worth-design-minimal-first` scenario asked about "our web app"
without supplying an app, an actor-bound obstacle, email eligibility, week
boundaries, or the meaning of its free-format field. Its machine expectation
nevertheless required `Decision: BUILD-minimal`. The recorded `NOT-GROUNDED`
answer correctly identified those missing facts. That failure is evidence of a
contradictory benchmark, not proof that grounding should be bypassed.

The request, blind rubric and all nine checks remain unchanged. Their file
SHA-256 is `470441ba53223d666c2f16b3265ac34b9e67cf9cb59b95eb5a186da0237632e5`.
The previous transcript is preserved at
`../.scenarios/worth-design-minimal-first/replays/unpaired-refactor-v5.json`,
SHA-256 `ff84d5db56631defeb8849db6756a8aad68751380ecef1af938ae64c7feccfcc`.
The other fixtureless attempts under that replay directory also remain.

The new `project/` is explicitly synthetic. Its README supplies the canonical
benchmark premises: account owners currently retrieve usage manually, want the
completed week's items by email, and may author one optional account note.
Existing application APIs already own usage queries, authenticated note editing,
recipient eligibility and idempotent account-notice delivery. The platform's
existing Monday UTC task hook is available. Only the weekly-summary binding is
missing; no registry, new delivery service, authoring workflow or framework is
required. Sample data includes eligible and ineligible accounts, zero usage,
other-account usage and exact week-boundary events.

Those declared premises make positive worth falsifiable: the design can remove
the specified manual retrieval step using existing interfaces while preserving
owner-only data, opt-in eligibility and optional text. They do not prescribe a
worth verdict to the model. Baseline contract tests verify the supplied APIs;
the README separately lists verification obligations for the proposed weekly
summary. A passing model recording still needs the unchanged nine checks and a
review of its reasoning.

Baseline verification on 2026-09-30: `node --test test/app.test.js` passed all
five existing-contract tests. They exercise account isolation and week edges,
optional owner-only notes, recipient eligibility and concurrent deduplication,
visible delivery failure/retry, and the established scheduled-task context.
They do not implement or prove the requested summary handler.

The single fixture-backed model recording met **6 of 9** unchanged checks and
failed acceptance. Its 749-word answer exceeded the 350-word limit, failed the
explicit list/free-format presentation check, and claimed Gate
L after reading only its Rapid reference rather than the owning `SKILL.md`.
It did evaluate worth and issued `BUILD-minimal`; the declared fixture context
supplied the facts that the old benchmark lacked. Its long code-first design and
gate ledger remain observed behavior failures; this correction is not a
successful minimal-design result. No reroll or check relaxation followed.

The recording is preserved at
`../.scenarios/worth-design-minimal-first/replays/unpaired-fixture-backed-v6.json`.
Its captured-source revision is `a19723f562c1` and transcript SHA-256 is
`f6b51944f017ef8fc79f6d4f49de15e42fedf3462f25d72552dc7b010557560b`.
See [fixture file hashes](benchmark-fixture-manifest.json),
[baseline API command output](benchmark-api-verification.log), and
[model recorder command output](benchmark-record-verification.log).

This is a new fixture-backed synthetic benchmark. Its result cannot be combined
with fixtureless runs as an identical-fixture improvement, and it cannot resolve
the originating plugin-design failure. The six paired refactor scenarios and
their frozen inputs are unchanged. No product, user study, production delivery
or universal skill effectiveness is claimed by these synthetic premises.
