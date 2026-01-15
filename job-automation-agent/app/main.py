from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from app.api.endpoints import jobs
import uvicorn
from contextlib import asynccontextmanager
from app.core.scheduler import scheduler
from app.api.endpoints.jobs import process_job_search, ScrapeRequest
from app.core.config import ROLES, LOCATIONS
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Scheduler...")
    scheduler.start()

    # Auto-schedule default job on startup
    logger.info("Initializing Default Scheduled Scrape (Every 3 Hours)...")
    defaults = ScrapeRequest(
        search_terms=ROLES,
        locations=LOCATIONS,  # Use full list
        # Ideally we'd iterate but for "agentic" simplicity let's stick to config defaults.
        # Or better: Create a tailored request.
        schedule_interval_hours=3,
        results_wanted=10,
        email_to="contact.sohailshaikh07@gmail.com",  # Hardcoded user pref for auto-start
        country_indeed="India",
    )

    # Add the job directly
    scheduler.add_job(
        process_job_search,
        "interval",
        hours=3,
        args=[defaults],
        id="auto_scrape_default",
        replace_existing=True,
    )

    yield
    # Shutdown
    logger.info("Stopping Scheduler...")
    scheduler.shutdown()


app = FastAPI(title="Job Automation Agent API", version="1.1.0", lifespan=lifespan)

# Include Routers
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])


@app.get("/")
def read_root():
    return {
        "message": "Job Automation Agent is running. Go to /docs for API documentation."
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
