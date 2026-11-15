# Requirement: billing-rule-isolation

Audience: the shop-api team. Purpose: the canonical statement of this
requirement. It records the problem and the scope; it decides no design.
Completed on 2026-11-09 with the product owner. Evidence:
[change history](../evidence/change-history.md), current for `main` at
`9c41e07`.

```text
Subject:        billing-rule-isolation
Mode:           standalone
Decision:       GROUNDED
Problem:        Confirmed. The developer on the weekly finance rota applies
                finance's billing rule change: a tax rate, a discount tier, or
                the invoice layout. To do it they edit `placeOrder`, which also
                validates and stores the order, because the rules are written
                inside that function.
Basis profile:  evidenced
Confidence:     high
Blocking gaps:  none
Outcome hypotheses: not applicable: the requirement claims nothing beyond its
                complete-when conditions, and the cost it removes is measured
                in the change history
Supersedes:     none
Next action:    decide whether it is worth building, then design it
Verification:   change history read on 2026-11-09; problem, done state, and
                not-problem confirmed by the product owner the same day
```

## Problem statement

Most weeks finance sends one billing rule change: a tax rate, a discount tier,
or the invoice layout. The developer on the finance rota applies it. Today that
means editing `placeOrder` in `src/orders/index.js`, the function that also
validates the order, sets its status, and stores it. A rule change therefore
carries the risk of an order lifecycle change.

## Done when

- A billing rule change edits no file that validates an order, stores it, or
  changes its status.
- `npm test` passes with no assertion changed: prices, discounts, tax, invoices,
  and order behaviour stay exactly as they are.

## Not-problem

Confirmed out of scope by the product owner:

- A separate service, deployable, or release cycle for billing. shop-api stays
  one process and one deployable.
- Any change to a price, a discount tier, a tax rule, rounding, or the invoice
  layout.
- Any change to how an order is stored or to what shipping reads.

## Requirement

```text
Requirement: billing-rule-isolation
Actor: developer on the weekly finance rota
Must be able to: apply a billing rule change without editing order lifecycle code
So that: a rule change cannot break placing, cancelling, or reading an order
Complete when:
- a change to a tax rate, a discount tier, or the invoice layout edits no file
  that validates an order, stores it, or changes its status
- `npm test` passes with no assertion changed
Basis: evidenced
Source or evidence: docs/evidence/change-history.md
Priority: should
Validation decision: accept
Confidence: high
```

## Evidence

From the change history, 26 weeks and 33 commits under `src/`:

- 24 commits are billing rule changes (`FIN` tickets), in 23 of the 26 weeks.
  All 24 edit `src/orders/index.js`.
- 3 of those 24 broke order lifecycle behaviour and needed a fix the next day
  (ORD-82, ORD-85, ORD-88).
- 4 commits change order lifecycle behaviour for its own reasons (`ORD`
  tickets). No commit carries both a `FIN` and an `ORD` ticket.

## Facts

- One team of four owns all of `src/`. The service is one deployable.
- Only `placeOrder` uses the billing rules. No other module and no client
  depends on how they are computed. The stored order keeps the resulting
  `invoice` object, and its shape is not changing.

## Decision log

| Date | Decision | Source | Supersedes |
| --- | --- | --- | --- |
| 2026-11-09 | Problem, done state, and not-problem confirmed | Product owner, with the team | none |
| 2026-11-09 | A separate billing service is out of scope | Product owner: one deployable, one team | none |
