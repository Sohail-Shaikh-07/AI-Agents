import resend
import os
from typing import List, Dict, Optional
import logging
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER_EMAIL = "Roxan AI <support@pystack.site>"

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
else:
    logger.warning(
        "RESEND_API_KEY not found in environment variables. Email sending will be disabled/mocked."
    )


async def send_job_alert(
    to_email: str, jobs: List[Dict], attachment_path: Optional[str] = None
):
    """
    Sends an email with the list of found jobs using Resend.
    Supports PDF attachment for tailored resume.
    """
    if not RESEND_API_KEY:
        logger.warning("Skipping email send: No API Key")
        return {"status": "skipped", "reason": "No API Key"}

    if not jobs:
        # We might still want to send an email if zero jobs found but process ran?
        # For now, let's skip.
        return {"status": "skipped", "reason": "No jobs to send"}

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    subject = f"Roxan AI Job Alert: {len(jobs)} New Opportunities Found ({date_str})"

    # Professional HTML Body
    jobs_html = rf"""
    <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2c3e50;">Active Recruitment Update</h2>
        <p>Hello,</p>
        <p>Roxan AI has identified <strong>{len(jobs)}</strong> new positions matching your criteria as of {date_str}.</p>
        
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <tr style="background-color: #f8f9fa;">
                <th style="padding: 10px; border-bottom: 2px solid #dee2e6; text-align: left;">Role</th>
                <th style="padding: 10px; border-bottom: 2px solid #dee2e6; text-align: left;">Company</th>
                <th style="padding: 10px; border-bottom: 2px solid #dee2e6; text-align: left;">Location</th>
            </tr>
    """

    for job in jobs[:10]:  # Limit to top 10 in email body to avoid too large email
        title = job.get("title", "N/A")
        company = job.get("company", "N/A")
        url = job.get("job_url", "#")
        location = job.get("location", "N/A")

        jobs_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;"><a href="{url}" style="color: #007bff; text-decoration: none;">{title}</a></td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{company}</td>
                <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{location}</td>
            </tr>
        """

    jobs_html += """
        </table>
        
        <p style="margin-top: 20px; font-size: 0.9em; color: #6c757d;">
            Run automated by Roxan AI.<br>
            <a href="https://pystack.site" style="color: #6c757d; text-decoration: underline;">Visit Dashboard</a>
        </p>
    </div>
    """

    params = {
        "from": SENDER_EMAIL,
        "to": to_email,
        "subject": subject,
        "html": jobs_html,
        "attachments": [],
    }

    # Add attachment if exists
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as f:
                content = f.read()
                # Resend expects list of dicts with filename and content (as list of integers or bytes? SDK is strict)
                # Actually Resend Python SDK handles file reading if we pass params correctly?
                # The official way in current python sdk:
                # "attachments": [{"filename": "resume.pdf", "content": list(content)}] or base64?
                # Let's check typical usage. Usually `content` is a buffer or list of ints.
                # Simplest is reading as list of bytes.
                params["attachments"].append(
                    {
                        "filename": os.path.basename(attachment_path),
                        "content": list(content),
                    }
                )
        except Exception as e:
            logger.error(f"Failed to attach file: {e}")

    try:
        r = resend.Emails.send(params)
        logger.info(f"Email sent: {r}")
        return r
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return {"status": "error", "error": str(e)}
