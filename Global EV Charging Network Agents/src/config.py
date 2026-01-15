import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    API_KEY = os.getenv("Open_Charge_Map")
    BASE_URL = "https://api.openchargemap.io/v3/poi"

    # API Parameters
    MAX_RESULTS_PER_REQUEST = 100000  # API limit guidelines
    USER_AGENT = "KaggleDatasetAgent/1.0"

    # Paths
    DATA_DIR = os.path.join(os.getcwd(), "data")
    LOGS_DIR = os.path.join(os.getcwd(), "logs")
    RAW_DATA_FILE = os.path.join(DATA_DIR, "global_raw.json")
    FINAL_CSV_FILE = os.path.join(DATA_DIR, "global_ev_charging.csv")

    # Target Columns (Reference only - logic is in DataProcessor)
    CSV_COLUMNS = [
        "StationID",
        "UUID",
        "Operator",
        "OperatorID",
        "UsageType",
        "UsageCost",
        "AddressTitle",
        "AddressLine1",
        "Town",
        "StateOrProvince",
        "Postcode",
        "Country",
        "Latitude",
        "Longitude",
        "StatusType",
        "YearCreated",
        "MaxPowerKW",
        "ConnectionTypes",
    ]

    @staticmethod
    def validate():
        if not Config.API_KEY:
            raise ValueError("API Key 'Open_Charge_Map' not found in .env file.")
