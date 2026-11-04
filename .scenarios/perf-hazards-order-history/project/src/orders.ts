import { db } from "./db/index.js";

export const PAGE_SIZE = 50;

export async function orderHistory(customerId: string, page: number) {
  const orders = await db.query(
    `SELECT * FROM orders WHERE customer_id = $1 ORDER BY created_at DESC OFFSET $2`,
    [customerId, page * PAGE_SIZE],
  );
  for (const order of orders.rows) {
    order.items = (await db.query(`SELECT * FROM order_items WHERE order_id = $1`, [order.id])).rows;
  }
  const skus: string[] = [];
  for (const order of orders.rows) {
    for (const item of order.items) {
      if (!skus.includes(item.sku)) skus.push(item.sku);
    }
  }
  return { orders: orders.rows.slice(0, PAGE_SIZE), distinctSkus: skus };
}
