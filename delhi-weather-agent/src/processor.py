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

    def fetch_full_day_data(self, location_name: str, lat_lon: str, date_str: str):
        """
        Fetches the entire 24-hour timeline for a single day.
        Optimized: 1 API Call = 24 hours of data (we extract 8).
        """
        lat, lon = lat_lon.split(",")
        # Visual Crossing Daily Call: .../YYYY-MM-DD/YYYY-MM-DD

        while True:
            api_key = self.lb.get_current_key()
            url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}/{date_str}/{date_str}"
            params = {
                "key": api_key,
                "unitGroup": "metric",
                "include": "days,hours",  # CRITICAL: Needed for AQI
                "elements": "datetime,temp,humidity,pressure,windspeed,visibility,uvindex,conditions,description,aqi,pm2.5,pm10,co,no2",
            }

            try:
                response = requests.get(url, params=params, timeout=20)

                if response.status_code == 200:
                    self.lb.report_success()
                    return response.json()

                elif response.status_code == 429:
                    print(
                        f"[Worker Q{self.quarter}] Rate Limit (429) detected. Executing Credential Rotation Strategy..."
                    )
                    self.lb.rotate_key()
                    time.sleep(2)

                elif response.status_code >= 500:
                    print(
                        f"[Worker Q{self.quarter}] Server Error {response.status_code}. Retrying..."
                    )
                    time.sleep(5)
                else:
                    print(
                        f"[Worker Q{self.quarter}] Fatal Error {response.status_code}: {response.text}"
                    )
                    return None

            except Exception as e:
                print(f"[Worker Q{self.quarter}] Network Error: {str(e)}")
                time.sleep(5)

        return None

    def fetch_open_meteo_aqi(self, lat: float, lon: float, date_str: str):
        """
        Fetches AQI data from Open-Meteo for a specific day.
        Returns a dictionary keyed by hour (0-23) containing AQI metrics.
        """
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi,european_aqi",
            "start_date": date_str,
            "end_date": date_str,
            "timezone": "auto",  # Auto match location time
        }

        try:
            r = requests.get(url, params=params, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if "hourly" in data:
                    h_data = data["hourly"]
                    # Pivot data: {hour_idx: {pm10: val, ...}}
                    hourly_map = {}
                    # Assuming 24 hours returned
                    length = len(h_data["time"])
                    for i in range(length):
                        # Extract hour from ISO string "YYYY-MM-DDTHH:MM" -> int(HH)
                        # But simpler: index 0 is 00:00, index 1 is 01:00 usually.
                        # Let's verify by parsing the time string if needed, but index mapping is robust for single day.

                        hourly_map[i] = {
                            "pm10": h_data["pm10"][i],
                            "pm2_5": h_data["pm2_5"][i],
                            "co": h_data["carbon_monoxide"][i],
                            "no2": h_data["nitrogen_dioxide"][i],
                            "so2": h_data["sulphur_dioxide"][i],
                            "ozone": h_data["ozone"][i],
                            "us_aqi": h_data["us_aqi"][i],
                            "eu_aqi": h_data["european_aqi"][i],
                        }
                    return hourly_map
            else:
                print(f"[OpenMeteo] Error {r.status_code}: {r.text}")
        except Exception as e:
            print(f"[OpenMeteo] Exception: {e}")

        return {}

    def process_day(self, current_date: datetime):
        """
        Fetches full day for all locations, extracts target hours.
        Hybrid: VC for Weather, Open-Meteo for AQI.
        """
        date_iso = current_date.strftime("%Y-%m-%d")
        day_rows = []

        for loc_name, lat_lon in LOCATIONS.items():
            print(f"  > Fetching {loc_name} for {date_iso}...")

            # 1. Fetch Weather (Visual Crossing)
            data = self.fetch_full_day_data(loc_name, lat_lon, date_iso)

            # 2. Fetch AQI (Open-Meteo)
            lat_str, lon_str = lat_lon.split(",")
            aqi_data_map = self.fetch_open_meteo_aqi(
                float(lat_str), float(lon_str), date_iso
            )

            if data and "days" in data and len(data["days"]) > 0:
                day_data = data["days"][0]
                hours_data = day_data.get("hours", [])

                # Extract only TARGET_HOURS (0, 3, 6...)
                for target_h in TARGET_HOURS:
                    if target_h < len(hours_data):
                        h_data = hours_data[target_h]

                        # Get AQI data for this specific hour
                        aqi_h = aqi_data_map.get(target_h, {})

                        # Construct Timestamp Object
                        ts_obj = datetime.combine(
                            current_date, datetime.min.time().replace(hour=target_h)
                        )

                        # Split Date and Time
                        date_str = ts_obj.strftime(DATE_FORMAT_OUTPUT)
                        time_str = ts_obj.strftime(TIME_FORMAT_OUTPUT)

                        # Fallback for AQI if OpenMeteo failed
                        # Use US AQI as primary 'aqi_index'
                        final_aqi = aqi_h.get("us_aqi")
                        if final_aqi is None:
                            final_aqi = h_data.get(
                                "aqi"
                            )  # Try VC fallback (unlikely work)

                        final_pm25 = aqi_h.get("pm2_5")
                        if final_pm25 is None:
                            final_pm25 = h_data.get("pm2p5")

                        final_pm10 = aqi_h.get("pm10")
                        if final_pm10 is None:
                            final_pm10 = h_data.get("pm10")

                        row = [
                            date_str,
                            time_str,
                            loc_name,
                            lat_lon.split(",")[0],
                            lat_lon.split(",")[1],
                            h_data.get("temp"),
                            h_data.get("humidity"),
                            h_data.get("pressure"),
                            h_data.get("windspeed"),
                            h_data.get("visibility"),
                            h_data.get("uvindex"),
                            h_data.get("conditions"),
                            h_data.get("description"),
                            # AQI Data (Hybrid)
                            final_aqi,  # aqi_index
                            final_pm25,  # pm2_5
                            final_pm10,  # pm10
                            aqi_h.get(
                                "co"
                            ),  # co (µg/m³) vs VC's co? OpenMeteo is good.
                            aqi_h.get("no2"),  # no2
                        ]
                        day_rows.append(row)

            time.sleep(REQUEST_DELAY_SECONDS)

        return day_rows

    def run(self):
        """
        Iterates through every DAY in the quarter.
        """
        print(f"[Worker Q{self.quarter}] Starting Optimized Daily Fetch Job...")

        start = datetime.strptime(self.start_date_str, "%Y-%m-%d").date()
        end = datetime.strptime(self.end_date_str, "%Y-%m-%d").date()

        current = start
        batch_buffer = []

        while current <= end:
            print(f"[Worker Q{self.quarter}] Processing Date: {current}")
            new_rows = self.process_day(current)
            batch_buffer.extend(new_rows)

            # Write buffer every 2 days (~96 rows) to minimize API writes but keep safe
            if len(batch_buffer) >= 90:
                self.connector.write_data(self.worksheet_name, batch_buffer)
                batch_buffer = []

            current += timedelta(days=1)

        # Final Flush
        if batch_buffer:
            self.connector.write_data(self.worksheet_name, batch_buffer)

        print(f"[Worker Q{self.quarter}] Job Complete!")
