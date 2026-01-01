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
        
    def run(self, log_calback=None):
        current = self.start_date
        batch_buffer = []

        while current <= self.end_date:
            date_iso = current.strftime("%Y-%m-%d")
            if log_calback:
                log_calback(f"Processing {date_iso}...")

            hourly_map = self.fetch_day(date_iso)

            if hourly_map:
                # Dynamic Interval Loop
                target_range = range(0, 24, self.interval)
                for target_h in target_range:
                    if target_h in hourly_map:
                        data = hourly_map[target_h]
                        ts_obj = datetime.combine(
                            current, datetime.min.time().replace(hour=target_h)
                        )

                        row = [
                            ts_obj.strftime(DATE_FORMAT_OUTPUT),
                            ts_obj.strftime(TIME_FORMAT_OUTPUT),
                            self.location,
                            self.lat,
                            self.lon,
                        ]
                        condition_text = get_wmo_description(data["code"])

                        if "temp" in self.columns:
                            row.append(data["temp"])
                        if "humidity" in self.columns:
                            row.append(data["humidity"])
                        if "pressure" in self.columns:
                            row.append(data["pressure"])
                        if "wind" in self.columns:
                            row.append(data["windspeed"])
                        if "visibility" in self.columns:
                            row.append(
                                data["visibility"] / 1000
                                if data["visibility"] is not None
                                else 0
                            )
                        # if "uv" in self.columns: row.append(data["uvindex"])  <-- Removed

                        row.append(condition_text)

                        if "aqi" in self.columns:
                            row.append(data["aqi"])
                            row.append(data["pm2_5"])
                            row.append(data["pm10"])
                            row.append(data["co"])
                            row.append(data["no2"])

                        batch_buffer.append(row)

            current += timedelta(days=1)
            time.sleep(0.2)

        # Build Dynamic Header
        header = ["date_ist", "time_ist", "location", "lat", "lon"]
        if "temp" in self.columns:
            header.append("temp_c")
        if "humidity" in self.columns:
            header.append("humidity")
        if "pressure" in self.columns:
            header.append("pressure_mb")
        if "wind" in self.columns:
            header.append("windspeed_kph")
        if "visibility" in self.columns:
            header.append("visibility_km")

        header.append("condition_text")

        if "aqi" in self.columns:
            header.extend(["aqi_index", "pm2_5", "pm10", "co", "no2"])

        if log_calback:
            log_calback(
                f"Writing {len(batch_buffer)} rows to Sheet '{self.worksheet_name}'..."
            )
        self.connector.write_data(self.worksheet_name, batch_buffer, header_list=header)
        if log_calback:
            log_calback("Job Completed Successfully!")
