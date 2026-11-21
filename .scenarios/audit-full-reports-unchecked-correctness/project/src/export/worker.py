from export.retry import with_retry
from export.render import render_report

BATCH_SIZE = 100


def handle_export(payload, storage):
    rows = payload["rows"]
    pages = [rows[i:i + BATCH_SIZE] for i in range(0, len(rows) - BATCH_SIZE, BATCH_SIZE)]
    document = render_report(payload["customer"], pages)
    with_retry(lambda: storage.upload(payload["key"], document))


def register(queue, storage):
    queue.consume("exports", lambda payload: handle_export(payload, storage))
