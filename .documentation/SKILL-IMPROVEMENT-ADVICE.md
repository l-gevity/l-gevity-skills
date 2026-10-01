# Verified improvements and the next refactor

Reviewed 2026-10-01. Keep the replay runner, checker/accounting fixes, installer
managed blocks, and the continuous-improvement replay protocol. The failed
Alchemy/M/A/L/C/root behavioral changes were withdrawn from active guidance.
They are preserved for research, not accepted or repinned into a consumer.

Full skill validation, all 52 deliberate validator mutations, 26 runner tests,
40 checks across nine fresh scenarios, and both installer suites pass.
The selected subset's fresh checks are recorded in
[proven-improvements-verification.json](proven-improvements-verification.json).
The [next-refactor prompt](NEXT-SKILLS-REFACTOR.md) carries the remaining work.

## What is retained

The paired runner accepts Git revisions or directories, freezes both sources,
identical requests/fixtures, criteria and checker before execution, randomizes
arm order, and atomically checkpoints arms and completed pairs. An isolated
judge sees anonymous A/B reports and bounded product evidence. Source hashes,
raw traces, lengths, results, previous attempts and resume inputs persist.
Its 26 deterministic regressions cover freezing, interruption, isolation,
cleanup recovery and accounting. Guidance costs count unique whole-file word
estimates through Skill, Read and successful content search, never token usage.

All eight installers now merge one managed block into the agent's own root
file, preserve surrounding instructions, replace the block on reinstall/repin,
adapt skill links, and reject malformed markers before mutation. The suites
exercise first/repeat install, real repin and preservation: 252 Bash checks and
504 PowerShell checks across two hosts. Both suites passed again on the restored guidance.

The checker recognizes equivalent route letters/full skill names and explicit
verdict punctuation while rejecting claims for unloaded stages. Standard
recordings bind to the complete captured scenario, fixture and available
skill sources. CI runs the deterministic replay tests.

## Why the skill bundle was withdrawn

The historical v6 comparison used three runs per arm for each of six cases.
Its guidance hash was
`5cac1e7de382a3ef8454bfb21952684bac6c9b4ac59dacb9e87574b5d076e864`.
This is the preserved experimental source, not the selected current source.
[Results and hashes](refactor-verification.json) and
[unchanged criteria](refactor-replay-criteria.md) remain available.

| Historical case | Mean report words, before → after | Candidate ≤350 | Blind preference |
| --- | ---: | ---: | --- |
| SKIP | 149 → 179 | Not a SKIP criterion | After 2/3 |
| DIRECT worth | 972 → 355 | 1/3 | After 3/3 |
| Existing retry audit | 995 → 368 | 0/3 | After 2/3 |
| ADAPTIVE structural | 2,944 → 374 | 1/3 | Before 3/3 |
| Recovered plugin comparison | 3,019 → 1,114 | 0/3 | After 2/3 |
| Originating design reconstruction | 3,668 → 572 | 0/3 | After 2/3 |

Shorter ADAPTIVE answers lost material preservation, placement acceptance or
verification facts. The actual plugin case still added facades, registries,
codecs, enforcement and migrations without proving them necessary; unknown
formats were sometimes rejected. [Semantic review](plugin-design-review.md)
records failures beyond keyword checks. Original implementation correctness
and full conversation coverage were not established.

The experimental SKIP/DIRECT guidance estimates fell 54%/37%, but those
numbers include other withdrawn prompt changes and use the experiment's
older accounting version. Subsequent review also found and corrected false
loads from guidance-path mentions in search results; historical cost figures
are not re-certified by the current parser. A pure extraction of baseline
Alchemy sections 2–6 would save roughly 40% on SKIP before routing stubs,
below the saved 50% bar. Do not transfer the successful cost figures to a
different source or call the extraction independently proven.

## What to try next

Evaluate a format table and explicitly unverified free-format input through
existing authoring before decomposition. Every added mechanism must repair a
concrete obligation that candidate cannot satisfy. Preserve known validation,
trim, supported URI/QR, execution separation and the catalog-backed hero.
Then separately derive the compact report from a complete decision record,
checking decisive evidence and material gaps survive. Reconstruct cheap
Alchemy loading separately and replay ADAPTIVE as well as SKIP/DIRECT.

Keep every failed trial and the original acceptance bar. Preference is not
acceptance; three pairs cannot prove universal effectiveness. Full frozen
inputs and raw logs remain in the [evidence archive layout](../.refactor-evidence/README.md).
Nothing was published or repinned.
