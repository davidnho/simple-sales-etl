from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "sales.csv"
OUTPUT_DIR = ROOT / "outputs"

REQUIRED_COLUMNS = {
    "order_id", "order_date", "customer_name", "region",
    "product", "quantity", "unit_price"
}


def extract(path: Path = RAW_FILE) -> pd.DataFrame:
    """Read raw sales records from CSV."""
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_csv(path)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Validate, clean and enrich sales records."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    clean = df.copy()
    clean["order_id"] = clean["order_id"].astype("string").str.strip()
    clean["customer_name"] = clean["customer_name"].astype("string").str.strip()
    clean["region"] = clean["region"].fillna("Unknown").astype("string").str.strip()
    clean["region"] = clean["region"].replace("", "Unknown")
    clean["product"] = clean["product"].astype("string").str.strip()

    clean["order_date"] = pd.to_datetime(clean["order_date"], errors="coerce")
    clean["quantity"] = pd.to_numeric(clean["quantity"], errors="coerce")
    clean["unit_price"] = pd.to_numeric(clean["unit_price"], errors="coerce")

    clean = clean.dropna(subset=[
        "order_id", "customer_name", "product", "order_date",
        "quantity", "unit_price"
    ])
    clean = clean[(clean["quantity"] > 0) & (clean["unit_price"] >= 0)]
    clean = clean.drop_duplicates(subset=["order_id"], keep="first")
    clean["total_sales"] = (clean["quantity"] * clean["unit_price"]).round(2)
    clean["order_date"] = clean["order_date"].dt.strftime("%Y-%m-%d")

    return clean.sort_values("order_id").reset_index(drop=True)


def _sql_string(value: Path) -> str:
    """Return a safely quoted SQL string literal for a local output path."""
    return "'" + str(value).replace("'", "''") + "'"


def load(df: pd.DataFrame, output_dir: Path = OUTPUT_DIR) -> None:
    """Load curated data into DuckDB and export analytics-friendly files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(output_dir / "sales_analytics.duckdb"))
    try:
        con.register("clean_sales_df", df)
        con.execute("""
            CREATE OR REPLACE TABLE clean_sales AS
            SELECT * FROM clean_sales_df
        """)
        con.execute(
            f"COPY (SELECT * FROM clean_sales ORDER BY order_date, order_id) "
            f"TO {_sql_string(output_dir / 'clean_sales.csv')} (HEADER, DELIMITER ',')"
        )
        con.execute(
            f"COPY (SELECT region, COUNT(*) AS order_count, "
            f"SUM(total_sales) AS total_sales FROM clean_sales "
            f"GROUP BY region ORDER BY total_sales DESC) "
            f"TO {_sql_string(output_dir / 'sales_by_region.csv')} "
            f"(HEADER, DELIMITER ',')"
        )
        con.execute(
            f"COPY (SELECT * FROM clean_sales ORDER BY order_date, order_id) "
            f"TO {_sql_string(output_dir / 'clean_sales.parquet')} (FORMAT PARQUET)"
        )
    finally:
        con.close()


def run_pipeline() -> dict:
    raw = extract()
    clean = transform(raw)
    load(clean)
    result = {
        "source_rows": len(raw),
        "clean_rows": len(clean),
        "removed_rows": len(raw) - len(clean),
        "total_sales": round(float(clean["total_sales"].sum()), 2),
    }
    print("ETL completed successfully")
    for key, value in result.items():
        print(f"{key}: {value}")
    return result


if __name__ == "__main__":
    run_pipeline()
