import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import logging
import base64
import json
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
# Check for Base64 Env Var first, then file
GOOGLE_CREDENTIALS_BASE64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
CREDENTIALS_FILE = "credentials.json"
SHEET_NAME = "Job Automation Agent"  # Default sheet name


def get_sheet_service():
    creds = None

    # Priority 1: Base64 Env Var
    if GOOGLE_CREDENTIALS_BASE64:
        try:
            creds_json = base64.b64decode(GOOGLE_CREDENTIALS_BASE64).decode("utf-8")
            creds_dict = json.loads(creds_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        except Exception as e:
            logger.error(f"Failed to decode GOOGLE_CREDENTIALS_BASE64: {e}")

    # Priority 2: Local File
    if not creds and os.path.exists(CREDENTIALS_FILE):
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                CREDENTIALS_FILE, SCOPE
            )
        except Exception as e:
            logger.error(f"Failed to load {CREDENTIALS_FILE}: {e}")

    if not creds:
        logger.warning(
            "No valid Google Sheets credentials found (Env or File). Logging disabled."
        )
        return None

    try:
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        logger.error(f"Failed to authorize Google Sheets: {e}")
        return None


def log_jobs_to_sheet(jobs: List[Dict]):
    """
    Appends a list of jobs to the Google Sheet.
    Creates the sheet and header if it doesn't exist.
    """
    client = get_sheet_service()
    if not client:
        return

    try:
        # Open sheet: Prefer ID, then URL, then Name
        try:
            if GOOGLE_SHEET_ID:
                sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
            elif GOOGLE_SHEET_URL:
                sheet = client.open_by_url(GOOGLE_SHEET_URL).sheet1
            else:
                sheet = client.open(SHEET_NAME).sheet1
        except gspread.SpreadsheetNotFound:
            if GOOGLE_SHEET_ID or GOOGLE_SHEET_URL:
                logger.error(
                    f"Sheet with ID {GOOGLE_SHEET_ID} or URL {GOOGLE_SHEET_URL} not found/accessible."
                )
                return

            logger.info("Sheet not found, creating new one...")
            sheet = client.create(SHEET_NAME).sheet1
            # Add header
            sheet.append_row(
                [
                    "Date Found",
                    "Date Posted",
                    "Source (Indeed/LinkedIn)",
                    "Job Title",
                    "Company",
                    "Location",
                    "Job Link",
                    "Salary Range",
                    "Job Description",
                    "Status",
                ]
            )

        rows_to_add = []
        for job in jobs:
            # Map job dict to row
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(job.get("date_posted") or "N/A"),
                job.get("site", "Unknown"),
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("job_url", ""),
                job.get("salary_range")
                or job.get("salary")
                or "N/A",  # JobSpy might return either
                (job.get("description") or "")[
                    :500
                ],  # Truncated for sheet as requested
                "New",
            ]
            rows_to_add.append(row)

        if rows_to_add:
            sheet.append_rows(rows_to_add)
            logger.info(f"Logged {len(rows_to_add)} jobs to Google Sheets.")

    except Exception as e:
        logger.error(f"Error logging to sheets: {e}")
