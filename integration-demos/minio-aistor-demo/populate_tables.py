import argparse
import os
from pathlib import Path

import pyarrow.parquet as pq
from pyiceberg.catalog.rest import RestCatalog

from json_to_parquet import FIELDS, SCHEMAS


def iceberg_schema(name):
    from pyiceberg.schema import Schema
    from pyiceberg.types import BooleanType, NestedField, StringType, TimestampType

    types = {
        "STRING": StringType(),
        "DATETIME": TimestampType(),
        "BOOLEAN": BooleanType(),
    }
    return Schema(
        *(
            NestedField(i, field, types[kind], required=False)
            for i, (field, kind) in enumerate(FIELDS[name.lower()], 1)
        )
    )


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
    tables = {
        name: pq.read_table(folder / f"{name}.parquet").cast(schema)
        for name, schema in SCHEMAS.items()
    }
    connection = catalog()
    connection.create_namespace_if_not_exists(namespace)
    if not replace:
        existing = [
            name for name in SCHEMAS if connection.table_exists((namespace, name))
        ]
        if existing:
            raise ValueError(
                f"Tables already exist: {existing}. Use a new namespace or --replace-demo-data."
            )
    for name, data in tables.items():
        table = connection.create_table_if_not_exists(
            (namespace, name), schema=iceberg_schema(name)
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
