import { save, load } from "./repository.js";

// Amounts are integer cents; rates are basis points (2100 = 21%).
const TAX_BP = { nl: 2100, de: 1900, fr: 2000 };
const DISCOUNT_TIERS = [
  { overCents: 50000, cutBp: 1000 },
  { overCents: 10000, cutBp: 500 },
];

export function placeOrder(customer, lines) {
  if (lines.length === 0) throw new Error("an order needs at least one line");
  if (!(customer.country in TAX_BP)) throw new Error(`no tax rate for country ${customer.country}`);

  const subtotal = lines.reduce((sum, line) => sum + line.priceCents * line.quantity, 0);
  const tier = DISCOUNT_TIERS.find((candidate) => subtotal > candidate.overCents);
  const discount = tier ? Math.round((subtotal * tier.cutBp) / 10000) : 0;
  const tax = Math.round(((subtotal - discount) * TAX_BP[customer.country]) / 10000);

  return save({
    customer,
    lines,
    status: "placed",
    invoice: {
      lines: lines.map((line) => ({ label: line.sku, amountCents: line.priceCents * line.quantity })),
      discountCents: discount,
      taxCents: tax,
      totalCents: subtotal - discount + tax,
    },
  });
}

export function cancelOrder(orderId) {
  const order = getOrder(orderId);
  if (order.status !== "placed") throw new Error(`order ${orderId} is ${order.status}, not placed`);
  order.status = "cancelled";
  return save(order);
}

export function getOrder(orderId) {
  const order = load(orderId);
  if (!order) throw new Error(`no order ${orderId}`);
  return order;
}
