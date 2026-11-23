# Simple Sales ETL Pipeline

A portfolio-ready batch ETL project built with Python, Pandas, DuckDB and GitHub Actions. Free tools; no Docker or cloud database required.

## Architecture

`CSV source -> Python/Pandas -> DuckDB + CSV + Parquet -> GitHub Actions`

## Features

- Extract sales records from CSV
- Validate schema and convert data types
- Handle missing regions and invalid records
- Remove duplicate order IDs
- Calculate total sales
- Load curated data into DuckDB
- Export CSV and Parquet datasets
- Test transformations with Pytest
- Automate on push, manual dispatch, and daily schedule

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest -v
python run_etl.py
```

Outputs are written to `outputs/`: DuckDB database, clean CSV, Parquet, and regional sales summary.

## GitHub Actions

The workflow runs on pushes to `main`, manually from Actions, and daily at 00:00 UTC (08:00 Philippine time). Each run uploads `outputs/` as a 14-day artifact. GitHub-hosted runners are temporary, so this is an artifact-based delivery rather than permanent database hosting.

## Portfolio description

**Automated Sales ETL Pipeline | Python, Pandas, DuckDB, GitHub Actions**

Developed an automated batch ETL pipeline that extracts raw sales data from CSV, validates and cleans records using Python and Pandas, and loads curated datasets into DuckDB. Generated CSV and Parquet outputs plus regional sales aggregates. Implemented Pytest data quality checks and GitHub Actions automation for push-triggered, manual, and scheduled execution.
