# 🔌 Global EV Charging Network Agents

A professional Python agent designed to autonomously aggregate, clean, and standardize global electric vehicle charging data from the OpenChargeMap API. Designed for high-performance and Kaggle-ready dataset generation.

## 🌟 Features

- **Global Scope**: Iterates through 250+ countries to build a complete world map.
- **Full History**: Captures `DateCreated` to enable time-series growth analysis (2015-2025).
- **Smart Mapping**: Automatically resolves IDs (e.g., `OperatorID: 123`) to human-readable names using Reference Data.
- **Robust ETL**: Handles pagination, rate limits (429), and connection retries.
- **Kaggle-Ready**: Outputs a clean, flat CSV schema optimized for Data Science.

## 🛠️ Project Structure

```bash
EV_Dataset_Agent/
├── main.py               # Entry point
├── src/
│   ├── api_client.py     # Smart API handling (Retry/Backoff)
│   ├── data_processor.py # Schema transformation & ID Mapping
│   └── config.py         # App Configuration
├── data/                 # Output directory
│   ├── global_ev_charging_2025.csv  # Final Dataset
│   └── dataset_metadata.md          # Kaggle Documentation
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

### 3. Run Agent

```bash
python main.py
```

_The agent will fetch reference maps, iterate through all countries, and generate the CSV in the `data/` folder._

## 📊 Output Schema

The final CSV includes high-value columns for analysis:

- `Operator`: Network Provider (e.g., Tesla, Ionity)
- `PowerKW`: Max charging speed (Fast/Slow analysis)
- `Status`: Operational status
- `UsageCost`: Pricing info (Free/Paid)
- `Country`: Full Country Name
- `DateCreated`: Timestamp for growth analysis

## 📜 License

MIT License. Data subject to OpenChargeMap terms.
