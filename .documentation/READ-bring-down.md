# Bring-Down: Every Line You Write Is a Line You Maintain

Somewhere in your codebase there is a file called something like
`retryUtils.ts`. It was written in an afternoon, four years ago, because
"pulling in a whole library for this felt like overkill." It has exponential
backoff, sort of. It has jitter, added after the thundering-herd incident. It
has a subtle bug where a timeout during the final retry surfaces as success,
which nobody has found yet. Three services depend on it, each on a
slightly different copied version.

Meanwhile, the maintained library that does exactly this — battle-tested by
thousands of teams, edge cases documented, bug fixed in 2019 — was one
dependency away the whole time.

This document explains bring-down: the idea that code is a liability rather
than an asset, that every capability has a *lowest responsible level* at which
it can be maintained, and that moving commodity code down to that level —
into frameworks, libraries, standards, platforms, and managed services — is
how you keep a codebase small enough to understand.

## Code is a liability

The instinct that writing code is *producing* something is subtly wrong. The
capability is the asset — "requests retry safely" is worth something. The
code is the *cost* of that asset: every line must be read by new teammates,
kept compatible through upgrades, secured, tested, and debugged at 2am. That
cost recurs for as long as the line exists, and it's paid by whoever owns
the line.

Which makes the interesting question about any piece of code not *"does it
work?"* but *"who maintains it?"* — and, right behind it: *"who **should**?"*
When your team hand-rolls retry logic, your team pays its maintenance forever.
When the code comes from a maintained library, thousands of teams share the
cost, and specialists whose whole job is retry semantics pay most of it. Same
capability, radically different bill.

## The altitude scale

For any capability, there's a scale of possible maintainers, from "us,
bespoke" at the top to "someone else entirely" at the bottom:

| Level | Who maintains the capability | Example: authentication |
| ----- | ---------------------------- | ----------------------- |
| **L4 — Custom code** | Your team, in this codebase | Hand-rolled session handling and password hashing |
| **L3 — Library / framework** | The library's maintainers; you consume an API | The framework's built-in auth module |
| **L2 — Standard path** | An external standard or convention; you follow it | OpenID Connect, rather than an invented login protocol |
| **L1 — Internal platform** | A platform team in your org; you consume their product | The company SSO gateway every app plugs into |
| **L0 — Managed service** | An external provider; you keep only integration code | Auth0, Cognito, Entra ID |

"Bringing down" a capability means moving it toward the bottom: replacing
your bespoke implementation with something maintained further away from you —
and then, crucially, **deleting the bespoke version**.

One clarification, because the word "down" collides with another mental
image: this is not about your architecture's layers. Moving code from a
controller into a repository class doesn't change who maintains it — it's the
same team, one directory over. "Down" here means *less bespoke, more shared*:
the maintenance genuinely changes hands. If the new owner is still your team,
you've refactored (perhaps usefully!), but you haven't brought anything down.

## Commodity versus differentiation

If lower levels are cheaper, why not bring everything down to a managed
service? Because the scale has a floor, and the floor is different for every
capability. The dividing question:

> **Does this code make our product different, or does it make our product
> the same as every other product?**

Your pricing engine, your matching algorithm, the domain rules that encode
ten years of hard-won business knowledge — that's *differentiating* code. It
has no lower home, because nobody else does what it does. It belongs at L4,
written and owned by you, and it deserves the bulk of your attention.

Retry logic, date arithmetic, PDF generation, sending email, cron parsing,
password hashing, object storage — that's *commodity*. Every product needs
it; doing it identically to everyone else is correct; doing it *differently*
from everyone else is, at best, a quirk and, at worst (password hashing), a
vulnerability. Commodity capability kept at L4 is pure liability: you're
paying bespoke prices for a product available wholesale.

The scale's real instruction is therefore not "go as low as possible" but:
**find the lowest *responsible* level.** Differentiating logic stays high.
Commodity sinks. And a capability can split — the stable commodity core goes
down, while the genuinely product-specific 10% stays local and explicit.

## The traps

Bring-down has failure modes, and they're worth knowing before the first
enthusiastic migration:

**Forcing an abstraction over real variation.** Three services have similar
looking export code, so someone builds `SharedExporter` to unify them. But
the similarity was superficial — one needs streaming, one needs retries, one
needs a different encoding — and `SharedExporter` sprouts seven boolean
parameters trying to serve everyone, becoming harder to maintain than the
three copies were. Repetition makes a capability a *candidate* for bringing
down; it's only a *fit* if the copies genuinely want to be the same thing.
Three copies that solve different problems are three capabilities wearing the
same coat.

**Platformizing uncertainty.** Building a shared platform for a pattern
you've seen once or twice locks in guesses. A premature abstraction with many
consumers multiplies the cost of every wrong guess by the number of
consumers. Bring down what has *stabilized*; let the still-evolving stay
local and cheap to change.

**The wrapper habit.** "We wrapped the library so we can swap it out later"
produces a bespoke L4 layer around an L3 capability — the maintenance you
were trying to shed, reintroduced as insulation against an event (swapping
the library) that rarely happens. A wrapper earns its existence only when it
enforces a real policy of yours (limits, auditing, safe defaults). A wrapper
that just renames the library's methods is negative-value code.

**Migration without deletion.** The library is adopted, the announcement is
made — and the old hand-rolled version still has callers a year later. Now
there are *two* retry mechanisms: the liability went up, not down. A
bring-down is finished when the custom code is deleted, not when its
replacement is installed. Until then you haven't simplified; you've added
inventory.

**Outsourcing your crown jewels.** The mirror image of hoarding commodity:
pushing differentiating logic into a vendor's opinionated service, then
spending years fighting the vendor's model of your domain. The scale's floor
exists for a reason.

## Look in your own stack first

The reflex when custom code smells like commodity is to search for a new
library or evaluate vendors. But the cheapest landing is almost always closer
to home, so the search runs inward-out:

1. **The framework you already use.** Modern frameworks quietly ship
   validation, scheduling, caching, retries, pagination. A surprising amount
   of bespoke code re-implements a feature of a dependency already in the
   lockfile.
2. **Libraries and services your org already approved.** Adopted, understood,
   security-reviewed — no new supply-chain decision needed.
3. **Your org's internal platforms.** The deploy workflow or logging pipeline
   another team already operates.
4. **Only then, the market** — with current evidence, not folklore: is the
   candidate maintained *now*, is the license compatible, does it actually
   cover your cases, what does migration and (importantly) *rollback* look
   like? A library that was the obvious choice five years ago may be
   abandoned today, and popularity is not fitness — stars measure fame, not
   whether it handles your edge cases.

And a step zero that outranks them all: **check whether the capability needs
to exist.** The best bring-down is discovering the custom code solves a
problem nobody has anymore, and deleting it with no replacement at all.

## The habit

The concept compresses to a question you can ask of any file you're about to
maintain, extend, or debug: *is this our business, or is this everybody's
business?* If it's everybody's business — if this code makes your product the
same as every other product — then somewhere below there is a framework
feature, a library, a standard, a platform, or a service whose entire job is
to maintain it, better than you can afford to.

The signals are recognizable: "we have our own X" said slightly defensively;
the same helper copy-pasted across repos with small mutations; the module
everyone is afraid to touch that does something a lockfile dependency already
does; the infrastructure your team babysits that a cloud provider offers as
three lines of configuration. Each is commodity code living above its
station — paying bespoke prices, wholesale product.

---

*Bring-down is one of three related "move it along the axis" ideas:
[shift-left](READ-defect-shift-left.md) moves defect detection earlier in
time, [push-out](READ-push-out.md) moves recurring operational work out of
human hands into durable systems, and bring-down moves bespoke code down into
maintained, reusable capability. The full operational reference for this
concept — the complete scale, outsourcing triggers, and survey protocols —
lives in [SKILL.md](../.claude/skills/bring-down/SKILL.md).*
