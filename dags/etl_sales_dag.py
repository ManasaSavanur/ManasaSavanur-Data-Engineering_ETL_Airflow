from datetime import datetime, timedelta
import os
import tempfile

from airflow import DAG
from airflow.decorators import task
import pandas as pd
from sqlalchemy import create_engine, text

def ensure_orderdate_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure ORDERDATE column is converted to datetime."""
    if "ORDERDATE" in df.columns:
        df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"], errors="coerce", infer_datetime_format=True)
    return df


# --- DAG settings ---
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="etl_sales",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    tags=["etl", "sales"],
) as dag:

    @task()
    def fetch_sheet_csv(sheet_id: str, sheet_name: str) -> str:
        """Download the Google Sheets CSV export and save to a temp file."""
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        tmp_path = os.path.join(tempfile.gettempdir(), f"etl_raw_{sheet_name}.csv")
        df = pd.read_csv(url)
        df.to_csv(tmp_path, index=False)
        return tmp_path

    @task()
    def normalize_orderdate(input_path: str) -> str:
        """Normalize ORDERDATE to MM/DD/YYYY format."""
        df = pd.read_csv(input_path)
        df = ensure_orderdate_datetime(df)

        if "ORDERDATE" in df.columns:
            df["ORDERDATE"] = df["ORDERDATE"].dt.strftime("%m/%d/%Y")
        else:
            print("WARNING: 'ORDERDATE' column not found in input CSV.")

        out_path = os.path.join(tempfile.gettempdir(), "etl_transformed.csv")
        df.to_csv(out_path, index=False)
        return out_path

    @task()
    def save_to_sqlite(transformed_path: str) -> None:
        """Save the transformed data to a local SQLite database."""
        df = pd.read_csv(transformed_path)
        df = ensure_orderdate_datetime(df)

        # Save database inside the project directory (persistent)
        db_path = os.path.join(os.getcwd(), "output", "sales_data.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        engine = create_engine(f"sqlite:///{db_path}")

        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS sales"))
            df.to_sql("sales", conn, if_exists="replace", index=False)
            print(f"✅ Data written to SQLite at {db_path}")
            print(f"Rows: {len(df)}, Columns: {', '.join(df.columns)}")

        print("\nExample query for Looker Studio connection:")
        print("SELECT strftime('%Y-%m', ORDERDATE) as month, SUM(SALES) as total_sales FROM sales GROUP BY month;")

    # ---- Pipeline wiring ----
    SHEET_ID = "1lhytKIPUvE3vhRggAbM_T1I3nJDGA_zBI7pfvMVs2oo"
    SHEET_NAME = "sales_data_sample_Kaggle"

    raw_csv = fetch_sheet_csv(SHEET_ID, SHEET_NAME)
    transformed_csv = normalize_orderdate(raw_csv)
    save_to_sqlite(transformed_csv)
