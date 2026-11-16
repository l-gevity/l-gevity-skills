// Discount tiers for an order's gross amount.
const DISCOUNT_TIERS = [
  { over: 500, cut: 0.1 },
  { over: 100, cut: 0.05 },
];

export function discountFor(gross, lines) {
  if (lines.length === 0) return 0;
  const tier = DISCOUNT_TIERS.find((candidate) => gross >= candidate.over);
  return tier ? Math.round(gross * tier.cut * 100) / 100 : 0;
}
