ETL Project — Airflow + Docker (Local Development) 🚀🐍🐳
Project Overview 📦

This repository provides a minimal Airflow-based ETL pipeline that:

📥 Downloads a sales CSV from Google Sheets

🗓 Normalizes the ORDERDATE column

💾 Writes the transformed data to a local SQLite database (or a managed database if configured)

Purpose: Provide a reproducible local development environment using Docker Compose for authoring and testing Airflow DAGs that process sales data and expose it for BI tools.