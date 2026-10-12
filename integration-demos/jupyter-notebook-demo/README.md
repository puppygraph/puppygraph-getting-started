# Query PuppyGraph in Jupyter Notebook
This demo shows how to query PuppyGraph in a Jupyter Notebook using both openCypher and Gremlin. The examples are written in Python >=3.9 and use the [Neo4j Python driver](https://neo4j.com/docs/api/python-driver/current/) and the [Gremlin-Python driver](https://tinkerpop.apache.org/docs/3.7.3/reference/#gremlin-python). You can find sample queries in the notebooks:
- `opencypher.ipynb`
- `gremlin.ipynb`

## Start PuppyGraph

Run the command below to start a [PuppyGraph Docker container](https://docs.puppygraph.com/getting-started/launching-puppygraph-in-docker/). This command will also download the PuppyGraph image if it hasn't been downloaded previously.
```bash
docker run -p 8081:8081 -p 8182:8182 -p 7687:7687 -d --name puppy --rm --pull=always puppygraph/puppygraph:latest
```

## Load the Example Graph

The notebooks query the built-in Modern example graph.

1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
   - Username: `puppygraph`
   - Password: `puppygraph123`
2. Under **Use Example Graph**, click **Load Example** and choose **Modern Graph**.

## Set up Python and Start Jupyter Notebook

Create a virtual environment, install Jupyter together with the [**Neo4j** Python driver](https://pypi.org/project/neo4j/) and the [**Gremlin-Python** driver](https://pypi.org/project/gremlinpython/), and start the notebook server:
```bash
python3 -m venv venv
source venv/bin/activate
pip install jupyter neo4j gremlinpython
jupyter notebook
```

## OpenCypher
Open the `opencypher.ipynb` notebook and run the queries provided.

## Gremlin
Open the `gremlin.ipynb` notebook and run the queries provided. It connects through `AiohttpTransport(call_from_event_loop=True)` so the driver shares Jupyter's event loop; the notebook explains why.
