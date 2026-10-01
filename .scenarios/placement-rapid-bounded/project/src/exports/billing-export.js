import { getOrderTotals } from "../orders/index.js";

export function runBillingExport(orderIds) {
  return orderIds.map((id) => getOrderTotals(id));
}
