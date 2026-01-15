from app.api.endpoints.jobs import generate_pdf_from_text
from app.services.email import send_job_alert
import os
import asyncio


async def test():
    # 1. Test PDF Generation
    text = "This is a tailored resume.\nSkill: Python\nExperience: Building Agents."
    pdf_path = generate_pdf_from_text(text, "test_resume_gen.pdf")

    if os.path.exists(pdf_path):
        print(f"PDF Generated successfully: {pdf_path}")
    else:
        print("PDF Generation Failed")

    # 2. Test Email Logic (Mocked send)
    # We won't actually send unless API key is valid, but we check if function runs without error
    try:
        await send_job_alert(
            "test@example.com", [{"title": "Test Job", "company": "Test Co"}], pdf_path
        )
        print("Email function executed (check logs for actual send status).")
    except Exception as e:
        print(f"Email function failed: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(test())
    except Exception as e:
        print(f"Loop error: {e}")
