from rq import Queue
from rq.job import Job
from redis import Redis
from .jobs.scrape_cases import scrape_cases

class JobManager:
    def __init__(self):
        self.redis = Redis()
        self.q = Queue(connection=self.redis)

    def enqueue_scrape(self, name, acts, sections, state_code):
        # 4 hour timeout
        return self.q.enqueue(
            scrape_cases,
            name,
            acts,
            sections,
            state_code,
            job_timeout=14400
        )

    def get_jobs(self):
        queued_jobs = self.q.get_jobs()

        started_job_ids = self.q.started_job_registry.get_job_ids()
        started_jobs = [Job.fetch(job_id, connection=self.redis) for job_id in started_job_ids]

        finished_job_ids = self.q.finished_job_registry.get_job_ids()
        finished_jobs = [Job.fetch(job_id, connection=self.redis) for job_id in finished_job_ids]

        return queued_jobs + started_jobs + finished_jobs
