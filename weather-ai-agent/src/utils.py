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

def format_for_csv(dt: datetime) -> str:
    return dt.strftime(DATE_FORMAT_OUTPUT)

WMO_CODE_MAP = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 47: "Depositing rime fog", 48: "Depositing rime fog",
    51: "Drizzle: Light", 53: "Drizzle: Moderate", 55: "Drizzle: Dense",
    56: "Freezing Drizzle: Light", 57: "Freezing Drizzle: Dense",
    61: "Rain: Slight", 63: "Rain: Moderate", 65: "Rain: Heavy",
    66: "Freezing Rain: Light", 67: "Freezing Rain: Heavy",
    71: "Snow fall: Slight", 73: "Snow fall: Moderate", 75: "Snow fall: Heavy",
    77: "Snow grains", 80: "Rain showers: Slight", 81: "Rain showers: Moderate",
    82: "Rain showers: Violent", 85: "Snow showers: Slight", 86: "Snow showers: Heavy",
    95: "Thunderstorm: Slight or moderate", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}

def get_wmo_description(code: int) -> str:
    return WMO_CODE_MAP.get(code, "Unknown")