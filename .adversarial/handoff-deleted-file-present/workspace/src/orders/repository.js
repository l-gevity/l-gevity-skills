export function saveOrder(store, order) {
  store.set(order.id, order);
}
