import requests
import time
import json
from src.config.config_manager import ConfigManager

class PlacesEngine:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.base_url = "https://google.serper.dev/places"

    def fetch_for_city_category(self, city, category):
        """
        Fetches business data for a given Category in a City using Serper API.
        Uses 2 query variations for efficiency.
        """
        api_key = self.config.get_serper_key()

        # 1. Generate Query Variations
        queries = [
            f"{category} in {city} best",
            f"{category} in {city} near market",
        ]

        all_places = {}

        for q in queries:
            print(f"🔎 Searching: '{q}'...")

            payload = json.dumps({"q": q})
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }

            try:
                response = requests.post(self.base_url, headers=headers, data=payload)

                # Check for 403/400 explicitly
                if response.status_code in [403, 401, 400]:
                    print(f"❌ API Error {response.status_code}: {response.text}")
                    return None

                data = response.json()
                places = data.get("places", [])

                if not places:
                    print(f"   ⚠️ No results for '{q}'")

                # Deduplicate
                for p in places:
                    pid = p.get("cid") or p.get("place_id") or (p.get("title", "") + p.get("address", ""))
                    if pid and pid not in all_places:
                        all_places[pid] = self._normalize_place(p, city, category)

            except Exception as e:
                print(f"❌ Network Error: {e}")
                time.sleep(2)

        unique_results = list(all_places.values())
        print(f"✅ Found {len(unique_results)} unique places for '{category}' in '{city}'.")
        return unique_results

    def _normalize_place(self, p, city, category):
        """
        Standardizes the Serper result into our 11-column format.
        """
        return {
            "NAME": p.get("title", ""),
            "CATEGORY": category,
            "ADDRESS": p.get("address", ""),
            "CITY": city,
            "STATE": "",  # To be filled by LLM or inferred
            "PHONE": p.get("phoneNumber", ""),
            "WEBSITE": p.get("website", ""),
            "HASWEBSITE": "Yes" if p.get("website") else "No",
            "RATING": p.get("rating", 0),
            "DATASOURCE": "Serper/GoogleMaps"
        }
