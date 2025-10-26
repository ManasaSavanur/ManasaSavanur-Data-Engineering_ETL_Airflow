# ETL Project — Airflow + Docker (local dev)

Note: this file contains Docker-specific instructions. See `README.md` for the full project overview and other usage notes.

Project summary
- Short: This repository contains a minimal Airflow-based ETL that downloads a sales CSV from Google Sheets, normalizes the ORDERDATE column, and writes the transformed data to a local SQLite database (or Cloud SQL if configured).
- Purpose: Provide a reproducible local development environment (Docker Compose) for authoring and testing Airflow DAGs that process sales data and expose it for BI tools.
- Contents: `dags/etl_sales_dag.py` (the DAG), `ETL.py` (standalone script for quick tests), `docker-compose.yaml` (Airflow container), `run_airflow.ps1` (Windows helper), and `output/` (persistent outputs such as SQLite DB).

How it works (high level)
- The DAG `etl_sales` fetches the CSV export of a Google Sheet, normalizes the `ORDERDATE` column, and writes the results to a persistent location. The project includes helpers to run Airflow in Docker and to persist outputs for BI consumption (Looker Studio, local inspection, or Cloud SQL).

Prerequisites
- Docker Desktop (Windows) running
- PowerShell (you're already in the project root)

Files added
- `docker-compose.yaml` — simple compose that runs `apache/airflow:2.7.1` in standalone mode and mounts `./dags`.

Quick start (PowerShell, run from project root `C:\Users\User\Desktop\ETL Project`)

1. Start the container (foreground, useful to watch logs):

```powershell
docker compose up
```

Or run in background (daemon):

```powershell
docker compose up -d
```

2. Open the Airflow UI in your browser:

- http://localhost:8080

If you used the `airflow users create` command in the compose, the credentials are:
- username: `admin`
- password: `admin`

3. Trigger your DAG `etl_sales`

- From UI: find the DAG and click Trigger
- From CLI inside the container:

```powershell
docker compose exec airflow airflow dags trigger etl_sales
```

View task logs (example):

```powershell
docker compose exec airflow airflow tasks list etl_sales_transform_orderdate
docker compose exec airflow airflow tasks logs etl_sales_transform_orderdate fetch_sheet_csv 2025-10-25T00:00:00+00:00
```

Notes & tips
- The compose file sets `_PIP_ADDITIONAL_REQUIREMENTS=pandas`, so pandas will be installed inside the container automatically at startup.
- The `dags/` volume is mounted read-only from the host; if you want to edit DAG files from the container, remove `:ro` in `docker-compose.yaml`.
- Network access is required to fetch the Google Sheets CSV from your DAG.
- If you prefer a more production-like setup (Postgres + Redis + scheduler + workers), I can add the full official docker-compose example; this simple setup is intended for local development and testing.

Troubleshooting
- If the webserver port 8080 is already used, change the port mapping in `docker-compose.yaml`.
- If your DAG doesn't appear, check `docker compose logs` and ensure the `dags` path in your host contains the DAG file (`dags/etl_sales_dag.py`).
