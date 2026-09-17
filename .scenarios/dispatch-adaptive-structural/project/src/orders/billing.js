// Billing rules. These change most weeks: rates, discount tiers, and the
// invoice layout are all edited here.
const TAX = { nl: 0.21, de: 0.19, fr: 0.2 };
const DISCOUNT_TIERS = [
  { over: 500, cut: 0.1 },
  { over: 100, cut: 0.05 },
];

export function priceOrder(order) {
  const gross = order.lines.reduce((sum, line) => sum + line.price * line.quantity, 0);
  const tier = DISCOUNT_TIERS.find((candidate) => gross > candidate.over);
  return tier ? gross * (1 - tier.cut) : gross;
}

export function applyTaxRules(amount, country) {
  return amount * (1 + (TAX[country] ?? 0));
}

export function invoiceFor(order) {
  return {
    lines: order.lines.map((line) => ({ label: line.sku, amount: line.price * line.quantity })),
    total: order.total,
  };
}
