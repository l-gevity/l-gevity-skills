# Isolated refactor results

The accepted baseline was `3df41af`, with the frozen criteria in
`.documentation/refactor-replay-criteria.md`. The current working tree was
clean before the experiments. The rejected v6 source hash remains
`5cac1e7de382a3ef8454bfb21952684bac6c9b4ac59dacb9e87574b5d076e864` and is
not used as evidence for these candidates.

The evidence ZIP was hash-verified before recovery. The reduced plugin fixture
and the original-context reconstruction were copied unchanged into the review
harness at `C:/Users/Patrick/Projects/l-gevity/l-gevity-skills-review-20261001`.
Requests, criteria, rubrics, and fixtures were frozen by the maintained runner.

The infrastructure change in this worktree adds `--decision-records` to the
paired runner. It gives both arms a bounded `.decision-record.md` sink,
rechecks product and guidance hashes, preserves the record and SHA-256 beside
raw traces including interruption, and supplies anonymized record text to the
blind judge. The live disposable probe created the sink and left a protected
file unchanged. The maintained checks pass: skill validation, 52 deliberate
validator mutations, 29 replay tests, 252 Bash installer checks, and 504
PowerShell installer checks across both hosts.

Behavioral results remain separate:

- `extraction-v1` preserved completed SKIP and DIRECT checks but reduced SKIP
  guidance from 5,016 to 3,087 words (38.5%), below the unchanged 50% bar.
- `extraction-v2` only corrected the required operating-guide filename. Its
  completed SKIP and DIRECT checks still do not establish the incomplete
  ADAPTIVE set; ADAPTIVE reports exceeded 350 words.
- `routing-v1` completed SKIP pairs at 2,475 versus 5,016 words (50.7%) and
  passed those SKIP checks, but its completed DIRECT and ADAPTIVE reports
  exceeded 350 words and its full set was interrupted. It is not promoted.
- `compact-v2` completed all three DIRECT and retry pairs with candidate
  reports at or below 306 words, and its explicit detailed-report recording
  passed all six detail checks. Its ADAPTIVE set was incomplete; one candidate
  run was 320 words but did not load the operating guide because this was a
  compact-only candidate. The default report experiment therefore remains
  unaccepted until a combined candidate passes all six scenarios.
- `minimal-v1` failed the reduced and original plugin obligations: reports
  exceeded 350 words, the reduced case omitted the free-format path, and the
  original case introduced unsupported components. `minimal-v2` was started
  with an explicit unverified fallback rule but was interrupted before a
  completed pair; no claim is made for it.

Every failed or interrupted artifact remains under the review harness's
`trials/` and `*.logs/` directories. No behavioral guidance candidate was
copied into the canonical `.agents` or `.claude` trees, no consumer was
repinned, and no commit or publication was made.
