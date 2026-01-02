# 🌦️ Weather Agent AI (Enterprise Edition)

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.10%2B-blueviolet) ![Status](https://img.shields.io/badge/status-active-success)

> A modern, autonomous data collection agent that fetches historical and forecast weather/AQI data using the **Open-Meteo API**. Features a stunning **Glassmorphism UI**, dynamic location search, and smart Google Sheets integration.

---

## ✨ Key Features

- **🎨 Modern Immersive UI**: Built with Glassmorphism, Neon accents, and smooth animations.
- **🌍 Dynamic Geocoding**: Search for _any_ city worldwide (powered by Open-Meteo).
- **⏱️ Flexible Intervals**: Choose 1H, 3H, 6H, or 12H data granularity.
- **📊 Custom Data Columns**: Select only the metrics you need (Temp, Humidity, AQI, Pressure, etc.). The sheet headers adapt dynamically!
- **⚡ Localhost Engine**: Runs locally to bypass cloud variable costs and IP limits.
- **🛡️ Google Sheets Sync**: Writes data securely to your Google Sheet using Service Account Auth.

---

## 🛠️ Quick Start

### 1. Prerequisites

- Python 3.10 or higher.
- A Google Cloud Service Account (JSON key).

### 2. Installation

You can either download just this agent or clone the entire repository.

#### Option A: Download Only This Agent (Easiest)

1.  Go to **[download-directory.github.io](https://download-directory.github.io/)**.
2.  Paste this URL: `https://github.com/Sohail-Shaikh-07/AI-Agents/tree/main/weather-ai-agent`
3.  Click **Download** to get the zip file.
4.  Extract the folder and open it in your terminal of choice.

#### Option B: Clone Full Repository

```bash
git clone https://github.com/Sohail-Shaikh-07/AI-Agents.git
cd AI-Agents/weather-ai-agent
```

#### Continue Setup

1.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Setup Environment:**
    - Create a `.env` file (copy `.env.example`).
    - Add your Google Sheet ID and Base64 Credentials.
    - _See [Google Setup Guide](google_setup_guide.md) for help._

### 3. Run the Agent

```bash
uvicorn server:app --reload
```

Open your browser to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🎮 How to Use

1.  **Search Location**: Type a city (e.g., "Tokyo") and click 🔍.
2.  **Select Dates**: Choose your Start and End dates.
3.  **Time Interval**: Pick how detailed you want the data (Hourly vs Daily).
4.  **Select Columns**: Check/Uncheck data points to customize your output.
5.  **Initialize**: Click **"Initialize Agent Protocol"**.
6.  **Watch**: The live terminal will show the agent scraping data and writing to your sheet in real-time.

---

## 📊 Data Dictionary

Here is a breakdown of every data point the agent can collect:

| Data Point      | Metric          | Unit   | Description                                    |
| :-------------- | :-------------- | :----- | :--------------------------------------------- |
| **Temperature** | `temp_c`        | °C     | Air temperature at 2 meters above ground.      |
| **Humidity**    | `humidity`      | %      | Relative humidity at 2 meters.                 |
| **Pressure**    | `pressure_mb`   | hPa    | Atmospheric pressure at the surface.           |
| **Wind Speed**  | `windspeed_kph` | km/h   | Wind speed at 10 meters above ground.          |
| **Visibility**  | `visibility_km` | km     | Distance at which objects can be clearly seen. |
| **AQI**         | `aqi_index`     | US AQI | United States Air Quality Index (0-500).       |
| **PM 2.5**      | `pm2_5`         | μg/m³  | Fine particulate matter (< 2.5 micrometers).   |
| **PM 10**       | `pm10`          | μg/m³  | Coarse particulate matter (< 10 micrometers).  |
| **CO**          | `co`            | μg/m³  | Carbon Monoxide concentration.                 |
| **NO₂**         | `no2`           | μg/m³  | Nitrogen Dioxide concentration.                |

_Note: AQI data includes PM2.5, PM10, CO, and NO₂ automatically when selected._

---

## 🧱 Architecture

| Component     | Technology              | Description                                         |
| :------------ | :---------------------- | :-------------------------------------------------- |
| **Frontend**  | HTML5, CSS3, Vanilla JS | Glassmorphism UI, Fetch API, Real-time Logs.        |
| **Backend**   | FastAPI (Python)        | Async API handling, Background Tasks.               |
| **Processor** | `DynamicProcessor`      | Handles Open-Meteo API logic, filtering, and loops. |
| **Database**  | Google Sheets           | Acts as the NoSQL-like storage backend.             |

---

## ⚠️ Troubleshooting

- **403 Permission Error**: You forgot to share the Google Sheet with your Service Account Email! Check `google_setup_guide.md`.
- **API Error**: Check your internet connection (Open-Meteo requires public internet).

---
