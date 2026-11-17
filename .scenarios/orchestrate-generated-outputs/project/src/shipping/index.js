import { LABEL_FIELDS } from "../generated/api-types.js";

export function labelFor(order) {
  return { orderId: order.id, weightGrams: 500 };
}

export { LABEL_FIELDS };
