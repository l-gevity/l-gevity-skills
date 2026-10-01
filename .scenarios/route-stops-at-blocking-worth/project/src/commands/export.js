import { toJson } from "../format/json.js";

export function exportCommand(records) {
  return toJson({ records });
}
