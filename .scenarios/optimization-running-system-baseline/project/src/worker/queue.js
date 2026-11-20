// Jobs arrive from the API; one worker drains them in arrival order.
const jobs = [];

export function enqueue(job) {
  jobs.push({ ...job, enqueuedAt: Date.now() });
}

export async function drain(run) {
  while (jobs.length > 0) {
    await run(jobs.shift());
  }
}
