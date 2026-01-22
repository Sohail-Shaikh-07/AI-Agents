# 🔌 Global EV Charging Network Agents

A professional Python agent designed to autonomously aggregate, clean, and standardize global electric vehicle charging data from the OpenChargeMap API. Designed for high-performance and Kaggle-ready dataset generation.

## 🌟 Features

- **Global Scope**: Iterates through all available regions to map **123+ countries**.
- **Full History**: Captures `YearCreated` to enable time-series growth analysis (2010-2026).
- **Architecture**: Professional **JSON-First / ELT Pipeline** ensures zero data loss.
- **Smart Mapping**: Automatically resolves IDs (e.g., `Operator: 123`) to names.
- **Robust ETL**: Handles pagination, rate limits (429), and connection retries.
- **Kaggle-Ready**: Outputs a clean, flat CSV schema optimized for Data Science.

## 🛠️ Project Structure

```bash
EV_Dataset_Agent/
├── main.py               # Entry point (Fetch -> Save JSON -> Convert CSV)
├── process_json.py       # Utility: Convert local JSON to CSV (Offline Mode)
├── src/
│   ├── api_client.py     # Smart API handling (Retry/Backoff)
│   ├── data_processor.py # Schema transformation & ID Mapping
│   └── config.py         # App Configuration
├── data/                 # Output directory
│   ├── global_raw.json              # Raw Data (Golden Copy)
│   ├── global_ev_charging_station.csv  # Final Dataset
│   ├── processed_data.csv  # If you run process_json.py this will be your Dataset
│   └── dataset_metadata.md          # Kaggle Documentation
├── logs/                 # Execution Logs
│   └── agent_execution.log
└── requirements.txt      # Dependencies
```

## 🚀 Usage

### 1. Setup

```bash
pip install -r requirements.txt
```

### 2. Configure

Create a `.env` file with your API Key:

```env
Open_Charge_Map=your_api_key_here
```

### 3. Run Agent (Full Pipeline)

```bash
python main.py
```

_Fetches fresh data, saves raw JSON, and generates the CSV._

### 4. Offline Processing (Optional)

If you want to modify the CSV logic without re-downloading:

```bash
python process_json.py
```

## 📊 Output Schema

The final CSV includes high-value columns for analysis:

| Column Name       | Description                       | Example                          |
| :---------------- | :-------------------------------- | :------------------------------- |
| `StationID`       | Unique Identifier for the station | `12345`                          |
| `UUID`            | Global Unique ID                  | `123e4567-e89...`                |
| `DataProviderID`  | Source Data Provider ID           | `1` (OpenChargeMap)              |
| `Operator`        | The network provider              | `Tesla Supercharger`, `Ionity`   |
| `UsageType`       | Access Type                       | `Public`, `Private - Restricted` |
| `UsageCost`       | Cost description                  | `Free`, `$0.40/kWh`              |
| `StatusType`      | Current operational status        | `Operational`, `Planned`         |
| `Country`         | Full Country Name                 | `United States`, `Norway`        |
| `MaxPowerKW`      | Maximum power output (speed)      | `250` (Fast), `7` (Slow)         |
| `FastChargeCount` | Number of chargers > 40kW         | `8`                              |
| `ConnectionTypes` | List of supported plugs           | `Type 2, CCS, CHAdeMO`           |
| `AddressTitle`    | Name of the location              | `Supermarché Match`              |
| `AddressLine1`    | Street address                    | `13 Rue Lavoisier`               |
| `Town`            | City or Town                      | `Ronchin`                        |
| `StateOrProvince` | Region or State                   | `Hauts-de-France`                |
| `Postcode`        | Postal Code                       | `59790`                          |
| `Latitude`        | GPS Latitude                      | `50.6040`                        |
| `Longitude`       | GPS Longitude                     | `3.0760`                         |
| `YearCreated`     | Year of installation              | `2024`                           |

## 📜 License

MIT License. Data subject to OpenChargeMap terms.
