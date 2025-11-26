from fastapi import FastAPI
from scraper import scrape_site
from rq import Queue
from redis import Redis
import uuid
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()
redis_conn = Redis(host="redis", port=6379)
q = Queue(connection=redis_conn)

@app.post("/crawl")
def crawl(url: str):
    job_id = str(uuid.uuid4())
    q.enqueue(scrape_site, url, job_id)
    logging.info(f"Job {job_id} queued for {url}")
    return {"job_id": job_id, "status": "queued"}

@app.get("/result/{job_id}")
def get_result(job_id: str):
    result = redis_conn.get(job_id)
    if result:
        return {"job_id": job_id, "emails": eval(result.decode("utf-8"))}
    return {"job_id": job_id, "status": "pending"}
