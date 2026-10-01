const orders = new Map();

export function findOrder(id) {
  return orders.get(id);
}

export function saveOrder(order) {
  orders.set(order.id, order);
}
