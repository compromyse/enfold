from rq import Queue
from rq.job import Job
from redis import Redis
from .jobs.scrape_cases import scrape_cases

class JobManager:
    def __init__(self):
        self.redis = Redis()
        self.q = Queue(connection=self.redis)

    def enqueue_scrape(self, name, acts, section, state_code):
        # 4 hour timeout
        return self.q.enqueue(
            scrape_cases,
            name,
            acts,
            section,
            state_code,
            job_timeout=14400
        )

    def get_started_jobs(self):
        started_job_ids = self.q.started_job_registry.get_job_ids()
        jobs = [Job.fetch(job_id, connection=self.redis) for job_id in started_job_ids]
        return jobs
