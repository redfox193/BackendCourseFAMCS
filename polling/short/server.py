import asyncio
import random
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException

app = FastAPI()

jobs: dict[str, dict] = {}
background_tasks: set[asyncio.Task] = set()


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    result: str | None = None


@app.post('/jobs')
async def create_job():
    job_id = str(uuid.uuid4())
    jobs[job_id] = {'status': 'pending', 'progress': 0, 'result': None}

    task = asyncio.create_task(_process_job(job_id))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

    return JobStatus(job_id=job_id, **jobs[job_id])


@app.get('/jobs/{job_id}', response_model=JobStatus)
async def get_job_status(job_id: str) -> JobStatus:
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail='Job not found')
    return JobStatus(job_id=job_id, **jobs[job_id])


async def _process_job(job_id: str) -> None:
    jobs[job_id]['status'] = 'running'

    for step in range(1, 11):
        await asyncio.sleep(random.uniform(0.5, 1.5))
        jobs[job_id]['progress'] = step * 10

    jobs[job_id]['status'] = 'done'
    jobs[job_id]['result'] = f'Computed value: {random.randint(100, 999)}'
