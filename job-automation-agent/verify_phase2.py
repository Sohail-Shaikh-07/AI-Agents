import os
import sys

# Mocking env for test if not set
if not os.getenv("DEEPINFRA_API_KEY"):
    print("Warning: DEEPINFRA_API_KEY not set. LLM check will probably fail or skip.")

# Try imports
try:
    from app.services.llm import client as llm_client
    from app.services.sheets import get_sheet_service
    from app.services.parser import parse_pdf
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    print("Imports successful.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

# Check PDF Parser
test_pdf = "test_resume.pdf"
if os.path.exists(test_pdf):
    print(f"Testing PDF parse on {test_pdf}...")
    text = parse_pdf(test_pdf)
    print(f"Extracted {len(text)} chars.")
else:
    print("No test_resume.pdf found, skipping PDF test.")

# Check Sheets
print("Checking Google Sheets connection...")
service = get_sheet_service()
if service:
    print("Google Sheets Service: Connected (Credentials found).")
else:
    print(
        "Google Sheets Service: Not connected (No valid service_account.json found - expected if not provided)."
    )

# Check LLM Client
if llm_client:
    print("LLM Client: Initialized.")
else:
    print("LLM Client: Not initialized (Missing API Key).")
