import requests
import json
import time
import logging
from .config import Config

logger = logging.getLogger(__name__)


class OCMClient:
    def __init__(self):
        self.api_key = Config.API_KEY
        self.headers = {"User-Agent": Config.USER_AGENT, "X-API-Key": self.api_key}

    def get_all_countries(self):
        """Fetch list of all countries to iterate over."""
        url = "https://api.openchargemap.io/v3/referencedata"
        try:
            response = requests.get(
                url, headers=self.headers, params={"output": "json"}
            )
            response.raise_for_status()
            data = response.json()
            countries = data.get("Countries", [])
            logger.info(f"Fetched {len(countries)} countries from reference data.")
            return countries
        except Exception as e:
            logger.error(f"Failed to fetch country list: {e}")
            return []

    def fetch_pois_by_country(self, country_code):
        """Fetch POIs for a specific country."""
        url = Config.BASE_URL
        params = {
            "output": "json",
            "countrycode": country_code,
            "maxresults": Config.MAX_RESULTS_PER_REQUEST,
            "compact": "true",
            "verbose": "false",
        }

        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(
                    url, headers=self.headers, params=params, timeout=30
                )
                if response.status_code == 429:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Rate limited (429). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                data = response.json()
                logger.info(f"Fetched {len(data)} stations for {country_code}")
                return data
            except requests.exceptions.RequestException as e:
                logger.error(
                    f"Error fetching data for {country_code} (Attempt {attempt+1}/{retries}): {e}"
                )
                time.sleep(1)

        return []

    def fetch_reference_data(self):
        """Fetch all necessary reference data maps (Countries, Operators, etc.)."""
        logger.info("Fetching Reference Data (Maps)...")
        maps = {}

        # Categories to fetch
        refs = {
            "Countries": "Country",  # API returns list of Country objects
            "Operators": "OperatorInfo",
            "ConnectionTypes": "ConnectionType",
            "UsageTypes": "UsageType",
            "StatusTypes": "StatusType",
        }

        url = "https://api.openchargemap.io/v3/referencedata"

        try:
            response = requests.get(
                url, headers=self.headers, params={"output": "json"}
            )
            response.raise_for_status()
            data = response.json()

            # Process each category into a Lookup Dict: {ID: Title}
            for key, api_field in refs.items():
                items = data.get(key, [])
                lookup = {}
                for item in items:
                    # Country needs special handling if we want full title
                    title = item.get("Title")
                    if not title and key == "Countries":
                        title = item.get("Title")  # Countries have Title

                    id_val = item.get("ID")
                    if id_val and title:
                        lookup[id_val] = title

                maps[key] = lookup
                logger.info(f"Loaded {len(lookup)} {key}")

            return maps

        except Exception as e:
            logger.error(f"Failed to fetch reference data: {e}")
            return {}

    def fetch_global_data(self):
        """Orchestrate the global fetch by iterating countries."""
        # 1. Get Countries
        countries = self.get_all_countries()
        all_data = []

        # 2. Iterate and Fetch
        # Sort countries by ID or ISOCode to be systematic
        for country in countries:
            iso_code = country.get("ISOCode")
            if not iso_code:
                continue

            stations = self.fetch_pois_by_country(iso_code)
            if stations:
                all_data.extend(stations)

            # Be nice to the API
            time.sleep(0.1)

        return all_data
