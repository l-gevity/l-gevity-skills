# Capacity

| Table       | Rows today | Growth          |
|-------------|------------|-----------------|
| orders      | 40 M       | +2 M per month  |
| order_items | 240 M      | ~6 per order    |
| events      | 900 M      | +60 M per month |

The largest customer has 60 000 orders. Staging holds 10 000 orders in total.

Order history must answer within 300 ms at p95.
