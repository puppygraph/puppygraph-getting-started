# Query PuppyGraph in Jupyter Notebook
This demo shows how to query PuppyGraph in a Jupyter Notebook using both openCypher and Gremlin. The examples are written in Python >=3.9 and use the [Neo4j Python driver](https://neo4j.com/docs/api/python-driver/current/) and the [Gremlin-Python driver](https://tinkerpop.apache.org/docs/3.7.3/reference/#gremlin-python). You can find sample queries in the notebooks:
- `opencypher.ipynb`
- `gremlin.ipynb`

## Start PuppyGraph

Run the command below to start a [PuppyGraph Docker container](https://docs.puppygraph.com/getting-started/launching-puppygraph-in-docker/). This command will also download the PuppyGraph image if it hasn't been downloaded previously.
```bash
docker run -p 8081:8081 -p 8182:8182 -p 7687:7687 -d --name puppy --rm --pull=always puppygraph/puppygraph:stable
```

## Start Jupyter Notebook

Run the following command to start Jupyter Notebook server.
```bash
jupyter notebook
```

## OpenCypher
1. Install the [**Neo4j** Python driver](https://pypi.org/project/neo4j/):
```bash
pip install neo4j
```
2. Open the `opencypher.ipynb` notebook and run the queries provided.

## Gremlin
1. Install the [**Gremlin-Python** driver](https://pypi.org/project/gremlinpython/):

```bash
pip install gremlinpython
```
2. Event Loop Considerations
When using Gremlin-Python within a Jupyter notebook, you may encounter event loop conflicts because Jupyter/IPython runs its own event loop by default. The Gremlin driver needs to integrate with the existing event loop rather than starting a new one.

    **How to Tackle the Event Loop Issue**
    Import the `AiohttpTransport` class:
    ```python
    from gremlin_python.driver.aiohttp.transport import AiohttpTransport
    ```
    When creating the DriverRemoteConnection, provide a `transport_factory` that sets `call_from_event_loop=True`:
    ```python
    from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

    connection = DriverRemoteConnection(
        'ws://localhost:8182/gremlin',
        'g',
        username='your_username',
        password='your_password',
        transport_factory=lambda: AiohttpTransport(call_from_event_loop=True)
    )
    ```
    This ensures all asynchronous calls are scheduled on (and run by) Jupyter’s active event loop, avoiding conflicts.

1. Open the `gremlin.ipynb` notebook to see detailed examples and learn how to handle the event loop issue.

