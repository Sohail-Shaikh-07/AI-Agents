import os
import gspread
import pandas as pd
import json
import base64
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

        self.sheet = self.client.open_by_key(GOOGLE_SHEET_ID)
        print(f"[GSheet] Connected to Sheet: {self.sheet.title}")

    def _authenticate(self):
        """Authenticates using Service Account JSON."""
        # 1. Dev Mode: Look for local file
        if os.path.exists("service_account.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "service_account.json", self.scope
            )
        # 2. Prod Mode (Render): Look for Base64 Env Var
        elif os.getenv(GOOGLE_JSON_ENV_VAR):
            json_str = base64.b64decode(os.getenv(GOOGLE_JSON_ENV_VAR)).decode("utf-8")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                json.loads(json_str), self.scope
            )
        else:
            raise FileNotFoundError(
                "Service Account credentials not found (Checked 'service_account.json' and 'GOOGLE_JSON' env var)."
            )

        return gspread.authorize(creds)
