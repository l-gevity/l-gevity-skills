# Paired before/after replay

A changed decision rule remains a hypothesis until it is compared against the
same scenario on both skill sources. A transcript recorded only against current
text does not establish an improvement.

Record the originating miss as a scenario with its request, fixture, skills,
and predeclared pass/fail criteria. Include a blind-judge rubric when human
judgment is needed. Then run:

```sh
python scripts/replay-scenarios.py <scenario> \
  --before <ref-or-path> --after <ref-or-path> --runs 3 --blind-judge
```

The harness freezes both sources, the request, fixture, criteria and checker
before calling a model. It gives both arms fresh projects, randomizes arm order,
records criteria and report length per run, and conceals the arm mapping from
the judge. The isolated judge has no source files, tools, user instructions or
assignment key; it sees A/B reports, the rubric and shared product context.

Artifacts under `.scenarios/<scenario>/replays/` checkpoint every arm and
completed pair atomically. `.inputs` retains source snapshots and file hashes;
`.logs` retains raw traces and anonymous judge packets. Resume an interrupted
trial with `python scripts/replay-scenarios.py --resume <artifact.json>`;
completed arms are reused and changed working files cannot alter frozen inputs.
Keep failed trials. A runner execution succeeding is not behavioral acceptance.

Loaded-guidance cost counts unique root, SKILL.md bodies and reference files
loaded through Skill, Read, or successful content search. Partial reads charge the whole file; discovery
metadata and system prompts are excluded. These are word estimates, never
token-usage measurements. Use `python scripts/test-replay-scenarios.py` to
check persistence, source freezing, accounting and judge isolation without
calling a model.

Promote the candidate only when the target failure improves without a worse
verdict or any unmet required criterion. For a brevity change, compare report
length alongside verdict and content checks; shorter output alone is not
success. Apply the candidate rule to the current change itself before calling
it ready.
