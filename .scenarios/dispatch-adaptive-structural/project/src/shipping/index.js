import { getOrder } from "../orders/index.js";

export function labelFor(orderId) {
  const order = getOrder(orderId);
  return { orderId, address: order.customer.address, lineCount: order.lines.length };
}
