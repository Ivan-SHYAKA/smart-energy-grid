# Smart Energy Grid Monitoring System

A real-time energy monitoring pipeline demonstrating TimescaleDB time-series features.

## Architecture

All components run on Windows 11:

- **EMQX 5.8.6** — MQTT broker (localhost, port 1883, GUI on port 18083)
- **TimescaleDB** on PostgreSQL 16 — local database (localhost, port 5432)
- **Python 3.11** — simulator, subscriber, historical loader, dashboard
- **Dash (Plotly)** — web dashboard on port 8050

## Data Pipeline

Python simulator → EMQX (port 1883) → Python subscriber → TimescaleDB (port 5432)

## Key Results

- **8,064,000 rows** loaded across 4 weeks, 1,000 meters
- **~2x compression ratio** across all chunk configurations
- **2.44x query speedup** using continuous aggregates
- Chunk experimentation: 225 chunks (3h) vs 29 chunks (1d) vs 5 chunks (1w)

## Setup Instructions

1. Install PostgreSQL 16 + TimescaleDB on Windows
2. Install EMQX on Windows
3. Run `pip install paho-mqtt psycopg2-binary dash plotly pandas sqlalchemy`
4. Run SQL scripts in order from the `sql/` folder
5. Start `python subscriber.py` then `python simulator.py`
6. Run `python dashboard.py` and open `http://localhost:8050`
