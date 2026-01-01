import os
import gspread
import pandas as pd
import json
import base64
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from config.settings import GOOGLE_SHEET_ID, GOOGLE_JSON_ENV_VAR


class GoogleSheetConnector:
    """
    Enterprise Connector for Google Sheets.
    Supports Service Account Authentication via Env Vars (Render compatible).
    """

    def __init__(self):
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        self.client = self._authenticate()

        if not GOOGLE_SHEET_ID:
            raise ValueError("[Configuration Error] GOOGLE_SHEET_ID is missing in .env")

        try:
            self.sheet = self.client.open_by_key(GOOGLE_SHEET_ID)
            print(f"[GSheet] Connected to Sheet: {self.sheet.title}")
        except gspread.exceptions.APIError as e:
            if "403" in str(e):
                raise PermissionError(
                    f"\n[CRITICAL AUTH ERROR] 🛑 \n"
                    f"The Service Account does not have permission to access Sheet ID: {GOOGLE_SHEET_ID}.\n"
                    f"👉 ACTION REQUIRED: Open the Google Sheet -> Click 'Share' -> Add your Service Account Email (from your JSON file) as Editor."
                )
            raise e
        
    def _authenticate(self):
        """Authenticates using Service Account JSON."""
        if os.path.exists("credential.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "credential.json", self.scope
            )
        elif os.getenv(GOOGLE_JSON_ENV_VAR):
            json_str = base64.b64decode(os.getenv(GOOGLE_JSON_ENV_VAR)).decode("utf-8")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                json.loads(json_str), self.scope
            )
        else:
            raise FileNotFoundError(
                "Service Account credentials not found (Checked 'credential.json' and 'GOOGLE_JSON' env var)."
            )

        return gspread.authorize(creds)

    def write_data(self, worksheet_name: str, data: list, header_list: list = None):
        try:
            ws = self.sheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            print(f"[GSheet] Tab '{worksheet_name}' not found. Creating...")
            ws = self.sheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")
            header = (
                header_list
                if header_list
                else [
                    "date_ist",
                    "time_ist",
                    "location",
                    "lat",
                    "lon",
                    "temp_c",
                    "humidity",
                    "pressure_mb",
                    "windspeed_kph",
                    "visibility_km",
                    "condition_text",
                    "aqi_index",
                    "pm2_5",
                    "pm10",
                    "co",
                    "no2",
                ]
            )
            ws.append_row(header)

        if data:
            ws.append_rows(data, value_input_option="USER_ENTERED")
            print(f"[GSheet] Appended {len(data)} rows to {worksheet_name}")