import os
import glob
import time
import subprocess

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PWD  = os.getenv("MYSQL_PWD", "root")
MYSQL_DB   = os.getenv("MYSQL_DB", "omop")

DATA_DIR = os.getenv("DATA_DIR", "./1_omop_data_csv")

TABLE_ORDER = [
    # health system
    "location",
    "care_site",
    "provider",

    # core
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

    # notes/cost/facts/era/cohort/meta
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

def run_mysql(sql: str) -> None:
    cmd = [
        "mysql",
        f"-h{MYSQL_HOST}",
        f"-P{MYSQL_PORT}",
        f"-u{MYSQL_USER}",
        f"-p{MYSQL_PWD}",
        "--local-infile=1",
        MYSQL_DB,
        "-e",
        sql
    ]
    subprocess.check_call(cmd)

def wait_mysql():
    for _ in range(60):
        try:
            run_mysql("SELECT 1;")
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("MySQL not ready")

def load_one_csv(table: str, csv_path: str):
    sql = f"""
    LOAD DATA LOCAL INFILE '{os.path.abspath(csv_path)}'
    INTO TABLE {table}
    FIELDS TERMINATED BY ',' ENCLOSED BY '"'
    LINES TERMINATED BY '\\n'
    IGNORE 1 ROWS;
    """
    run_mysql(sql)

def main():
    wait_mysql()
    csv_map = {}
    for p in glob.glob(os.path.join(DATA_DIR, "*.csv")):
        name = os.path.splitext(os.path.basename(p))[0]
        csv_map[name] = p
    for t in TABLE_ORDER:
        if t in csv_map:
            print(f"[LOAD] {t} <- {csv_map[t]}")
            load_one_csv(t, csv_map[t])
        else:
            print(f"[SKIP] {t} (csv not found)")

    print("Done.")

if __name__ == "__main__":
    main()