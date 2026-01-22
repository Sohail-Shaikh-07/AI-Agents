import json
import logging
import os
from src.config import Config
from src.api_client import OCMClient
from src.data_processor import DataProcessor

# Setup Logging
if not os.path.exists(Config.LOGS_DIR):
    os.makedirs(Config.LOGS_DIR)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


def convert_json():
    logger.info("=== Starting JSON -> CSV Converter ===")

    # 1. Fetch Reference Maps (Need these to resolve IDs like "OperatorID: 1")
    # This is fast and lightweight compared to fetching the main data.
    client = OCMClient()
    logger.info("Fetching Reference Maps (Countries, Operators)...")
    reference_maps = client.fetch_reference_data()

    # 2. Load Raw JSON (The Golden Copy)
    raw_file = Config.RAW_DATA_FILE
    if not os.path.exists(raw_file):
        logger.error(f"❌ Raw file not found: {raw_file}")
        logger.info("Run 'python main.py' first to fetch the data.")
        return

    logger.info(f"Loading Raw Data from {raw_file}...")
    try:
        with open(raw_file, "r", encoding="utf-8") as f:
            all_data = json.load(f)
        logger.info(f"Loaded {len(all_data)} records.")
    except Exception as e:
        logger.error(f"Failed to read JSON: {e}")
        return

    # 3. Transform (Process -> CSV)
    logger.info("Running Data Processor (Sanitization & Schema)...")
    processor = DataProcessor(reference_maps=reference_maps)

    # User requested to name this "process data"
    output_name = os.path.join(Config.DATA_DIR, "processed_data.csv")
    df = processor.process_and_save(all_data, output_filename=output_name)

    if df is not None:
        logger.info("✅ Conversion Complete.")
        logger.info(f"Output: {output_name}")
    else:
        logger.error("❌ Transformation Failed.")


if __name__ == "__main__":
    convert_json()
