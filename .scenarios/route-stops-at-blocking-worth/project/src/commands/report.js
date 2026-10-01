import { toJson } from "../format/json.js";

export function reportCommand(records) {
  const total = records.reduce((sum, record) => sum + record.amount, 0);
  return toJson({ count: records.length, total });
}
