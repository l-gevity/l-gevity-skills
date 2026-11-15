# Change history of `src/`, 2026-05-11 to 2026-11-08

Source: `git log --since=2026-05-11 --until=2026-11-08 --date=short --name-only --format="%h %ad %s" -- src/`,
run on 2026-11-09 on `main` at `9c41e07`.

Coverage: every commit that touched a file under `src/` in the 26 weeks. The
repository squash-merges, so one commit is one reviewed change and carries one
ticket. The ticket prefix names the reason for the change: `FIN` is a billing
rule change requested by finance, `ORD` is order lifecycle work, `SHP` is
shipping work.

Blind spots: the log names files, not lines, so a `FIN` and an `ORD` commit that
both edit `src/orders/index.js` are told apart by their ticket only. Files outside
`src/` are not listed.

| Commit | Date | Subject | Files under `src/` |
| --- | --- | --- | --- |
| `09815cb` | 2026-05-12 | FIN-201 invoice: label lines by sku instead of product name | `src/orders/index.js` |
| `e002fa0` | 2026-05-19 | FIN-202 discount: lower the 5% tier from 150.00 to 100.00 | `src/orders/index.js` |
| `1824f71` | 2026-05-21 | ORD-81 reject an order without lines | `src/orders/index.js` |
| `5ebc3c0` | 2026-05-27 | FIN-203 tax: FR rate from 19.6% to 20% | `src/orders/index.js` |
| `d61a780` | 2026-06-02 | FIN-204 discount: spring promotion, 10% tier from 400.00 | `src/orders/index.js` |
| `349ed55` | 2026-06-09 | FIN-205 invoice: show the discount as its own amount | `src/orders/index.js` |
| `06ff490` | 2026-06-10 | ORD-82 fix placeOrder storing orders without a status (regression from FIN-205) | `src/orders/index.js` |
| `e8016db` | 2026-06-16 | FIN-206 discount: end spring promotion, 10% tier back to 500.00 | `src/orders/index.js` |
| `4faf8ff` | 2026-06-23 | FIN-207 tax: DE temporary rate 16% | `src/orders/index.js` |
| `c19458c` | 2026-06-25 | SHP-31 label shows the line count | `src/shipping/index.js` |
| `7eb94c2` | 2026-06-30 | FIN-208 invoice: show tax as its own amount | `src/orders/index.js` |
| `4b25b22` | 2026-07-07 | FIN-209 tax: charge tax on the discounted amount | `src/orders/index.js` |
| `1589cee` | 2026-07-09 | ORD-84 add cancelOrder; save keeps the id of a stored order | `src/orders/index.js`, `src/orders/repository.js` |
| `8be9cce` | 2026-07-14 | FIN-210 discount: a tier applies above its threshold, not at it | `src/orders/index.js` |
| `c55079d` | 2026-07-21 | FIN-211 tax: round tax to the nearest cent | `src/orders/index.js` |
| `f1ea357` | 2026-08-04 | FIN-212 discount: summer promotion, 5% tier from 50.00 | `src/orders/index.js` |
| `1943ee1` | 2026-08-06 | FIN-213 invoice: amounts in cents, no formatted strings | `src/orders/index.js` |
| `5ad1b13` | 2026-08-07 | ORD-85 fix placeOrder returning the invoice instead of the order (regression from FIN-213) | `src/orders/index.js` |
| `c93be1d` | 2026-08-11 | FIN-214 tax: reject a country without a rate | `src/orders/index.js` |
| `cb32150` | 2026-08-18 | FIN-215 discount: end summer promotion, 5% tier back to 100.00 | `src/orders/index.js` |
| `0cb5bf9` | 2026-08-25 | FIN-216 tax: DE rate back to 19% | `src/orders/index.js` |
| `4378110` | 2026-08-27 | ORD-86 add getOrder; it rejects an unknown order | `src/orders/index.js` |
| `0966fd8` | 2026-09-01 | FIN-217 discount: round the discount to the nearest cent | `src/orders/index.js` |
| `9a4fdf6` | 2026-09-15 | FIN-218 invoice: the total includes tax | `src/orders/index.js` |
| `d879bca` | 2026-09-17 | SHP-33 read orders through getOrder | `src/shipping/index.js` |
| `1689b19` | 2026-09-22 | FIN-219 discount: autumn promotion, 10% tier from 450.00 | `src/orders/index.js` |
| `29520a7` | 2026-09-29 | FIN-220 invoice: one line per order line | `src/orders/index.js` |
| `640cb4d` | 2026-09-30 | ORD-88 fix orders stored without their lines (regression from FIN-220) | `src/orders/index.js` |
| `f75e98b` | 2026-10-06 | FIN-221 discount: end autumn promotion, 10% tier back to 500.00 | `src/orders/index.js` |
| `ee9f673` | 2026-10-08 | ORD-90 cancelOrder rejects an order that is not placed | `src/orders/index.js` |
| `7951f1c` | 2026-10-20 | FIN-222 tax: FR temporary rate 19% | `src/orders/index.js` |
| `7ee4a9f` | 2026-10-27 | FIN-223 tax: FR rate back to 20% | `src/orders/index.js` |
| `d585a2f` | 2026-11-03 | FIN-224 invoice: name the line amount amountCents | `src/orders/index.js` |

## Totals

- 33 commits in 26 weeks; 31 of them edit `src/orders/index.js`.
- `FIN`: 24 commits, in 23 of the 26 weeks. Each edits `src/orders/index.js` and no
  other file under `src/`.
- `ORD`: 7 commits. Each edits `src/orders/index.js`; 1 also edits
  `src/orders/repository.js`. 3 of the 7 fix a regression that a `FIN`
  commit introduced (ORD-82, ORD-85, ORD-88).
- `SHP`: 2 commits. Each edits `src/shipping/index.js` only.
- No commit carries two tickets.
