# Is This Worth Building? Is It Worth Keeping?

Two code reviews, same week.

In the first, someone proposes a configuration system so future teams can
swap the PDF engine — "we might need it." In the second, you find a retry
loop wrapped around a function call *in the same process* — it can't fail
transiently; there's nothing to retry. Both pieces of code are well-written.
Both pass tests. And both fail a question that code review rarely asks:

> **Does this functionality solve a real problem, and is it worth what it
> costs?**

Every feature, guard, abstraction, and flag is a purchase. Something is
bought (a capability) and something is paid (complexity, maintenance, risk
— forever). This document explains how to evaluate that purchase honestly —
before building, and retroactively, for everything already in the codebase.

![Functionality Pruner](functionality_pruner.svg)

## First question: can the problem even occur here?

Before asking whether functionality is worth its cost, ask something more
basic: **does the problem it solves actually exist in this system?** A
surprising amount of code fails this test — it guards against things that
*cannot happen*, and it clusters into recognizable species:

- **Impossible-state guards.** A null check on a value the type system
  guarantees is never null. A client/server version-mismatch check in an
  app deployed as a single artifact — client and server *can't* be at
  different versions. A mutex in a single-threaded runtime.
- **Already defended elsewhere.** Hand-rolled XSS escaping on top of a
  template engine that already escapes everything. A CSRF token on a
  read-only GET. The concern is real — but another layer owns it, and this
  copy is a rumor of a defense, not a defense.
- **Cargo-culted patterns.** A connection pool in a CLI that exits in 200
  milliseconds. A singleton in a stateless function. The pattern is fine
  where its prerequisites hold; here, they don't.
- **Phantom requirements.** The feature flag for a launch that completed
  two years ago. The migration shim after every record has provably
  migrated. The requirement was real once; the world moved on.
- **Generality nobody asked for.** The plugin interface with one plugin.
  The strategy pattern with one strategy. The config key that has held the
  same value in every environment since it was born.

The highest-yield way to find these is the **invariant audit**: list what
the architecture already guarantees — the type system's promises, the
deployment topology, what the framework enforces, what upstream middleware
ensures — then walk the code's branches with that list in hand. Any branch
that contradicts a guarantee is dead. A useful companion test: *construct
one concrete, real-world sequence of events that reaches this code.* If
you genuinely can't, you've found something.

The verdict for such code isn't "low value" — it's **obsolete**, and the
distinction matters for how permanently the question closes. "We removed
it because it wasn't worth the cost" invites relitigation whenever
priorities shift. "We removed it because client/server skew cannot occur
in a single-artifact deploy" closes the case until the architecture itself
changes.

Two honest caveats before deleting. Some "impossible-state" code is
*documenting* an invariant rather than enforcing one — an assertion whose
job is to fail loudly if a future contributor changes the topology. That
has real (small) value; convert it to a comment, a build-time check, or a
test rather than silently deleting the only record of the invariant. And
some code that *looks* cargo-culted is load-bearing — the complex version
exists because the simple one was measured too slow or too fragile. Read
the original commit or decision record before concluding; the difference
between "obsolete" and "load-bearing but quiet" is whether the original
rationale's premises still hold.

## Second question: the two-sided ledger

For functionality that passes the necessity test, the evaluation becomes a
ledger with two sides — scored separately, never collapsed into one number,
because a real trade-off is only visible while both sides are visible.

**Value** is what the functionality delivers, and it has four honest
components: how *severe* the need is (what actually breaks without it), how
*often* it arises, how *many* users or flows encounter it, and how *costly
the alternative* is (a decent workaround slashes value; no alternative
multiplies it). These multiply rather than add — which is the sharp edge: a
feature loved by 2% of users, needed yearly, with a one-line workaround,
has near-zero value *no matter how elegantly it's built*. The
most-inflated inputs in any proposal are reach and frequency; demand
evidence — tickets, telemetry, observed workarounds — not adjectives.

**Cost** is what the functionality imposes, and almost all of it is
invisible in the initial diff: the structural footprint (new concepts, new
dependencies, longer chains — the codebase is now harder to hold in one's
head), the maintenance tax (tests, docs, reviews, dependency updates,
every future refactor touching this too), the risk surface (more code, more
bugs, more blast radius), and — the most underestimated — the **evolution
tax**: the degree to which this constrains future change. It surfaces
later, as the PR that "should have been small but touched twelve files."

And the two sides age differently: **value is realized per use, but cost
accrues on every future change whether the feature is used or not.** A
feature used daily amortizes beautifully; one used quarterly is paying rent
on every sprint. Most production code is long-lived — evaluate over the
lifetime, not the demo.

## The default is no

With the ledger in view, the decision rule is deliberately asymmetric: **if
worth is not clearly positive, don't build it** — or build the smallest
slice that captures most of the value. This is YAGNI, but with its
reasoning attached: it isn't pessimism about ideas; it's arithmetic about
asymmetry. Not building costs almost nothing and is reversible the moment
real evidence arrives. Building speculatively costs the full ledger,
forever, on a guess — and speculative generality usually guesses the *wrong*
flexibility anyway, so when the real requirement lands you pay to remove
the old abstraction first.

The bar rises further for **one-way doors**: public APIs, persisted
schemas, wire formats — anything hard to remove once shipped. Reversible
choices can be made quickly on thin evidence; irreversible ones demand
stronger value and higher confidence.

The same asymmetry, run backwards, applies to existing code: **a feature
that would be rejected as a proposal today should not survive as code
today** merely because it exists. Sunk cost is not value. The most
empirically damning signal in a retrospective audit is **churn ×
complexity**: files that change *often* and are *complicated* are where
maintenance money actually goes, and they're disproportionately where the
bugs live. High churn dominated by fixes rather than improvements is a
ledger running in the red.

One caution in the deletion direction: "no telemetry hits" can mean
*unused* — or it can mean *you aren't measuring*. Deleting a feature
because you can't see it being used is survivorship bias in reverse.
Instrument first, decide later; structural impossibility (the necessity
test) is the only finding that licenses removal without usage data.

## The legitimate exceptions

Four cases where the raw ledger misleads, worth knowing by name:

- **Compliance, accessibility, and safety floors.** Audit logs, legal
  holds, accessible paths — their value doesn't show up in usage metrics
  and isn't optional. Priced by the obligation, not the click-through
  rate; kept even when "unused," provided the actual obligation is
  identified rather than assumed.
- **Named optionality.** Keeping something because it makes a *specific,
  probable* next feature cheap is a real argument. "Might be useful
  someday" is not — that's the plugin-with-one-plugin again.
- **Keystone cost.** Some locally-expensive code is the seam holding a
  correct abstraction together; deleting it makes the *system* more
  complex. Measure globally before celebrating a local win.
- **Measured performance and safety.** Complexity backed by a benchmark or
  an incident is load-bearing. The tell is a rationale whose premises still
  hold.

## The habit

The discipline compresses into a short interrogation, applicable to a
ticket, a PR, or a ten-year-old module: *Can the problem this solves
actually occur here — can I construct the sequence that triggers it? Who
specifically needs it, and what do they do today without it? What's the
smallest slice that captures most of the value? What does this cost per
future change, not per demo? And if it vanished in twelve months, what's
the realistic worst outcome?*

Beware, finally, of the three words that end more of these conversations
than they should: *clever*, *elegant*, and *defensive*. Cleverness is a
cost wearing a compliment; "defensive, just in case" is the necessity test
being waved off. The kindest thing you can say about code is not that it's
interesting — it's that it earns its keep.

---

*Related concepts:
[structural simplification](READ-structural-simplification.md) supplies the
complexity measurement for the cost side of the ledger;
[bring-down](READ-bring-down.md) asks the follow-up question for code that
passes — even if it's worth having, should *you* be the one maintaining it?
The full operational reference for this concept — detection heuristics,
scoring axes, the worth matrix, and verdicts — lives in
[SKILL.md](../.claude/skills/functionality-complexity-tradeoff/SKILL.md).*
