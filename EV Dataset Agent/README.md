# 🔌 Global EV Charging Network Agents

A professional Python agent designed to autonomously aggregate, clean, and standardize global electric vehicle charging data from the OpenChargeMap API. Designed for high-performance and Kaggle-ready dataset generation.

## 🌟 Features

- **Global Scope**: Iterates through all available regions to map **123+ countries**.
- **Full History**: Captures `YearCreated` to enable time-series growth analysis (2010-2026).
- **Architecture**: Professional **JSON-First / ELT Pipeline** ensures zero data loss.
- **Smart Mapping**: Automatically resolves IDs (e.g., `OperatorID: 123`) to names.
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
│   ├── global_ev_charging_2025.csv  # Final Dataset
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

- `Operator`: Network Provider (e.g., Tesla, Ionity)
- `MaxPowerKW`: Max charging speed (Fast/Slow analysis)
- `StatusType`: Operational status (e.g., Operational, Broken)
- `UsageCost`: Pricing info (Free/Paid)
- `Country`: Full Country Name
- `YearCreated`: Installation Year (2010-2026) for growth tracking
- `ConnectionTypes`: List of supported plugs (Type 2, CCS, CHAdeMO)

## 📜 License

MIT License. Data subject to OpenChargeMap terms.
