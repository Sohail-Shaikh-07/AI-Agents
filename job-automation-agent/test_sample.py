import asyncio
import logging
import os
from dotenv import load_dotenv

# Load env before importing app services so keys are picked up
load_dotenv()

from app.api.endpoints.jobs import process_job_search, ScrapeRequest
from app.services.parser import parse_pdf
from app.core.config import ROLES, LOCATIONS  # Import the lists

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL_TO = "contact.sohailshaikh07@gmail.com"
RESUME_PATH = "Data/Resume.pdf"


async def run_test():
    logger.info("Starting Full Coverage Test Sample...")

    # 1. Parse Resume
    resume_text = ""
    if os.path.exists(RESUME_PATH):
        logger.info(f"Parsing resume from {RESUME_PATH}...")
        resume_text = parse_pdf(RESUME_PATH)
    else:
        logger.warning(f"Resume not found at {RESUME_PATH}.")
        resume_text = "Experienced Data Scientist."

    # 2. Create Request Object with ALL Roles and Locations
    # We reduce results_wanted to 3 per combo to avoid hitting rate limits or taking forever during test
    # (4 roles * 6 locations = 24 scrapes. This might take 5-10 mins. We'll run it.)

    logger.info(
        f"Testing search for {len(ROLES)} Roles in {len(LOCATIONS)} Locations..."
    )

    req = ScrapeRequest(
        search_terms=ROLES,
        locations=LOCATIONS,
        results_wanted=2,  # Keep low for test speed
        email_to=EMAIL_TO,
        country_indeed="India",
        tailor_resume_for_top_match=True,
        resume_text=resume_text,
    )

    try:
        await process_job_search(req)
        logger.info("Test Sample Completed Successfully!")
    except Exception as e:
        logger.error(f"Test Failed: {e}")


if __name__ == "__main__":
    try:
        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(run_test())
    except KeyboardInterrupt:
        pass
