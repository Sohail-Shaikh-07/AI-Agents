from jobspy import scrape_jobs
import pandas as pd
from typing import List, Optional, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_jobs(
    search_term: str,
    location: str,
    results_wanted: int = 10,
    hours_old: int = 72,
    country_indeed: str = "USA"
) -> List[Dict]:
    """
    Scrapes jobs from LinkedIn, Indeed, Glassdoor, and ZipRecruiter using python-jobspy.
    """
    logger.info(f"Starting scrape for: {search_term} in {location}")
    
    try:
        # jobspy expects synchronous execution for now, but we'll run it directly as it's the main operation
        # For production with high load, we'd offload this to a worker (Celery/RQ)
        jobs: pd.DataFrame = scrape_jobs(
            site_name=["indeed", "linkedin", "glassdoor"],
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            country_indeed=country_indeed,
            
            # linkedin_fetch_description=True # Optional, slows down scraping
        )
        
        logger.info(f"Found {len(jobs)} jobs")
        
        if jobs.empty:
            return []

        # Convert to list of dicts for API response
        # Handle nan values/dates for JSON serialization
        jobs_dict = jobs.to_dict(orient="records")
        
        # Clean up data for JSON serialization (handle NaNs, timestamps)
        cleaned_jobs = []
        for job in jobs_dict:
            # Basic cleaning
            clean_job = {k: (v if pd.notna(v) else None) for k, v in job.items()}
            # Convert str dates if needed, though jobspy usually gives strings or objects
            cleaned_jobs.append(clean_job)
            
        return cleaned_jobs

    except Exception as e:
        logger.error(f"Error scraping jobs: {e}")
        return []
