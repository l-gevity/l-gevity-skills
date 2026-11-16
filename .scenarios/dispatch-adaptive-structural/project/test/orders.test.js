import { test } from "node:test";
import assert from "node:assert/strict";
import { placeOrder, cancelOrder, getOrder } from "../src/orders/index.js";
import { labelFor } from "../src/shipping/index.js";

const customer = (country = "nl") => ({ name: "A. Jansen", country, address: "Kade 1, Utrecht" });
const line = (priceCents, quantity = 1, sku = "pen") => ({ sku, priceCents, quantity });

test("an order below the first tier gets no discount", () => {
  const order = placeOrder(customer(), [line(250, 4)]);
  assert.deepEqual(order.invoice, {
    lines: [{ label: "pen", amountCents: 1000 }],
    discountCents: 0,
    taxCents: 210,
    totalCents: 1210,
  });
});

test("a subtotal of exactly 100.00 gets no discount", () => {
  const { invoice } = placeOrder(customer(), [line(10000)]);
  assert.equal(invoice.discountCents, 0);
  assert.equal(invoice.totalCents, 12100);
});

test("a subtotal above 100.00 gets 5%", () => {
  const { invoice } = placeOrder(customer(), [line(10001)]);
  assert.equal(invoice.discountCents, 500);
  assert.equal(invoice.taxCents, 1995);
  assert.equal(invoice.totalCents, 11496);
});

test("a subtotal of exactly 500.00 stays at 5%", () => {
  const { invoice } = placeOrder(customer(), [line(50000)]);
  assert.equal(invoice.discountCents, 2500);
});

test("a subtotal above 500.00 gets 10%", () => {
  const { invoice } = placeOrder(customer(), [line(20000, 3)]);
  assert.equal(invoice.discountCents, 6000);
  assert.equal(invoice.taxCents, 11340);
  assert.equal(invoice.totalCents, 65340);
});

test("tax follows the customer's country", () => {
  assert.equal(placeOrder(customer("de"), [line(1000)]).invoice.taxCents, 190);
  assert.equal(placeOrder(customer("fr"), [line(1000)]).invoice.taxCents, 200);
});

test("tax is charged on the discounted amount", () => {
  const { invoice } = placeOrder(customer("de"), [line(20000)]);
  assert.equal(invoice.discountCents, 1000);
  assert.equal(invoice.taxCents, 3610);
});

test("the invoice has one line per order line", () => {
  const { invoice } = placeOrder(customer(), [line(250, 4, "pen"), line(1200, 1, "ink")]);
  assert.deepEqual(invoice.lines, [
    { label: "pen", amountCents: 1000 },
    { label: "ink", amountCents: 1200 },
  ]);
});

test("a country without a tax rate is rejected", () => {
  assert.throws(() => placeOrder(customer("be"), [line(1000)]), /no tax rate for country be/);
});

test("an order without lines is rejected", () => {
  assert.throws(() => placeOrder(customer(), []), /at least one line/);
});

test("a placed order is stored and can be cancelled once", () => {
  const order = placeOrder(customer(), [line(1000)]);
  assert.equal(getOrder(order.id).status, "placed");
  assert.equal(cancelOrder(order.id).status, "cancelled");
  assert.throws(() => cancelOrder(order.id), /is cancelled, not placed/);
});

test("an unknown order is rejected", () => {
  assert.throws(() => getOrder(999999), /no order 999999/);
});

test("the shipping label reads the order through the orders module", () => {
  const order = placeOrder(customer(), [line(250, 4), line(1200)]);
  assert.deepEqual(labelFor(order.id), { orderId: order.id, address: "Kade 1, Utrecht", lineCount: 2 });
});
