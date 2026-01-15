from fastapi import APIRouter, Query, BackgroundTasks, HTTPException
from app.services.scraper import fetch_jobs
from app.services.email import send_job_alert
from app.services.sheets import log_jobs_to_sheet
from app.services.llm import tailor_resume
from app.core.scheduler import scheduler
from typing import Optional, List
from pydantic import BaseModel
import logging
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

router = APIRouter()
logger = logging.getLogger(__name__)


class ScrapeRequest(BaseModel):
    search_terms: List[str]  # Changed to list for multiple roles
    locations: List[str] = ["Remote"]  # Changed to list
    results_wanted: int = 5
    email_to: Optional[str] = None
    country_indeed: str = "India"  # User mentioned Indian cities
    tailor_resume_for_top_match: bool = False
    resume_text: Optional[str] = None  # Text extracted from PDF
    schedule_interval_hours: Optional[int] = None  # If set, schedules this job


def generate_pdf_from_text(text: str, filename: str = "tailored_resume.pdf") -> str:
    """
    Generates a simple PDF from text using ReportLab and returns the path.
    """
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        text_object = c.beginText(40, height - 40)
        text_object.setFont("Helvetica", 12)

        # Simple wrapping
        lines = text.split("\n")
        for line in lines:
            # Wrap long lines
            wrapped_lines = simpleSplit(line, "Helvetica", 12, width - 80)
            for wrapped in wrapped_lines:
                text_object.textLine(wrapped)
                if text_object.getY() < 40:  # Page break
                    c.drawText(text_object)
                    c.showPage()
                    text_object = c.beginText(40, height - 40)
                    text_object.setFont("Helvetica", 12)

        c.drawText(text_object)
        c.save()
        return filename
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")
        return ""


async def process_job_search(request: ScrapeRequest):
    """
    Core logic to fetch, log, and alert.
    """
    all_jobs = []
    for term in request.search_terms:
        for loc in request.locations:
            logger.info(f"Processing search for: {term} in {loc}")
            try:
                jobs = await fetch_jobs(
                    search_term=term,
                    location=loc,
                    results_wanted=request.results_wanted,
                    country_indeed=request.country_indeed,
                    hours_old=72,  # Get recent jobs
                )
                # Tag jobs with the search term used
                for job in jobs:
                    job["search_term"] = term
                    job["searched_location"] = loc

                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Failed to scrape {term} in {loc}: {e}")

    if not all_jobs:
        logger.warning("No jobs found for any criteria.")
        # Try to notify if email requested?
        if request.email_to:
            await send_job_alert(
                request.email_to, [], None
            )  # Send empty alert or skip?
        return

    # 1. Log to Sheets
    log_jobs_to_sheet(all_jobs)

    # 2. Tailor Resume & Generate Attachments
    attachment_path = None
    if request.tailor_resume_for_top_match and request.resume_text and all_jobs:
        best_job = all_jobs[0]  # Simplification: pick first
        description = best_job.get("description", "")
        if description:
            try:
                logger.info("Tailoring resume for top match...")
                tailored = tailor_resume(request.resume_text, description)
                logger.info("Resume tailored successfully.")
                best_job["tailored_resume_preview"] = tailored[:500] + "..."

                # Generate PDF
                logger.info("Generating PDF attachment...")
                attachment_path = generate_pdf_from_text(
                    tailored, "tailored_resume.pdf"
                )

            except Exception as e:
                logger.error(f"Failed to tailor resume or generate PDF: {e}")

    # 3. Send Email (with attachment if available)
    if request.email_to:
        await send_job_alert(request.email_to, all_jobs, attachment_path)


@router.post("/search")
async def search_jobs_endpoint(
    request: ScrapeRequest, background_tasks: BackgroundTasks
):
    """
    Trigger a job search. Can handle multiple roles and scheduling.
    """
    # Immediate Run
    background_tasks.add_task(process_job_search, request)

    # Schedule if requested
    if request.schedule_interval_hours:
        job_id = f"scrape_{request.email_to}_{request.search_terms[0]}"
        try:
            scheduler.add_job(
                process_job_search,
                "interval",
                hours=request.schedule_interval_hours,
                args=[request],
                id=job_id,
                replace_existing=True,
            )
            return {
                "message": f"Search started + Scheduled every {request.schedule_interval_hours} hours",
                "job_id": job_id,
            }
        except Exception as e:
            logger.error(f"Failed to schedule: {e}")
            return {"message": "Search started but scheduler failed", "error": str(e)}

    return {"message": "Search started in background"}


@router.get("/test")
async def test_endpoint():
    return {"status": "ok"}
