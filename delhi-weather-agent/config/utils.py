from datetime import datetime, timedelta
import pytz
from typing import List, Tuple
from config.settings import TARGET_HOURS, DATE_FORMAT_OUTPUT, TIMEZONE

# Professional Timezone Handling
IST = pytz.timezone(TIMEZONE)


def generate_target_timestamps(start_date: str, end_date: str) -> List[datetime]:
    """
    Generates target 3-hour intervals in IST.
    """
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    timestamps = []

    current_date = start
    while current_date <= end:
        for hour in TARGET_HOURS:
            dt = datetime.combine(current_date, datetime.min.time())
            dt = dt.replace(hour=hour)
            # Localize to IST
            dt_aware = IST.localize(dt)
            timestamps.append(dt_aware)
        current_date += timedelta(days=1)

    return timestamps


def format_for_csv(dt: datetime) -> str:
    """
    Formats datetime for Sheet storage.
    """
    return dt.strftime(DATE_FORMAT_OUTPUT)


def get_quarter_dates(year: int, quarter: int) -> Tuple[str, str]:
    if quarter == 1:
        return (f"{year}-01-01", f"{year}-03-31")
    elif quarter == 2:
        return (f"{year}-04-01", f"{year}-06-30")
    elif quarter == 3:
        return (f"{year}-07-01", f"{year}-09-30")
    elif quarter == 4:
        return (f"{year}-10-01", f"{year}-12-31")
    raise ValueError("Invalid Quarter")
