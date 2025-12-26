import json
import os
import gspread
from datetime import datetime
from src.sheet_manager.sheet_manager import SheetManager

class PersistenceManager:
    """
    Manages the 'Brain' of the agent.

    CLOUD UPDATE:
    Instead of local 'progress.json' (which gets deleted on Vercel/Render),
    we store the state in a Google Sheet tab named 'System_Memory'.
    """

    def __init__(self, sheet_manager):
        self.sheet_manager = sheet_manager
        self.worksheet_name = "System_Memory"
        self._init_memory()

    def _init_memory(self):
        """Ensures the memory tab exists."""
        try:
            # Try to get the tab
            ws = self.sheet_manager.client.open_by_url(
                self.sheet_manager.sheet_url
            ).worksheet(self.worksheet_name)
        except gspread.WorksheetNotFound:
            # Create it
            ws = self.sheet_manager.client.open_by_url(
                self.sheet_manager.sheet_url
            ).add_worksheet(self.worksheet_name, 10, 5)
            ws.append_row(["KEY", "VALUE", "LAST_UPDATED", "DESCRIPTION"])
            # Initialize default rows
            self.save_progress(0, 0, 0, 0)

    def save_progress(self, state_idx, dist_idx, city_idx, cat_idx):
        """
        Saves indices to the sheet.
        We just overwrite row 2 with the JSON blob or specific columns.
        Let's use a JSON blob in Cell B2 for simplicity.
        """
        data = {
            "state_idx": state_idx,
            "dist_idx": dist_idx,
            "city_idx": city_idx,
            "cat_idx": cat_idx,
        }

        try:
            ws = self.sheet_manager.client.open_by_url(
                self.sheet_manager.sheet_url
            ).worksheet(self.worksheet_name)
            # Update Cell B2 (Value)
            ws.update_acell("A2", "CURRENT_PROGRESS")
            ws.update_acell("B2", json.dumps(data))
            ws.update_acell("C2", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            ws.update_acell("D2", "Tracks where the agent stopped")
        except Exception as e:
            print(f"⚠️ Persistence Save Failed: {e}")

    def load_progress(self):
        try:
            ws = self.sheet_manager.client.open_by_url(
                self.sheet_manager.sheet_url
            ).worksheet(self.worksheet_name)
            val = ws.acell("B2").value
            if val:
                return json.loads(val)
            else:
                return {"state_idx": 0, "dist_idx": 0, "city_idx": 0, "cat_idx": 0}
        except Exception as e:
            print(f"⚠️ Persistence Load Failed (Defaulting to 0): {e}")
            return {"state_idx": 0, "dist_idx": 0, "city_idx": 0, "cat_idx": 0}
