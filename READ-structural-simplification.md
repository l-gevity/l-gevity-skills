# Structural Simplification — In-Depth Explanation

> **The core claim:** "Simpler" is the most overused and least falsifiable word
> in software engineering. Every refactor claims to simplify. Most refactors
> merely relocate complexity from one place to another. Without a measurable,
> multi-axis definition of complexity, any change can be argued either way — and
> the loudest voice wins. This skill makes complexity measurable, comparable,
> and honest.

---

## 1. Why "Simpler" Fails as an Argument

When two engineers disagree about whether a refactor simplifies a system, they
almost always turn out to be measuring different things. One says "this is
simpler — there are fewer files." The other says "this is more complex — the
dependency chain is longer." They are both right. They are talking about
different axes of complexity, but using the same word.

This is why simplification debates go in circles. The word "simpler" presupposes
a single measurable thing. There isn't one. Complexity is not a scalar — it is
at least a four-dimensional vector. Without separating the dimensions, every
claim about simplification is unfalsifiable: someone can always point to the
axis that improved and ignore the ones that worsened, and someone else can do
the opposite.

This skill exists to end that argument. By forcing every restructuring to
declare its effect on **each axis separately**, it converts a vague rhetorical
claim into a measurable, comparable proposition.

---

## 2. The Single-Number Trap

The temptation when measuring complexity is to collapse everything into a single
score — cyclomatic complexity, lines of code, file count, or some weighted
composite. This always fails, for two reasons.

**First, the axes correlate but are not identical.** More parts (n) usually
means more diversity (D) and more depth (P). But the correlation is imperfect.
You can have many parts with low diversity (a uniform array) or few parts with
high diversity (a small but heterogeneous mess). A composite score double-counts
the shared variance and obscures the independent variation that matters.

**Second, the trade-offs are real.** Most architectural moves _raise_ one axis
to _lower_ another. Adding an abstraction layer reduces coupling but increases
depth and quantity. Flattening two layers reduces depth but raises coupling.
Extracting a common part reduces diversity and coupling but adds quantity. A
composite score erases these trade-offs by averaging — which is exactly the
information you need to preserve.

The four axes must be tracked separately. Their interaction _is_ the design
problem.

---

## 3. The Four Axes

Each axis answers a distinct question about a structure:

**Diversity (D) — How many different shapes are there?** The number of distinct
patterns, conventions, or kinds of thing in the vocabulary of the structure. Two
ways of doing the same task is D=2; one way is D=1. A codebase with seven naming
conventions, three competing error-handling patterns, and a handful of bespoke
modules has high D. Diversity is the cost of _learning the system_ — every
unique shape is one more thing a reader must understand from scratch.

**Coupling (K) — How densely are the parts connected?** The ratio of actual
relationships to possible relationships: edges divided by n×(n−1). High K means
changing one part forces changes in many others. Low K means parts can be
modified, replaced, or reasoned about in isolation. Coupling is the cost of
_changing the system_ — every relationship is a path along which a change can
propagate.

**Depth (P) — How long is the longest chain?** The maximum path from any source
to any sink. Depth determines how many components a request, signal, or change
has to traverse. Depth is the cost of _tracing the system_ — every level adds
latency, indirection, and opportunities for misunderstanding.

**Quantity (n) — How many parts are there?** The total number of discrete units.
n is the simplest axis but the easiest to underestimate. Adding parts is cheap
locally but expensive globally — every new part is a candidate for new coupling,
new diversity, new depth. Quantity is the cost of _holding the system in mind_.

The four axes correspond to four irreducibly different costs: **learning,
changing, tracing, and holding**. A system can be cheap on some axes and
expensive on others. The job of architecture is to manage the _vector_, not
minimize a scalar.

---

## 4. Why Independence Matters

The axes are conceptually independent — moving along one does not determine
motion along the others — even though they correlate in practice. Independence
is what makes per-axis comparison rigorous.

Consider three refactorings of the same starting point:

- **Extract a helper used three times.** D↓ (one fewer pattern shape), K↓ (three
  direct dependencies become one shared dependency), P— (no new layer), n↑ (one
  new function). Net: probably better.
- **Wrap a service in a facade.** D↑ (a new interface kind), K— (same actual
  coupling), P↑ (one more hop on every call), n↑ (one more part). Net: probably
  worse — and crucially, the facade _hides_ P without reducing it.
- **Replace three error-handling styles with one.** D↓ (substantial), K—, P—, n—
  (or slight ↓ if shared utility consolidates). Net: clearly better, with no
  compensating cost.

A single-number metric would produce one verdict for all three. The four-axis
vector produces three different verdicts — and explains _why_. The verdicts are
not just outputs; they are diagnostic. They tell you _which axis_ you bought
improvement on and _which_ you paid for it on.

---

## 5. The Trade-Off Principle

Most architectural moves are not pure wins — they shift complexity along the
axis-vector. The skill's trade-off matrix exists because this is the rule, not
the exception.

Three patterns recur:

- **Reducing K usually raises P or n.** Decoupling means inserting indirection,
  extracting interfaces, or splitting things. Each of those adds depth or
  quantity.
- **Reducing P usually raises K or D.** Flattening layers means the parts that
  were buffered by the layer now talk to each other directly — coupling rises.
  Or the merged parts grow in shape diversity.
- **Reducing n usually raises K or P internally.** Merging two parts into one
  means whatever they used to do across a boundary now happens inside a larger
  thing — internal complexity rises.

The trade-off principle has a corollary: **moves that improve one axis without
degrading any other are rare and precious**. When you find one, take it. They
are typically deletions: removing a feature, eliminating a special case,
dropping an unused abstraction. Pure deletions are the only changes that improve
every axis simultaneously, which is why "delete over mitigate" is the most
powerful directive in the skill.

---

## 6. The Reduction Toolkit

The skill organizes simplification operations by which axis they target. This
organization matters because it forces you to know _what you are buying_.

**To reduce diversity (D↓)** — unify, normalize, generalize, abstract,
symmetrize, deduplicate, patternize. All of these collapse multiple shapes into
one canonical shape. They reduce the vocabulary of the system.

**To reduce coupling (K↓)** — encapsulate, indirect, invert, stratify, cohere,
temporally decouple, eliminate edges. All of these reduce the density or
directness of relationships. The most underrated of these is _cohesion_: when
you group what changes together, the external links to the group sever
automatically — coupling reduction as a side effect of cohesion increase.

**To reduce depth (P↓)** — flatten, inline, direct-bind. All of these shorten
chains. The crucial warning here is that a _facade_ hides depth without reducing
it — the chain still exists, you just can't see it. The skill is explicit:
verify actual P, not visible P.

**To reduce quantity (n↓)** — eliminate, merge. Of these, elimination is the
strongest move available in the entire toolkit. Removing a part doesn't just
drop n; it drops absolute coupling as K×n² (every potential edge to that part
disappears). One deletion can have outsized global effect.

**Multi-axis operations** — decomposition, factoring, separation of concerns.
These are the rare moves that reduce multiple axes at once, by partitioning the
structure along a natural seam where the axes align with the partition boundary.

The toolkit is not a menu of techniques. It is a map of _which lever moves which
dial_. When you reach for a tool, you should know the axis it targets and the
axis it likely costs.

---

## 7. Asymmetric Trades: Conform, Delete, Atomicity

Three asymmetric moves are powerful enough to deserve their own treatment.

**Conform over customize.** When a system has nine uniform components and one
snowflake, the snowflake inflates D disproportionately — it is the reason
readers have to learn an extra pattern. Forcing the snowflake into the existing
shape may produce _locally suboptimal_ code: the snowflake now does things the
standard way, even if a custom way would be marginally better. But globally, D
drops, the vocabulary shrinks, and every future reader benefits. Local
optimization is a trap; global uniformity is the win.

**Delete over mitigate.** Special cases are complexity multipliers. A single
edge case forces unique patterns (D↑), conditional paths (K↑), extended chains
(P↑), and supporting parts (n↑). The cost of a feature is rarely the feature
itself — it is every special case the feature forces elsewhere in the system.
When the feature is unloved or rarely used, the math almost always favours
removal. The most powerful simplification move is the one that removes the
source of complexity rather than handling it.

**Atomicity decision.** When an operation spans multiple systems, the atomicity
choice has direct structural cost. Atomicity raises K and P (the parts must
coordinate, the chain extends). Eventual consistency lowers K and P (the parts
proceed independently) but transfers complexity to compensation logic and
partial-failure documentation. The mistake is implementing the operation
_without making this choice consciously_ — at which point the structural cost
lands somewhere accidental and uncontrolled.

These three trades are special because they all violate naive
"minimize-everywhere" intuition. Each accepts a local cost — overengineering one
component, removing useful functionality, accepting eventual rather than perfect
consistency — to win a larger global gain.

---

## 8. The Decision Protocol: Measurement as Discipline

The protocol is the heart of the skill. It is deliberately mechanical:

1. Model the structure before the change. Record (D₁, K₁, P₁, n₁).
2. Model the structure after the change. Record (D₂, K₂, P₂, n₂).
3. Compute the deltas.
4. Classify the result:
    - All axes improve or hold → proceed.
    - Mixed → consult the trade-off matrix, apply asymmetric reasoning if it
      applies.
    - No axis improves while any worsens → reject or redesign.

The mechanical nature is the point. Without the protocol, "this is simpler" is a
feeling — and feelings are reliably partisan. With the protocol, "this is
simpler" becomes a claim with a structure: it asserts specific values for ΔD,
ΔK, ΔP, and Δn, and it can be challenged on any of them. The conversation moves
from "I think this is cleaner" to "you reduced K by 0.3 but raised P from 4 to 6
and added two parts — what was the net intent?"

This is the same shift that made other engineering disciplines mature: from
intuition to instrumentation. You cannot improve what you do not measure. And in
architecture, the thing to measure is not a scalar — it is the four-axis vector
of structural complexity.

---

## 9. Summary: What the Four-Axis Model Gives You

| Property                        | Without four-axis model               | With four-axis model                      |
| ------------------------------- | ------------------------------------- | ----------------------------------------- |
| **"Simpler" claims**            | Unfalsifiable, partisan               | Specific deltas, debatable on the data    |
| **Trade-off recognition**       | Hidden behind "cleaner" rhetoric      | Explicit per-axis costs and gains         |
| **Hidden complexity (facades)** | Invisible — looks like simplification | Caught — actual P doesn't drop            |
| **Refactor evaluation**         | Intuition-driven, individual taste    | Mechanical protocol with clear verdict    |
| **Architectural debate**        | Loudest voice wins                    | Vector comparison, evidence-based         |
| **Special-case cost**           | Localized to the case itself          | Multiplied across every axis it touches   |
| **Snowflake components**        | Tolerated locally                     | Identified as global D-inflators          |
| **Pure wins (deletions)**       | Indistinguishable from trade-offs     | Clearly visible as four-axis improvements |
| **Discipline required**         | High — relies on judgment alone       | Low — protocol does the heavy lifting     |

The model does not make architecture easier. It makes architecture _measurable_.
The hard part — knowing where to cut, which axis to spend, what to delete —
remains. But the conversation about whether a change is genuinely a
simplification stops being a matter of opinion. It becomes a matter of
arithmetic on a four-dimensional vector.

That is the entire claim of the skill: **complexity has four dimensions, and any
architectural decision that does not respect all four is gambling.**
