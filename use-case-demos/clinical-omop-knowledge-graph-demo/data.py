import os
import glob
import time
import subprocess
from typing import Dict, Optional


MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PWD  = os.getenv("MYSQL_PWD", "")       
MYSQL_DB   = os.getenv("MYSQL_DB", "omop")

DATA_DIR = os.getenv("DATA_DIR", "./1_omop_data_csv")

CSV_LINE_TERM = os.getenv("CSV_LINE_TERM", "\\n") 

TABLE_ORDER = [
    "location",
    "care_site",
    "provider",

    "person",
    "observation_period",
    "visit_occurrence",
    "visit_detail",
    "condition_occurrence",
    "drug_exposure",
    "procedure_occurrence",
    "observation",
    "measurement",
    "device_exposure",
    "specimen",
    "death",

    "note",
    "note_nlp",
    "cost",
    "fact_relationship",
    "condition_era",
    "drug_era",
    "dose_era",
    "cohort_definition",
    "cohort",
    "cohort_attribute",
    "attribute_definition",
    "metadata",
    "cdm_source",
]


def _run_mysql(sql: str) -> None:
    """
    Run a SQL statement using mysql client.
    IMPORTANT: Avoid passing password via CLI args.
    We pass MYSQL_PWD via environment variable to prevent leakage in process list / shell history.
    """
    cmd = [
        "mysql",
        "-h", MYSQL_HOST,
        "-P", MYSQL_PORT,
        "-u", MYSQL_USER,
        "--local-infile=1",
        MYSQL_DB,
        "-e", sql,
    ]

    env = os.environ.copy()
    if MYSQL_PWD:
        env["MYSQL_PWD"] = MYSQL_PWD
    else:
        env.pop("MYSQL_PWD", None)

    try:
        subprocess.check_call(cmd, env=env)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            "MySQL command failed.\n"
            f"Host={MYSQL_HOST} Port={MYSQL_PORT} User={MYSQL_USER} DB={MYSQL_DB}\n"
            "Tips:\n"
            "  - If MySQL is in Docker, ensure port mapping and network access are correct.\n"
            "  - Export MYSQL_PWD as env var (do NOT hardcode in code).\n"
            "  - Confirm the database exists and tables are created.\n"
        ) from e


def wait_mysql(timeout_sec: int = 60) -> None:
    """Wait until MySQL is ready by polling SELECT 1."""
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            _run_mysql("SELECT 1;")
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("MySQL not ready after waiting. Check container/logs and connection settings.")


def build_csv_map(data_dir: str) -> Dict[str, str]:
    """Map table name -> csv file path (by filename without extension)."""
    csv_map: Dict[str, str] = {}
    pattern = os.path.join(data_dir, "*.csv")
    for p in glob.glob(pattern):
        name = os.path.splitext(os.path.basename(p))[0]
        csv_map[name] = p
    return csv_map


def load_one_csv(table: str, csv_path: str) -> None:
    """
    Load a single CSV into a MySQL table using LOAD DATA LOCAL INFILE.
    """
    abs_path = os.path.abspath(csv_path).replace("\\", "\\\\")  # escape for Windows paths if any
    sql = f"""
LOAD DATA LOCAL INFILE '{abs_path}'
INTO TABLE {table}
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '{CSV_LINE_TERM}'
IGNORE 1 ROWS;
"""
    _run_mysql(sql)


def main() -> None:
    if not os.path.isdir(DATA_DIR):
        raise RuntimeError(
            f"DATA_DIR not found: {DATA_DIR}\n"
            "Set DATA_DIR to the folder that contains OMOP CDM CSV files.\n"
            "Example:\n"
            "  export DATA_DIR=./1_omop_data_csv\n"
        )

    wait_mysql()

    csv_map = build_csv_map(DATA_DIR)
    if not csv_map:
        raise RuntimeError(f"No CSV files found in DATA_DIR={DATA_DIR}")

    for t in TABLE_ORDER:
        p = csv_map.get(t)
        if p:
            print(f"[LOAD] {t} <- {p}")
            load_one_csv(t, p)
        else:
            print(f"[SKIP] {t} (csv not found)")

    print("Done.")


if __name__ == "__main__":
    main()