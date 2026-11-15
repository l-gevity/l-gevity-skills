# shop-api

One Node process and one deployable. Each directory under `src/` is a module:
other modules import only its `index.js`.

- `src/orders/`: placing, cancelling, and reading orders.
- `src/shipping/`: shipping labels.

Run the tests with `npm test`. Requirements live in `docs/requirements/`, the
evidence they cite in `docs/evidence/`.
