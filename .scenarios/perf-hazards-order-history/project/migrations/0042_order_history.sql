-- Order history: record which page a customer viewed.
CREATE INDEX events_customer_idx ON events (customer_id);
ALTER TABLE orders ADD COLUMN archived boolean NOT NULL DEFAULT false;
