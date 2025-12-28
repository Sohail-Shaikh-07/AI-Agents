import time
import json
import os
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from src.config.config_manager import ConfigManager


class SheetManager:
    """
    Handles robust interactions with Google Sheets for the Agent.
    """

    def __init__(self, config_manager):
        self.config = config_manager
        self.client = None
        self.current_spreadsheet = None
        self.sheet_url = self.config.google_sheet_url

        # Priority: Env JSON String > File Path
        self.creds_json = self.config.google_credentials_json
        self.creds_path = self.config.google_sheets_creds_path

        self.expected_columns = [
            "SR_NO",
            "NAME",
            "CATEGORY",
            "ADDRESS",
            "CITY",
            "STATE",
            "PHONE",
            "WEBSITE",
            "HASWEBSITE",
            "RATING",
            "DATASOURCE",
        ]

        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            creds_dict = None

            # 1. Try JSON String from Env (Cloud native)
            if self.creds_json:
                print("🔑 Authenticating via GOOGLE_CREDENTIALS_JSON env var...")
                try:
                    creds_dict = json.loads(self.creds_json)
                    # Fix: Handle escaped newlines in private_key if loaded from env
                    if "private_key" in creds_dict:
                        pk = creds_dict["private_key"]
                        if "\\n" in pk:
                            creds_dict["private_key"] = pk.replace("\\n", "\n")

                except json.JSONDecodeError:
                    print("❌ Error: GOOGLE_CREDENTIALS_JSON is not valid JSON.")

            # 2. Fallback to File
            if not creds_dict:
                if os.path.exists(self.creds_path):
                    print(f"📂 Authenticating via file: {self.creds_path}")
                    with open(self.creds_path, "r") as f:
                        creds_dict = json.load(f)
                else:
                    raise FileNotFoundError(
                        "No valid Credentials found (Checked Env and File)."
                    )

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            self.creds = creds
            self.client = gspread.authorize(creds)
            print("✅ Sheets Manager: Authenticated.")

        except Exception as e:
            print(f"❌ Sheets Auth Error: {e}")
            raise e

    def append_data(self, data: list, worksheet_name: str = "Dataset") -> bool:
        """
        Appends a list of dictionaries to the active sheet.
        Handles Serial Number generation automatically.
        """
        if not data:
            return True

        try:
            # Connect
            if self.current_spreadsheet:
                spreadsheet = self.current_spreadsheet
            elif "docs.google.com" in self.sheet_url:
                spreadsheet = self.client.open_by_url(self.sheet_url)
            else:
                spreadsheet = self.client.open_by_key(self.sheet_url)

            # Get Active Worksheet (Auto-Rolling)
            ws = self._get_active_worksheet(spreadsheet, worksheet_name)

            # Calculate SR_NO
            existing_rows = len(ws.col_values(1))
            start_id = existing_rows
            if existing_rows == 0:
                ws.append_row(self.expected_columns)
                start_id = 1
                self._format_header(ws)

            # Prepare rows
            rows_to_add = []
            for i, record in enumerate(data):
                record["SR_NO"] = start_id + i
                row = [str(record.get(col, "")) for col in self.expected_columns]
                rows_to_add.append(row)

            # Batch Append
            ws.append_rows(rows_to_add)
            print(
                f"📤 Sheets Manager: Appended {len(rows_to_add)} rows to '{ws.title}'."
            )
            return True

        except Exception as e:
            print(f"❌ Sheet Append Error: {e}")
            return False

    def switch_to_state_sheet(self, state_name: str):
        """
        Switches the active spreadsheet to one dedicated for the given state.
        Format: 'IBD_StateName' (e.g., IBD_Andhra_Pradesh)
        If it doesn't exist, it CREATES it and SHARES it with the Admin.
        """
        if not self.client:
             self._authenticate()

        safe_name = "".join(c if c.isalnum() else "_" for c in state_name)
        sheet_title = f"IBD_{safe_name}"

        try:
            print(f"🔄 Switching to Sheet: {sheet_title}...")
            self.current_spreadsheet = self.client.open(sheet_title)
            print(f"✅ Loaded existing sheet: {sheet_title}")

        except gspread.SpreadsheetNotFound:
            print(f"🆕 Creating NEW Sheet: {sheet_title}")
            try:
                self.current_spreadsheet = self.client.create(sheet_title)
                if self.config.admin_email:
                    print(f"🤝 Sharing {sheet_title} with {self.config.admin_email}...")
                    self.current_spreadsheet.share(self.config.admin_email, perm_type='user', role='writer')
                else:
                    print("⚠️ ADMIN_EMAIL not set! Sheet hidden in Service Account drive.")
            except Exception as e:
                print(f"❌ Failed to create/share sheet '{sheet_title}': {e}")
                # Fallback
                if "docs.google.com" in self.sheet_url:
                    self.current_spreadsheet = self.client.open_by_url(self.sheet_url)
                else:
                    self.current_spreadsheet = self.client.open_by_key(self.sheet_url)


    def _get_active_worksheet(self, spreadsheet, base_name: str):
        """
        Finds the first worksheet that hasn't hit the 500k row soft limit.
        Rotates: Dataset -> Dataset_2 -> Dataset_3 ...
        """
        i = 1
        while True:
            target_name = base_name if i == 1 else f"{base_name}_{i}"

            try:
                ws = spreadsheet.worksheet(target_name)
                if ws.row_count < 490000:
                    return ws

                existing_rows = len(ws.col_values(1))
                if existing_rows < 490000:
                    return ws

                print(
                    f"⚠️ Worksheet '{target_name}' is FULL ({existing_rows} rows). Checking next..."
                )
                i += 1

            except gspread.WorksheetNotFound:
                print(f"🆕 Creating New Worksheet: '{target_name}'")
                ws = spreadsheet.add_worksheet(title=target_name, rows=1000, cols=20)
                ws.append_row(self.expected_columns)
                self._format_header(ws)
                return ws

    def _format_header(self, ws):
        try:
            ws.format("A1:K1", {"textFormat": {"bold": True}})
            ws.freeze(rows=1)
        except:
            pass

    def log_dead_key(self, key_name: str, error_msg: str):
        """
        Logs a dead/expired API key to the 'Dead_Keys' worksheet.
        """
        try:
            worksheet_name = "Dead_Keys"
            try:
                ws = self.client.open_by_url(self.sheet_url).worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                ws = self.client.open_by_url(self.sheet_url).add_worksheet(
                    worksheet_name, 1000, 5
                )
                ws.append_row(["Key Name", "Error Message", "Timestamp"])
                ws.format("A1:C1", {"textFormat": {"bold": True}})

            ws.append_row(
                [key_name, error_msg, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            )
            print(f"💀 Dead Key Logged: {key_name}")

        except Exception as e:
            print(f"❌ Failed to log dead key: {e}")

    def log_district_report(self, state: str, district: str, city_stats: dict):
        """
        Logs district summary stats to 'District_Reports' worksheet.
        """
        try:
            worksheet_name = "District_Reports"
            try:
                ws = self.client.open_by_url(self.sheet_url).worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                ws = self.client.open_by_url(self.sheet_url).add_worksheet(
                    worksheet_name, 1000, 6
                )
                ws.append_row(
                    [
                        "State",
                        "District",
                        "Total Cities",
                        "Total Records",
                        "Timestamp",
                        "Stats JSON",
                    ]
                )
                ws.format("A1:F1", {"textFormat": {"bold": True}})

            total_records = sum(sum(cats.values()) for cats in city_stats.values())

            ws.append_row(
                [
                    state,
                    district,
                    len(city_stats),
                    total_records,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    json.dumps(city_stats),
                ]
            )
            print(f"📊 District Report Logged for {district}")

        except Exception as e:
            print(f"❌ Failed to log district report: {e}")
