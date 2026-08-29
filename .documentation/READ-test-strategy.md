# What Is a Test For?

The suite has 4,100 tests and 92% coverage. The dashboard is green. And
Saturday's outage — a currency-rounding error that quietly corrupted a
week of invoices — sailed through all of it, because not one of those
4,100 tests would have failed on a wrong amount. Hundreds of them
exercised the invoice code; they asserted that it *ran*, that results were
"not null," that mocks were called. Nothing asserted that the numbers were
*right*.

The suite was optimized for the wrong target: test count and coverage,
instead of the only thing a test is actually for — **evidence that a
specific failure is absent**. This document explains test strategy as a
question of evidence: which failures matter, what would prove their
absence, and what is the smallest set of checks that provides that proof.

## Start from the failure, not the test type

The unproductive way to plan testing starts from formats: "we need more
unit tests," "we should have E2E coverage," a pyramid poster with target
ratios. Formats are answers, and nobody has asked a question yet.

The productive way starts from **risk**: what can go wrong here, how bad
would it be, and how plausibly does it happen? "The proration calculation
can produce a wrong amount — every invoice affected, silently." "The
provider's API can change shape under us." "Concurrent edits can corrupt
an order." Each named failure mode is a question the test portfolio must
answer, and each points at its own most effective kind of check —
which is why a universal pyramid ratio can't be right: a system's correct
test shape is a function of *its* risks, not of geometry. Two honest rules
about scoring risk: impact and likelihood stay separate (a catastrophic
rarity and a trivial frequency both matter, differently), and **unknown
exposure is not low exposure** — "we don't know how often this happens"
is a finding, not reassurance.

## The oracle: the part of the test that is the test

Every real test has two halves: a way to *exercise* the system, and a way
to *tell right from wrong*. The second half is called the **oracle**, and
it is the half that gets skipped — because exercising code is easy and
mechanical, while defining correctness takes domain thought. The rule:

> **Before choosing any framework, level, or harness, state how correct
> and incorrect behavior will be distinguished.**

The 4,100-test suite failed Saturday precisely here. `assert result is
not null` has an oracle — "the code produces *something*" — that can't
distinguish a right invoice from a wrong one. A test's value is exactly
the discriminating power of its oracle, and a weak oracle is worse than a
missing test: the missing test leaves a visible gap; the hollow test
covers the gap with green paint. This is also the honest reading of
coverage: it **locates unexecuted code** — a genuinely useful gap-finder
— and says *nothing* about whether the executed code was checked against
anything. Coverage is a flashlight, not a verdict.

And when no credible oracle exists — nobody can yet say what "correct"
means for this behavior — the honest move is to say so and go get the
answer from the requirement's owner, not to write a test that asserts
whatever the code currently does. That test doesn't verify the behavior;
it *enshrines* it, bugs included.

## Describe tests by what they actually do

"Unit test" and "integration test" mean different things on every team,
and arguments about the labels are arguments about nothing. Five concrete
dimensions describe any test unambiguously: **what is under test**, which
**dependencies are exercised** (real ones, and which are replaced),
in what **environment**, with what **stimulus** (input, action, injected
fault), against what **oracle**. Two tests with the same label can differ
on every dimension; two tests that agree on all five are the same kind of
test whatever anyone calls them.

With that vocabulary, the scope rule is simple: **minimum sufficient
fidelity** — the smallest, fastest scope *that can faithfully observe the
named failure*. Both directions of error are real. Testing a pure
calculation through the full browser-to-database stack buys seconds of
runtime and layers of flakiness for zero extra discriminating power. But
testing "our queries work on the real database's semantics" against an
in-memory fake has *negative* value — it can't observe the named failure,
and its green result reassures falsely. The failure mode picks the scope;
neither speed preference nor thoroughness preference does.

## Test doubles: a decision, not a habit

Whether to use the real dependency or a stand-in follows from the same
question — *what failure is this test hunting?* — and compresses into a
short ladder:

- **Real collaborators** when they're deterministic, fast, and yours —
  replacing your own pure logic with a mock of itself tests nothing but
  the mock.
- **Stub** the slow, nondeterministic, or destructive things when the
  test targets local decision logic — the stub is scaffolding, not the
  subject.
- **Mock** (assert on the interaction itself) only when the interaction
  *is* the requirement — "we must call the audit log before committing."
  Otherwise mock-verification welds tests to implementation details and
  makes every refactor a test-fixing chore.
- **Go real** when the risk *is* compatibility — the wire, the database's
  actual semantics, the provider's behavior. No double can testify about
  a boundary it only imitates.

And one rule guards the whole ladder: **every double that stands in for an
external boundary is a claim about that boundary, and claims drift.** The
provider changes a field; your stub keeps the old shape; every test
passes; production breaks. Each such double needs a backstop — a shared
schema, an executable contract test, or a periodic real-boundary check —
that fails when the claim goes stale.

## Trustworthiness is part of validity

A flaky test — passing or failing on rerun without code changes — is not
an unreliable helper; it is **invalid evidence**. Its failures stop
meaning "defect" (people re-run and move on), which means its passes stop
meaning anything either, and the reflex it trains — *re-run until green*
— eventually swallows a real failure. Order dependence, uncontrolled
time, shared state, and environment leakage are the usual causes, and
they are test *defects* to fix, not weather. Quarantining a flaky test is
legitimate triage, with a condition: an owner, a reason, and an expiry —
and a quarantined test counts as *no evidence* until it returns.

The portfolio itself needs the same skepticism, and it has a built-in
teacher: **every escaped defect is the answer key**. Each bug that
reached production names precisely the risk, oracle, or fidelity decision
the portfolio got wrong — the cheapest strategy review you will ever get,
if it's actually held. The other standing audit is subtraction: tests
whose oracle checks nothing, broader tests fully duplicated by smaller
ones, expensive suites retained because they were expensive to build.
A test that provides no distinct evidence costs runtime and maintenance
forever and pays nothing.

## Keep the unknowns visible

The end state of a test strategy is not "everything is covered" — nothing
real is ever everything-covered. It is: **every material risk has either
credible evidence or a visible, owned gap.** "Recovery from a mid-batch
crash: untested — no environment can inject the fault yet; accepted until
Q3" is a professional statement. The same gap, silently absent from any
list, is a false claim of safety made by omission. Green dashboards are
only as honest as the list of things they don't check.

---

*Related concepts: [shift-left](READ-defect-shift-left.md) decides *where*
each chosen check runs — this concept decides *what evidence* is needed at
all; [reliable pipelines](READ-ci-cd-reliability-architecture.md) owns the
gates that execute the portfolio;
[traceability](READ-requirements-traceability.md) tracks which criteria the
executed evidence actually verifies. The full operational reference — the
risk ledger, technique selection, portfolio governance, and decision rules
— lives in [SKILL.md](../.claude/skills/test-strategy/SKILL.md).*
