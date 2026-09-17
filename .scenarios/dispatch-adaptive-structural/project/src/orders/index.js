import { priceOrder, invoiceFor, applyTaxRules } from "./billing.js";
import { save, load } from "./repository.js";

export function placeOrder(customer, lines) {
  const order = { customer, lines, status: "placed" };
  order.total = priceOrder(order);
  order.invoice = invoiceFor(order);
  save(order);
  return order;
}

export function reprice(orderId, country) {
  const order = load(orderId);
  order.total = applyTaxRules(priceOrder(order), country);
  save(order);
  return order;
}
