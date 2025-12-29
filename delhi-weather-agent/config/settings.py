import os
import sys
from dotenv import load_dotenv

load_dotenv()

# --- Application Config ---
PROJECT_NAME = "Delhi Weather Agent (Enterprise Edition)"
VERSION = "2.0.0"

# --- Target Locations (Delhi) ---
# Format: {"Name": "Lat,Lon"}
LOCATIONS = {
    "Anand Vihar": "28.6469,77.3160",
    "Connaught Place": "28.6304,77.2177",
    "Dwarka": "28.5882,77.0494",
    "Okhla Phase III": "28.5273,77.2618",
    "Rohini": "28.7041,77.1025",
    "IGI Airport": "28.5562,77.1000",
}

# --- Data Strategy ---
YEAR = 2025
INTERVAL_HOURS = 3
# Capture every hour of the day (0-23) since we fetch full day anyway
TARGET_HOURS = [h for h in range(24)]

# --- Formatting (Types) ---
DATE_FORMAT_OUTPUT = "%d/%m/%Y"  # DD/MM/YYYY
TIME_FORMAT_OUTPUT = "%H:%M"  # HH:MM (24-hour)
TIMEZONE = "Asia/Kolkata"

# --- API Keys (Enterprise Load Balancing) ---
# Inspects variables VC_API_1 through VC_API_20
API_KEYS = []
for i in range(1, 21):
    key = os.getenv(f"VC_API_{i}")
    if key:
        API_KEYS.append(key)

if not API_KEYS:
    # Fallback to legacy comma-separated if needed, or warn
    legacy = os.getenv("VC_API_KEYS")
    if legacy:
        API_KEYS = legacy.split(",")

# --- Google Sheets ---
# Users can provide ID (safer) or Name
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_JSON_ENV_VAR = "GOOGLE_JSON"

# --- Limits & Safety ---
REQUEST_DELAY_SECONDS = 1.0  # Slightly faster but safer with more keys
DAILY_QUOTA_PER_KEY = 1000  # Visual Crossing Free Tier
