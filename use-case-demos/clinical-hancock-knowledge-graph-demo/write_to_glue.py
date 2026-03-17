"""Load parquet tables from S3 into the Glue catalog."""

import pyarrow as pa
import pyarrow.parquet as pq
from pyiceberg.catalog import load_catalog
from pyiceberg.exceptions import NoSuchTableError
from pyiceberg.io.pyarrow import pyarrow_to_schema
from config import (
    TABLES,
    S3_BUCKET,
    S3_PREFIX,
    GLUE_DATABASE,
    GLUE_WAREHOUSE,
    OVERWRITE_GLUE_TABLES,
)

def add_field_ids(schema):
    return pa.schema([
        field.with_metadata({"PARQUET:field_id": str(i + 1)})
        for i, field in enumerate(schema)
    ])

def main():
    catalog = load_catalog("glue", **{
        "type": "glue",
        "warehouse": GLUE_WAREHOUSE,
    })

    catalog.create_namespace_if_not_exists(GLUE_DATABASE)
    mode = "overwrite" if OVERWRITE_GLUE_TABLES else "append"
    print(f"Glue load mode: {mode}")

    for table in TABLES:
        identifier = f"{GLUE_DATABASE}.{table}"
        parquet_path = f"s3://{S3_BUCKET}/{S3_PREFIX}/{table}/{table}_part0.parquet"
        try:
            arrow_table = pq.read_table(parquet_path)

            if arrow_table.num_rows == 0:
                raise ValueError(f"Parquet file has no rows: {parquet_path}")

            print(f"Loading {table}: {arrow_table.num_rows} rows")

            if OVERWRITE_GLUE_TABLES:
                try:
                    catalog.drop_table(identifier)
                except NoSuchTableError:
                    pass

                iceberg_table = catalog.create_table(
                    identifier,
                    schema=pyarrow_to_schema(add_field_ids(arrow_table.schema)),
                )
            else:
                iceberg_table = catalog.create_table_if_not_exists(
                    identifier,
                    schema=pyarrow_to_schema(add_field_ids(arrow_table.schema)),
                )

            iceberg_table.append(arrow_table)

            print(f"loaded {table}")
        except Exception as exc:
            raise RuntimeError(
                f"Failed loading table {table} from {parquet_path} into {identifier}"
            ) from exc

if __name__ == "__main__":
    main()
