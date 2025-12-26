import os
import glob
import json
import time
import sys
from src.config.config_manager import ConfigManager
from src.places_engine import PlacesEngine
from src.sheet_manager.sheet_manager import SheetManager
from src.persistence import PersistenceManager
from src.email_notifier.notifier import Notifier
from src.llm.llm_engine import LLMEngine


# Ensure current directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def load_inputs():
    """
    Loads all JSON state files from 'inputs/states/_.json'.
    Returns a unified list of (State, District, [Cities]) tuples.
    """
    hierarchy = [] # Path to states folder
    search_path = os.path.join(os.path.dirname(__file__), "inputs", "states", "_", "\*.json")
    files = glob.glob(search_path)

    # Fallback to direct files if any
    if not files:
        search_path_flat = os.path.join(
            os.path.dirname(__file__), "inputs", "states", "*.json"
        )
        files = glob.glob(search_path_flat)

    if not files:
        print(f"❌ No Input Files found.")
        return [], []

    files.sort()
    print(f"📂 Loading Inputs from {len(files)} files...")

    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)

            root_keys = list(data.keys())
            if not root_keys:
                continue

            state_name = root_keys[0]

            # ---------------------------------------------------------
            # SHARDING LOGIC: Filter by TARGET_STATES env var {easy to deploy multiple agent with target states}
            # ---------------------------------------------------------
            target_states_env = os.getenv("TARGET_STATES")
            if target_states_env:
                targets = [t.strip().lower() for t in target_states_env.split(",")]
                if state_name.lower() not in targets:
                    print(f"⏭️ Skipping State: {state_name}")
                    continue
            # ---------------------------------------------------------

            root = data[state_name]
            districts_data = root.get("data", [])

            for d_node in districts_data:
                d_name = d_node.get("district", "Unknown")
                cities = d_node.get("places", [])
                if cities:
                    hierarchy.append((state_name, d_name, cities))

        except Exception as e:
            print(f"❌ Error reading {fpath}: {e}")

    # Load Categories
    cat_path = os.path.join(os.path.dirname(__file__), "inputs", "categories.json")
    try:
        with open(cat_path, "r", encoding="utf-8") as f:
            categories = json.load(f)
    except:
        categories = ["Gym", "Spa", "Restaurant"] # Fallback

    return hierarchy, categories

def main():
    print("🚀 Starting Indian Business Scraper Agent...")

    # 1. Init Config & Modules
    config = ConfigManager()
    places = PlacesEngine(config)
    sheets = SheetManager(config)


    # Passing 'sheets' to PersistenceManager so it can save state to the cloud
    memory = PersistenceManager(sheets)
    notify = Notifier(config, sheet_manager=sheets)

    # 2. Load Data
    hierarchy, categories = load_inputs()
    if not hierarchy:
        print("❌ No data to process based on current filter.")
        return

    print(f"📊 Total Districts to Process: {len(hierarchy)}")

    # 3. Load Progress
    progress = memory.load_progress()
    p_dist_idx = progress.get("dist_idx", 0)
    current_dist_idx = p_dist_idx
    print(f"📖 Resuming from District Index: {p_dist_idx}")

    # 3. Main Loop
    for state, district, cities in hierarchy:

        # Ensure we are logged into the correct State Sheet (Auto-Switch)
        sheets.switch_to_state_sheet(state)

        print(f"\n🏗️  Starting District: {district}, {state} ({len(cities)} cities)")

        for city in cities:
            print(f"  🏙️  City: {city}")

            for category in categories:
                print(f"    🔍 Category: {category}")

                # Fetch
                results = places.fetch_for_city_category(city, category)

                if results:
                    # Save
                    sheets.append_data(results)
                    print(f"    ✅ Saved {len(results)} rows.")

                time.sleep(1) # Polite delay


if __name__ == "__main__":
    main()
