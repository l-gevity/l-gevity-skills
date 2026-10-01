import { findOrder } from "./repository.js";

export function getOrderTotals(orderId) {
  const order = findOrder(orderId);
  const subtotal = order.lines.reduce((sum, line) => sum + line.amount, 0);
  const tax = Math.round(subtotal * 0.21);
  return { orderId, subtotal, tax, total: subtotal + tax };
}
