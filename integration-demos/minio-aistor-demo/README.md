# CloudTrail security investigations with PuppyGraph and MinIO AIStor

## Summary

Query the public [flaws.cloud CloudTrail dataset](https://summitroute.com/blog/2020/10/09/public_dataset_of_cloudtrail_logs_from_flaws_cloud/)
as a graph over Iceberg tables in MinIO AIStor:

```text
Account → Identity → Session → Event → Resource
```

The sample preparation follows JSON → Parquet → Iceberg. AIStor stores the
Iceberg tables and provides its native catalog. PuppyGraph queries those tables
directly. Existing Iceberg tables can be connected without sample preparation.

## Prerequisites

- Docker with Compose v2 and Python 3.10+ with `venv` and `pip`.
- An [AIStor license](https://docs.min.io/aistor/operations/licenses/) that permits
  AIStor Tables, saved as `minio.license` in this directory.
- Ports 9000, 9001, 8081, 8182, and 7687 available locally.

Run all commands from this directory. Compose uses local demo credentials
and the `latest` images for both AIStor and PuppyGraph.

## Preparing the Data

Download and extract the public archive (about 240 MiB):

```bash
curl -fL https://summitroute.com/downloads/flaws_cloudtrail_logs.tar -o flaws_cloudtrail_logs.tar
mkdir -p json_data
tar -xf flaws_cloudtrail_logs.tar --strip-components=1 -C json_data
```

Create a Python environment and convert the logs into six Parquet files:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python json_to_parquet.py json_data parquet_data
```

The converter reads JSON and gzipped JSON, so a separate `gunzip` step is
unnecessary. It holds normalized rows in memory during conversion. Missing
sessions and MFA values remain unknown; account contact details are left empty.

## Getting Started

Start AIStor and PuppyGraph, then create the warehouse:

```bash
docker compose up -d --pull always
docker compose exec aistor mc alias set local http://localhost:9000 minioadmin minioadmin
docker compose exec aistor mc admin accesskey create local/ --access-key admin --secret-key password --name puppygraph
docker compose exec aistor mc table warehouse create local mywarehouse
```

## Populate Data

```bash
python populate_tables.py
```

This imports `parquet_data` into six Iceberg tables in AIStor and checks each
stored row count. Wait for all six checks to finish. JSON and Parquet files are
sample-import staging; PuppyGraph queries the AIStor tables without creating
local table copies. After a successful import, the downloaded archive,
`json_data`, and `parquet_data` can be deleted.

## Connect PuppyGraph to AIStor

Open <http://localhost:8081>, sign in with `puppygraph` / `puppygraph123`,
and use **Upload Schema** to upload `schema.json`.

The schema includes the AIStor catalog and storage connection settings, with
local demo credentials `admin` / `password`. It maps five vertex types
and four relationships to the external Iceberg tables. Events without a session
remain queryable but do not appear in complete account-to-resource paths.

## Craft Queries

In the **Query** panel, select Cypher.

### Which user has the largest attack surface, and what does it look like?

```cypher
MATCH (a:Account)-[:HasIdentity]->(i:Identity)
      -[:HasSession]->(s:Session)
      -[:RecordsEvent]->(e:Event)
      -[:OperatesOn]->(r:Resource)
WITH i, count(DISTINCT r) AS resource_count
ORDER BY resource_count DESC
LIMIT 1
MATCH path = (i)-[:HasSession]->(s:Session)
             -[:RecordsEvent]->(e:Event)
             -[:OperatesOn]->(r:Resource)
RETURN path
LIMIT 100
```

### If a given resource is compromised, who is the blast radius?

```cypher
MATCH path = (a:Account)-[:HasIdentity]->(i:Identity)
             -[:HasSession]->(s:Session)
             -[:RecordsEvent]->(e:Event)
             -[:OperatesOn]->(r:Resource {resource_id:
'3df9b313bb2514d0d12686ca1c54d8475bcb9dba3237911390997b546cd5acec'})
RETURN path
```

These paths show observed API activity, including attempted operations. They do
not establish permissions, compromise, or blast radius. Resource extraction
covers common CloudTrail fields; the graph is not a complete AWS access model.

For optional AI Chat, configure a provider key using the
[PuppyGraph AI configuration guide](https://docs.puppygraph.com/ai/built-in-chatbot/),
then ask: “Find the identity with the most distinct resources in observed session
events. Run the query and cite supporting event IDs. Distinguish activity from
permissions.” Compare the answer with the query results above.

## Shutdown Docker

```bash
docker compose down
```

This retains the AIStor data volume. On restart, skip access-key/warehouse creation and
import, then upload the schema again if the PuppyGraph container was recreated.
To deliberately replace demo table contents, run
`python populate_tables.py --replace-demo-data`; tables update separately,
so wait for all six checks before querying.
To delete the stored demo data, run `docker compose down --volumes`.
