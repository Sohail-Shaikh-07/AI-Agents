import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()


class ConfigManager:
    """
    Standard Configuration Manager (Single Key Version).
    """

    def __init__(self, sheet_manager=None):
        self.sheet_manager = sheet_manager

        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.google_sheet_url = os.getenv("GOOGLE_SHEET_URL")
        self.google_credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        self.google_sheets_creds_path = os.getenv(
            "GOOGLE_SHEETS_CREDENTIALS_PATH", "credentials.json"
        )
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.resend_api_key = os.getenv("RESEND_API_KEY")
        self.admin_email = os.getenv("ADMIN_EMAIL")  # Required for sharing

        # Feature Flags
        self.enable_llm = os.getenv("ENABLE_LLM", "False").lower() == "true"

        if not self.serper_api_key:
            print("⚠️ Warning: SERPER_API_KEY not found.")

    def set_sheet_manager(self, sheet_manager):
        self.sheet_manager = sheet_manager

    def get_serper_key(self):
        return self.serper_api_key

    # Alias for compatibility if needed, but we should update usage
    def get_current_serper_key(self):
        return self.serper_api_key
