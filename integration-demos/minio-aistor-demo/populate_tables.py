import argparse
import os
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from pyiceberg.catalog.rest import RestCatalog

TABLE_NAMES = ("Account", "Identity", "Session", "Event", "Resource", "EventResource")


def read_table(folder, name):
    data = pq.read_table(folder / f"{name}.parquet")
    timestamp_column = {"Session": "creation_date", "Event": "event_time"}.get(name)
    if timestamp_column:
        index = data.schema.get_field_index(timestamp_column)
        values = data[timestamp_column].cast(pa.timestamp("us", tz="UTC"))
        data = data.set_column(index, timestamp_column, values.cast(pa.timestamp("us")))
    return data


def catalog():
    endpoint = os.environ.get("AISTOR_ENDPOINT", "http://localhost:9000").rstrip("/")
    access = os.environ.get("AISTOR_ACCESS_KEY", "admin")
    secret = os.environ.get("AISTOR_SECRET_KEY", "password")
    return RestCatalog(
        "aistor",
        **{
            "uri": endpoint + "/_iceberg",
            "warehouse": os.environ.get("AISTOR_WAREHOUSE", "mywarehouse"),
            "rest.sigv4-enabled": "true",
            "rest.signing-name": "s3tables",
            "rest.signing-region": "us-east-1",
            "client.region": "us-east-1",
            "client.access-key-id": access,
            "client.secret-access-key": secret,
            "s3.endpoint": endpoint,
            "s3.region": "us-east-1",
            "s3.path-style-access": "true",
            "s3.access-key-id": access,
            "s3.secret-access-key": secret,
        },
    )


def load(folder, namespace="cloudtrail", replace=False):
    tables = {name: read_table(folder, name) for name in TABLE_NAMES}
    connection = catalog()
    connection.create_namespace_if_not_exists(namespace)
    if not replace:
        existing = [
            name for name in TABLE_NAMES if connection.table_exists((namespace, name))
        ]
        if existing:
            raise ValueError(
                f"Tables already exist: {existing}. Use a new namespace or --replace-demo-data."
            )
    for name, data in tables.items():
        table = connection.create_table_if_not_exists(
            (namespace, name), schema=data.schema
        )
        table.overwrite(data)
        actual = table.scan().count()
        if actual != len(data):
            raise RuntimeError(f"{name}: expected {len(data)} rows, found {actual}")
        print(f"{name}: verified {actual} rows in Iceberg")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path, nargs="?", default=Path("parquet_data"))
    parser.add_argument("--namespace", default="cloudtrail")
    parser.add_argument("--replace-demo-data", action="store_true")
    args = parser.parse_args()
    load(args.folder, args.namespace, args.replace_demo_data)
