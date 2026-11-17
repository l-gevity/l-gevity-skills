import { ORDER_LINE_FIELDS } from "../generated/api-types.js";

export function priceOrder(lines) {
  return lines.reduce((total, line) => total + line.quantity * line.unitPrice, 0);
}

export { ORDER_LINE_FIELDS };
