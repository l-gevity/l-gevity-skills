"""Job queue client.

Delivery contract: a job whose handler raises is redelivered with exponential
backoff, up to 5 attempts, then moved to the dead-letter queue. Handlers must
be idempotent.
"""


class JobQueue:
    def __init__(self, broker):
        self._broker = broker

    def consume(self, topic, handler):
        for job in self._broker.subscribe(topic):
            try:
                handler(job.payload)
            except Exception:
                self._broker.nack(job)
            else:
                self._broker.ack(job)
