import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from config.settings import (
    LOCATIONS,
    REQUEST_DELAY_SECONDS,
    TARGET_HOURS,
    DATE_FORMAT_OUTPUT,
    TIME_FORMAT_OUTPUT,
)
from src.utils import get_quarter_dates
from src.connectors import GoogleSheetConnector
from config.strategies import EnterpriseLoadBalancer


class QuarterlyBatchProcessor:
    """
    Worker Process responsible for a specific Quarter (Q1-Q4).
    Refactored to fetch FULL DAYs to capture AQI data correctly.
    """

    def __init__(self, quarter: int, year: int, load_balancer: EnterpriseLoadBalancer):
        self.quarter = quarter
        self.year = year
        self.lb = load_balancer
        self.connector = GoogleSheetConnector()
        self.worksheet_name = f"Q{quarter}_{year}"

        # Get date range as strings
        self.start_date_str, self.end_date_str = get_quarter_dates(year, quarter)
        print(
            f"[Worker Q{quarter}] Initialized: {self.start_date_str} -> {self.end_date_str}"
        )

    