# Integrating RisingWave and Querying Data Using PuppyGraph

## Summary
This demo showcases a real-time data analysis workflow by integrating RisingWave with PuppyGraph. 
We import data from Kafka into RisingWave, then query it using PuppyGraph’s graph database interface. 
This process streamlines data processing, storage, and visualization, enabling immediate insights from dynamic data.

## Prerequisites

- [Docker and Docker Compose](https://docs.docker.com/compose/)
- [Postgresql client](https://docs.risingwave.com/deploy/install-psql-without-postgresql)
- [Python 3 and virtual environment](https://docs.python.org/3/library/venv.html)

## Start the Services
Run the command below to start the services.
```bash
docker compose up -d
```

The services include the pipeline:
- Kafka
- RisingWave
- PuppyGraph


## Creating a Python Virtual Environment
Create a Python virtual environment and install the `confluent_kafka` package.
```bash
python3 -m venv myvenv
source myvenv/bin/activate
pip install confluent-kafka
```

## Creating Kafka Topics
Run the python script `topics.py` to create topics.
```bash
python topics.py -c
```

## RisingWave Connecting to Kafka
Execute the SQL commands in `rw_kafka.sql` using the PostgreSQL client. 
This will create sources for each stream and the correponding materialized views.
```bash
psql -h localhost -p 4566 -d dev -U root -f rw_kafka.sql
```

## Importing Snapshot Data.
Run the python script `topics.py` to import the snapshot data.
```bash
python topics.py -s
```

## Querying in RisingWave (Optional)
You can check the snapshot data in RisingWave via PostgreSQL client.
```bash
psql -h localhost -p 4566 -d dev -U root
```
For example:
- List tables, views, and sequences:
```sql
\d
```
- See 5 items of records in the materialized view `account_mv`.
```sql
SELECT * FROM public.account_mv LIMIT 5;
```
- Check the number of records in the materialized view `account_mv`.
```sql
SELECT COUNT(*) FROM public.account_mv;
```

## Modeling the Graph
Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
- Username: `puppygraph`
- Password: `puppygraph123`

Upload the schema:
- In Web UI, select the file `schema.json` under **Upload Graph Schema JSON**, then click on **Upload**.

## Querying via PuppyGraph
You can try some [Gremlin or Cypher queries](https://docs.puppygraph.com/querying/) of the snapshot data for PuppyGraph.
- Navigate to the **Query** panel on the left side. The **Gremlin Query** tab provides an interactive environment for querying the graph using Gremlin.
- After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. Click **Clear** at the top-right corner of the page.
- For Cypher queries, you can use [Graph Notebook and Cypher Console](https://docs.puppygraph.com/querying/querying-using-opencypher/). Be sure to add `:>` before the cypher query when using Cypher Console. 

Some example queries:

1. **Gremlin**: Get the number of accounts.
    ```groovy
    g.V().hasLabel('Account').count()
    ```
2. **Gremlin**: Get accounts that are blocked.
    ```groovy
    g.V().has('Account', 'isBlocked', 'true')
    ```

Note: 
Example queries 3 will return `null` for snapshot data because those vertices are included in the incremental data.

3. **Gremlin**: Given an account, find the sum and max of fund amounts in transfer-ins and transfer-outs for a specific time range.
   ```groovy
    g.V("Account[268245652805255366]").as('v').
        project('outs', 'ins').
            by(select('v').outE('AccountTransferAccount').
                has('createTime', between(
                    datetime("2022-01-01T00:00:00.000Z"), datetime("2024-01-01T00:00:00.000Z")
                )).fold()
            ).
            by(select('v').inE('AccountTransferAccount').
                has('createTime', between(
                    datetime("2022-01-01T00:00:00.000Z"), datetime("2024-01-01T00:00:00.000Z")
                )).fold()
            ).
        project('sumOutEdgeAmount', 'maxOutEdgeAmount', 'numOutEdge', 
        'sumInEdgeAmount', 'maxInEdgeAmount', 'numInEdge').
            by(select('outs').coalesce(unfold().values('amount').sum(), constant(0))).
            by(select('outs').coalesce(unfold().values('amount').max(), constant(-1))).
            by(select('outs').coalesce(unfold().count(), constant(0))).
            by(select('ins').coalesce(unfold().values('amount').sum(), constant(0))).
            by(select('ins').coalesce(unfold().values('amount').max(), constant(-1))).
            by(select('ins').coalesce(unfold().count(), constant(0)))
   ```
   
4. **Cypher**: Get the number of accounts.
   
   ```cypher
   MATCH (x:Account) RETURN count(x)
   ```

## Import Incremental Data
Run the python script `topics.py` to import the incremental data.
```bash
python topics.py -i
```

## Querying via PuppyGraph in Real Time
You can continue querying in PuppyGraph and see the results change as new data is added.

## Cleanup and Teardown
To stop and remove the containers and networks, run:
```bash
docker compose down -v
```

