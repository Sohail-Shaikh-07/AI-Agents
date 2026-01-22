# 🌍 Global EV Charging Station Network (2010-2026)

### ⚡ Comprehensive geospatial data of 257,000+ Stations across 123 Countries. Includes Power, Plugs, and Growth History.

## 🚀 Overview

The electric vehicle (EV) revolution is here. This dataset provides a comprehensive, **real-time snapshot** of the global charging infrastructure, capturing over **257,000+ charging stations** across **123 active countries**.

Unlike other datasets that are outdated or limited to specific regions, this dataset includes **Historical Growth Data** (Year Created) allowing for time-series analysis of infrastructure growth.

## 📊 Key Features

- **Global Coverage**: From the US to China, Europe to India (120+ Countries).
- **Granular Details**: Exact `Latitude/Longitude`, `Power Output (kW)`, and `Connector Types`.
- **Growth Tracking**: Includes `YearCreated` to visualize the explosion of EV infra from 2010 to 2026.
- **Rich Metadata**: Full Operator names (Tesla, Shell, ChargePoint), Status (Operational/Broken), and Usage Costs.

## 📂 Dataset Structure

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

## 💡 Inspiration for Analysis

1.  **The Range Anxiety Map**: Visualize "Charging Deserts" where the distance between fast chargers > 100km.
2.  **The Growth Curve**: Plot the number of _new_ chargers installed per year globally.
3.  **Fast vs. Slow**: What % of the network is actually "Fast Charging" (>50kW)?
4.  **Operator Wars**: Market share analysis of Tesla vs. Shell vs. regional players.

## 🤝 Acknowledgements

Data sourced from [OpenChargeMap](https://openchargemap.org), the world's largest open global registry of electric vehicle charging locations.

