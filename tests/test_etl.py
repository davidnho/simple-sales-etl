from pathlib import Path
import sys

# Ensure the repository root is importable when pytest collects this file.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import pytest

from src.etl import transform


def test_transform_removes_duplicate_order_and_calculates_sales():
    raw = pd.DataFrame([
        {"order_id": "1", "order_date": "2026-01-01", "customer_name": "A",
         "region": "", "product": "Pen", "quantity": 2, "unit_price": 10},
        {"order_id": "1", "order_date": "2026-01-01", "customer_name": "A",
         "region": "", "product": "Pen", "quantity": 2, "unit_price": 10},
    ])
    result = transform(raw)
    assert len(result) == 1
    assert result.loc[0, "total_sales"] == 20
    assert result.loc[0, "region"] == "Unknown"


def test_transform_rejects_missing_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        transform(pd.DataFrame({"order_id": ["1"]}))
