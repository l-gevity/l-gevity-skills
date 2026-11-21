// Analysis jobs: the HTTP handler enqueues, one worker drains the queue.
const jobs = [];

export function enqueue(job) {
  jobs.push({ ...job, enqueuedAt: Date.now() });
}

export async function drain(runAnalysis) {
  while (jobs.length > 0) {
    const job = jobs.shift();
    await runAnalysis(job); // one at a time; a long analysis blocks the rest
  }
}
