from datetime import datetime, timedelta
import pytz
from typing import List, Tuple
from config.settings import TARGET_HOURS, DATE_FORMAT_OUTPUT, TIMEZONE

IST = pytz.timezone(TIMEZONE)

def generate_target_timestamps(start_date: str, end_date: str) -> List[datetime]:
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    timestamps = []
    current_date = start
    while current_date <= end:
        for hour in TARGET_HOURS:
            dt = datetime.combine(current_date, datetime.min.time())
            dt = dt.replace(hour=hour)
            dt_aware = IST.localize(dt)
            timestamps.append(dt_aware)
        current_date += timedelta(days=1)
    return timestamps