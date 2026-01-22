import logging
import json
import os
from src.config import Config
from src.api_client import OCMClient
from src.data_processor import DataProcessor

# Setup Logging
if not os.path.exists(Config.LOGS_DIR):
    os.makedirs(Config.LOGS_DIR)

logging.basicConfig(
    filename=os.path.join(Config.LOGS_DIR, "agent_execution.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# Also log to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)

logger = logging.getLogger(__name__)


def main():
    logger.info("=== Starting Global EV Charging Network Agent (V6 - JSON First) ===")

    # 0. Validate Config
    try:
        Config.validate()
    except ValueError as e:
        logger.error(str(e))
        return

    client = OCMClient()

    # 1. Fetch Reference Data (Maps)
    logger.info("Phase 0: Building Reference Maps (Countries, Operators)...")
    reference_maps = client.fetch_reference_data()
    if not reference_maps:
        logger.warning(
            "Could not fetch reference maps. Data will contain IDs instead of Names."
        )

    # 2. Extract Phase: Fetch Global Data & Save to JSON
    logger.info("Phase 1: Extraction (Fetch & Save Raw JSON)...")
    all_data = client.fetch_global_data()

    if not all_data:
        logger.error("No data fetched. Aborting.")
        return

    # SAVE RAW JSON (The Golden Copy)
    try:
        logger.info(f"Saving Raw Data to {Config.RAW_DATA_FILE}...")
        with open(Config.RAW_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=None)  # Compact JSON
        logger.info("✅ Raw JSON Saved Successfully.")
    except Exception as e:
        logger.error(f"Failed to save raw JSON: {e}")
        # We continue to processing even if save fails? No, ELT pattern implies save first.
        # But we have the data in memory, so we can proceed.

    # 3. Transform Phase: Convert JSON to CSV
    logger.info("Phase 2: Transformation (JSON -> CSV)...")

    # (Optional: Reload from file to verify integrity, or just use memory)
    # Using memory is faster. We trust the save worked.

    processor = DataProcessor(reference_maps=reference_maps)
    df = processor.process_and_save(all_data)

    if df is not None:
        logger.info("Phase 2 Complete.")
        logger.info("=== Execution Success ===")
        logger.info(f"Final Dataset: {Config.FINAL_CSV_FILE}")
        logger.info(f"Total Stations: {len(df)}")
        if "Country" in df.columns:
            logger.info(f"Countries Covered: {df['Country'].nunique()}")
            logger.info(f"Sample Countries: {df['Country'].unique()[:5]}")
    else:
        logger.error("Phase 2 Failed.")


if __name__ == "__main__":
    main()
