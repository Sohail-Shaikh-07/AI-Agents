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

    def fetch_day(self, date_iso: str):
        target_dt = datetime.strptime(date_iso, "%Y-%m-%d").date()
        today = datetime.now().date()

        if target_dt > (today + timedelta(days=10)):
            return None

        if target_dt < (today - timedelta(days=5)):
            weather_url = "https://archive-api.open-meteo.com/v1/archive"
        else:
            weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": date_iso,
            "end_date": date_iso,
            "hourly": "temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,visibility,uv_index,weather_code",
            "timezone": "auto",
        }

        aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        aqi_params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": date_iso,
            "end_date": date_iso,
            "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,us_aqi",
            "timezone": "auto",
        }

        try:
            headers = {"User-Agent": "DelhiWeatherAgent/2.0 (hoodrobins098@gmail.com)"}
            w_res = requests.get(
                weather_url, params=weather_params, headers=headers, timeout=10
            )
            a_res = requests.get(
                aqi_url, params=aqi_params, headers=headers, timeout=10
            )

            if w_res.status_code != 200 or a_res.status_code != 200:
                print(f"API Error: W={w_res.status_code} A={a_res.status_code}")
                return None

            w_data = w_res.json()
            a_data = a_res.json()

            merged = {}
            if "hourly" in w_data and "hourly" in a_data:
                for i in range(len(w_data["hourly"]["time"])):
                    full_data = {
                        "temp": w_data["hourly"]["temperature_2m"][i],
                        "humidity": w_data["hourly"]["relative_humidity_2m"][i],
                        "pressure": w_data["hourly"]["surface_pressure"][i],
                        "windspeed": w_data["hourly"]["wind_speed_10m"][i],
                        "visibility": w_data["hourly"]["visibility"][i],
                        "uvindex": w_data["hourly"]["uv_index"][i],
                        "code": w_data["hourly"]["weather_code"][i],
                        "aqi": a_data["hourly"]["us_aqi"][i],
                        "pm2_5": a_data["hourly"]["pm2_5"][i],
                        "pm10": a_data["hourly"]["pm10"][i],
                        "co": a_data["hourly"]["carbon_monoxide"][i],
                        "no2": a_data["hourly"]["nitrogen_dioxide"][i],
                    }
                    merged[i] = full_data
            return merged
        except Exception as e:
            print(f"Error fetching {date_iso}: {e}")
            return None
