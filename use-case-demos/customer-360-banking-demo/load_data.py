from sqlalchemy import create_engine
import pandas as pd
from pathlib import Path
from faker import Faker

data_dir = Path("./data")   # CSVs live in ./data alongside this script

names = ["client", "account", "disp", "trans", "loan", "card", "order", "district"]
tables = {n: pd.read_csv(data_dir / f"{n}.csv", sep=";") for n in names}

engine = create_engine("postgresql://postgres:puppygraph123@localhost:5432/bank360")

sql_names = {"order": "orders"}   # 'order' is a reserved word in SQL, so rename it

district_rename = {
    "A1":  "district_id",
    "A2":  "district_name",
    "A3":  "region",
    "A4":  "population",
    "A5":  "num_municipalities_lt_499",
    "A6":  "num_municipalities_500_1999",
    "A7":  "num_municipalities_2000_9999",
    "A8":  "num_municipalities_gt_10000",
    "A9":  "num_cities",
    "A10": "urban_ratio",
    "A11": "avg_salary",
    "A12": "unemployment_rate_95",
    "A13": "unemployment_rate_96",
    "A14": "entrepreneurs_per_1000",
    "A15": "crimes_95",
    "A16": "crimes_96",
}

fake = Faker("cs_CZ")
Faker.seed(42)   

for name, df in tables.items():
    if name == "district":
        df = df.rename(columns=district_rename)   
    if name == "client":
        df = df.copy()
        df["name"] = [fake.name() for _ in range(len(df))]   
    table = sql_names.get(name, name)
    df.to_sql(table, engine, schema="public", if_exists="replace", index=False)
    print(f"{table}: {len(df)} rows")