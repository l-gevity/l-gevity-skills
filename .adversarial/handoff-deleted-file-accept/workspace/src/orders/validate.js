export function validateOrder(order) {
  return Number.isInteger(order.total) && order.total >= 0;
}
