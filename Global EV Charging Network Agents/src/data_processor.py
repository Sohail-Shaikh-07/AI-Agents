import pandas as pd
import json
import logging
from .config import Config
from datetime import datetime

logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self, reference_maps=None):
        self.maps = reference_maps or {}

    def _resolve(self, map_name, id_val):
        """Helper to resolve ID to String using reference maps."""
        if not id_val:
            return None
        return self.maps.get(map_name, {}).get(id_val, str(id_val))

    def _clean_text(self, text):
        """Sanitize text to prevent CSV breakage (remove newlines, tabs, quotes, COMMAS)."""
        if not text:
            return None
        # Convert to string and replace risky characters
        text = (
            str(text)
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("\t", " ")
            .replace('"', "'")
            .replace(",", ";")  
        )
        return text.strip()

    def process_and_save(self, json_data, output_filename=None):
        """Convert raw JSON list to structured CSV with ID Resolution."""
        if not json_data:
            logger.warning("No data to process.")
            return

        # Default to Config path if no filename provided
        output_file = output_filename if output_filename else Config.FINAL_CSV_FILE

        logger.info(f"Processing {len(json_data)} records...")

        processed_rows = []

        for record in json_data:
            row = {}

            # Identity
            row["StationID"] = record.get("ID")
            row["UUID"] = record.get("UUID")
            row["DataProviderID"] = record.get("DataProviderID")

            # Operator
            op_id = record.get("OperatorID")
            row["Operator"] = self._clean_text(self._resolve("Operators", op_id))

            # Usage
            usage_id = record.get("UsageTypeID")
            row["UsageType"] = self._clean_text(self._resolve("UsageTypes", usage_id))
            row["UsageCost"] = self._clean_text(record.get("UsageCost"))

            # Address
            addr = record.get("AddressInfo", {}) or {}
            row["AddressTitle"] = self._clean_text(addr.get("Title"))
            row["AddressLine1"] = self._clean_text(addr.get("AddressLine1"))
            row["Town"] = self._clean_text(addr.get("Town"))
            row["StateOrProvince"] = self._clean_text(addr.get("StateOrProvince"))
            row["Postcode"] = self._clean_text(addr.get("Postcode"))

            # Country
            country_id = addr.get("CountryID")
            row["Country"] = self._clean_text(self._resolve("Countries", country_id))

            row["Latitude"] = addr.get("Latitude")
            row["Longitude"] = addr.get("Longitude")

            # Connections
            connections = record.get("Connections", []) or []

            max_power = 0
            connection_types = set()
            fast_chargers = 0

            if connections:
                for conn in connections:
                    power = conn.get("PowerKW")
                    if power and isinstance(power, (int, float)):
                        if power > max_power:
                            max_power = power
                        if power >= 40:
                            fast_chargers += 1

                    c_type_id = conn.get("ConnectionTypeID")
                    c_title = self._resolve("ConnectionTypes", c_type_id)
                    if c_title:
                        connection_types.add(self._clean_text(c_title))

            row["MaxPowerKW"] = max_power
            row["FastChargeCount"] = fast_chargers
            row["ConnectionTypes"] = ", ".join(sorted(connection_types))

            status_id = record.get("StatusTypeID")
            row["StatusType"] = self._clean_text(
                self._resolve("StatusTypes", status_id)
            )

            # --- V5 Changes: Date Handling ---
            date_created_str = record.get("DateCreated")
            year_created = None

            if date_created_str:
                try:
                    # Parse simplified date string if possible
                    dt = pd.to_datetime(date_created_str, errors="coerce")
                    if pd.notnull(dt):
                        y = dt.year
                        # Filter Garbage Years (e.g., 1, 1000, 2030)
                        if 2005 <= y <= 2027:
                            year_created = int(y)
                except Exception:
                    pass

            row["YearCreated"] = year_created

            processed_rows.append(row)

        # Create DataFrame
        df = pd.DataFrame(processed_rows)

        # Save to CSV
        # output_file is determined at start of function
        df.to_csv(output_file, index=False)
        logger.info(
            f"Successfully saved dataset with {len(df)} rows to {output_file}"
        )

        return df
