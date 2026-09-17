const orders = new Map();
let sequence = 1;

export function save(order) {
  order.id = order.id ?? sequence++;
  orders.set(order.id, order);
  return order;
}

export function load(id) {
  return orders.get(id);
}
