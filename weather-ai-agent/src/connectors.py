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