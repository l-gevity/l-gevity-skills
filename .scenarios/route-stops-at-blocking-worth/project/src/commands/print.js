import { toJson } from "../format/json.js";

export function printCommand(record) {
  return toJson(record);
}
