CREATE TABLE orders (
  id          uuid PRIMARY KEY,
  customer_id uuid NOT NULL,
  created_at  timestamptz NOT NULL,
  status      text NOT NULL,
  total       numeric(12, 2) NOT NULL,
  payload     jsonb NOT NULL
);
CREATE INDEX orders_status_idx ON orders (status);

CREATE TABLE order_items (
  id       uuid PRIMARY KEY,
  order_id uuid NOT NULL REFERENCES orders (id),
  sku      text NOT NULL,
  qty      integer NOT NULL,
  price    numeric(12, 2) NOT NULL
);

CREATE TABLE events (
  id          bigserial PRIMARY KEY,
  customer_id uuid NOT NULL,
  kind        text NOT NULL,
  at          timestamptz NOT NULL
);
