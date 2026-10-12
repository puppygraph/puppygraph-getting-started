"""Export each DuckDB table and view as a parquet file."""
from pathlib import Path

import duckdb

from config import DB_PATH, TABLES, PARQUET_DIR


def main():
    out_dir = Path(PARQUET_DIR)
    out_dir.mkdir(exist_ok=True)
    conn = duckdb.connect(DB_PATH)
    try:
        for table in TABLES:
            out_path = out_dir / f"{table}.parquet"
            conn.execute(f"COPY (SELECT * FROM {table}) TO '{out_path}' (FORMAT PARQUET)")
            print(f"exported {table}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
