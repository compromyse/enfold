from rq import Queue
from redis import Redis
from jobs.scrape_cases import scrape_cases

class JobManager:
    def __init__(self):
        redis = Redis()
        self.q = Queue(connection=redis)

    def enqueue_scrape(self, act, section, state_code):
        return self.q.enqueue(
            scrape_cases,
            act,
            section,
            state_code
        )
