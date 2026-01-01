import os
import sys
from dotenv import load_dotenv

load_dotenv()

# --- Application Config ---
PROJECT_NAME = "Delhi Weather Agent (Enterprise Edition)"
VERSION = "2.0.0"

# --- Target Locations ---
# The Web UI uses dynamic search, so no hardcoded locations are needed here.

# --- Data Strategy ---
YEAR = 2025
INTERVAL_HOURS = 3
TARGET_HOURS = [h for h in range(24)]

# --- Formatting (Types) ---
DATE_FORMAT_OUTPUT = "%d/%m/%Y"  # DD/MM/YYYY
TIME_FORMAT_OUTPUT = "%H:%M"  # HH:MM (24-hour)
TIMEZONE = "Asia/Kolkata"

# --- Google Sheets ---
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_JSON_ENV_VAR = "GOOGLE_JSON"

# --- Limits & Safety ---
REQUEST_DELAY_SECONDS = 0.5
