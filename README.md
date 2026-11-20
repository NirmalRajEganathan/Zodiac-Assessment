# Zodiac Maritime Vessel KPI Dashboard

## Overview

A Streamlit-based dashboard developed for the Zodiac Maritime Take-Home Exercise to monitor vessel KPI performance, investigate anomalies, correct report data, and maintain an audit history.

## Features

- Vessel, Voyage Type, KPI, and Date Range filters
- Power % and Speed % scatter plots
- Blue (Normal) and Amber (Flagged) anomaly indicators
- Chart-driven row selection (Box Select / Lasso Select / Click Select)
- Data quality checks:
  - Duplicate Report IDs
  - Missing Power %
  - Negative Speed %
- Conditional formatting for negative deviations
- Inline editing with validation
- SQLite data storage
- Audit logging with user tracking
- Database reset functionality

## Technology Stack

- Python
- Streamlit
- Pandas
- Plotly
- SQLite

## Installation
python -m pip install -r requirements.txt

## Run Application & Databricks Deployment
python -m streamlit run app.py (on local)
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 (For Databricks Apps deployment, the application uses the runtime-provided $PORT environment variable as configured in app.yaml)

## Audit Log

All changes are recorded with:

Report ID
Field Modified
Old Value
New Value
User
Timestamp