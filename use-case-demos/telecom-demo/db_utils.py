import duckdb
import os

def connect_db(path="duckdb/my_project.duckdb"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return duckdb.connect(path)

def save_df(con, df, table_name):
    con.register("temp_df", df)
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_df")

def save_all_tables(con, dataframes):
    for table_name, df in dataframes.items():
        save_df(con, df, table_name)
