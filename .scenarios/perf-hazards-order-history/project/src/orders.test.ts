import { describe, expect, it, vi } from "vitest";

vi.mock("./db/index.js", () => ({
  db: {
    query: vi.fn(async (sql: string) =>
      sql.includes("FROM orders")
        ? { rows: [{ id: "o1" }, { id: "o2" }] }
        : { rows: [{ sku: "A" }, { sku: "B" }] },
    ),
  },
}));

import { orderHistory } from "./orders.js";

describe("orderHistory", () => {
  it("returns orders with their items and distinct skus", async () => {
    const result = await orderHistory("c1", 0);
    expect(result.orders).toHaveLength(2);
    expect(result.distinctSkus).toEqual(["A", "B"]);
  });
});
