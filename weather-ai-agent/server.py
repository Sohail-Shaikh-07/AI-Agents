from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import threading
import time
from datetime import datetime

# Import from local src
from src.processor import DynamicProcessor

app = FastAPI()

# --- In-Memory Log Buffer ---
log_buffer = []
job_status = "idle"  # idle, running, completed


class JobRequest(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    start_date: str
    end_date: str
    interval: int = 1
    columns: List[str]


def log_callback(msg: str):
    """Callback passed to processor to capture logs."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_buffer.append(f"{msg}")
    # Keep buffer small
    if len(log_buffer) > 100:
        log_buffer.pop(0)


def run_job_background(req: JobRequest):
    global job_status
    job_status = "running"
    log_buffer.clear()
    log_callback(f"Initializing job for {req.location_name}...")

    try:
        processor = DynamicProcessor(
            location=req.location_name,
            lat=req.latitude,
            lon=req.longitude,
            start_date=req.start_date,
            end_date=req.end_date,
            interval=req.interval,
            columns=req.columns,
        )
        processor.run(log_calback=log_callback)
        job_status = "completed"
    except Exception as e:
        import traceback

        traceback.print_exc()
        log_callback(f"CRITICAL ERROR: {e}")
        job_status = "error"


@app.post("/api/start-job")
def start_job(req: JobRequest, background_tasks: BackgroundTasks):
    global job_status
    if job_status == "running":
        return {"status": "error", "message": "A job is already running."}

    background_tasks.add_task(run_job_background, req)
    return {"status": "success", "message": "Job dispatched successfully."}


@app.get("/api/logs")
def get_logs():
    global log_buffer
    logs_to_send = list(log_buffer)
    log_buffer.clear()

    return {"status": job_status, "lines": logs_to_send}


# Serve Static UI
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
