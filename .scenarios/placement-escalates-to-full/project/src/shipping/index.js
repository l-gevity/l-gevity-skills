import { load } from "../orders/repository.js";

export function labelFor(orderId) {
  const order = load(orderId);
  return { orderId, address: order.customer.address, weight: order.lines.length };
}
