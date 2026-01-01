import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from config.settings import (
    TARGET_HOURS,
    DATE_FORMAT_OUTPUT,
    TIME_FORMAT_OUTPUT,
)
from src.utils import get_wmo_description
from src.connectors import GoogleSheetConnector


class DynamicProcessor:
    """
    New Processor for the Web UI.
    Fetches data for a SINGLE location over a CUSTOM date range.
    """

    def __init__(
        self,
        location: str,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
        interval: int = 1,
        columns: list = None,
    ):
        self.location = location
        self.lat = lat
        self.lon = lon
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        self.interval = interval
        self.columns = columns if columns else []

        safe_loc = "".join(c for c in location if c.isalnum())
        self.worksheet_name = f"{safe_loc}_{start_date.replace('-', '')}"
        self.connector = GoogleSheetConnector()
