# CloudTrail Graph Demo with MongoDB

## Summary
This demo shows how to build a SIEM-inspired investigation graph directly on a MongoDB Atlas cluster using PuppyGraph. We use a public dataset of anonymized AWS CloudTrail logs from [flaws.cloud](https://summitroute.com/blog/2020/10/09/public_dataset_of_cloudtrail_logs_from_flaws_cloud/), a security training environment created by Scott Piper. This dataset, with 1.9 million events that simulate realistic attack scenarios in AWS, is ideal for modeling real-world threat investigations. Here, we’ll leverage part of the data to construct and visualize a graph of these events using PuppyGraph.


## Prerequisites
- MongoDB account
- Docker
- Python 3

**Note:** If you are new to PuppyGraph or MongoDB Atlas, it is recommended to first go through the [MongoDB Atlas + PuppyGraph Quickstart Demo](https://docs.puppygraph.com/getting-started/querying-mongodb-atlas-data-as-a-graph/) to get familiar with the setup and basic concepts.


## MongoDB Atlas Setup
Follow the getting-started [guide](https://www.mongodb.com/docs/atlas/getting-started/) to set up a MongoDB Atlas cluster. You can use the free tier for this demo, which provides sufficient resources for our needs.
Follow the instructions up to step 4, **Manage the IP access list**:

1. Create a MongoDB Atlas cluster.
2. Deploy a Free cluster.
3. Manage database users for your cluster.
4. Manage the IP access list.


## Preparation

* Download the CloudTrail dataset and extract the files:
  ```bash
  wget https://summitroute.com/downloads/flaws_cloudtrail_logs.tar
  mkdir -p ./raw_data
  tar -xvf flaws_cloudtrail_logs.tar --strip-components=1 -C ./raw_data
  gunzip ./raw_data/*.json.gz
  ```

* Create a virtual environment and install the required Python packages. On some Linux distributions, you may need to install `python3-venv` first.
  ```sh
  # On some Linux distributions, install `python3-venv` first.
  sudo apt-get update
  sudo apt-get install python3-venv
  ```
  Create a virtual environment, activate it, and install the necessary packages:
  ```sh
  python -m venv venv
  source venv/bin/activate
  pip install ijson faker pandas pymongo
  ```

* Process the raw data and import the first chunk of data (100k events) into MongoDB, replace the connection string with your MongoDB Atlas connection string for MongoDB Python Driver. You can find the connection string in the **Connect** section of your cluster's settings. See the [document](https://www.mongodb.com/docs/manual/reference/connection-string/) for more details about the MongoDB connection string.
  ```sh
  export MONGODB_CONNECTION_STRING="your_mongodb_connection_string"
  python import_data.py raw_data/flaws_cloudtrail00.json --database cloudtrail
  ```

* Create Atlas SQL federated database instance and get the JDBC URI. The JDBC URI will be used to connect PuppyGraph to MongoDB Atlas via Atlas SQL interface. See the PuppyGraph [documentation]((https://docs.puppygraph.com/getting-started/querying-mongodb-atlas-data-as-a-graph/)) for more details on how to set up the Atlas SQL federated database.

* Manage Atlas SQL Schema. Check if the schema status is **Available** and if not, generate a new schema from sample. See the PuppyGraph [documentation](https://docs.puppygraph.com/getting-started/querying-mongodb-atlas-data-as-a-graph/) for more details on how to manage the Atlas SQL schema.


## Modeling the Graph
* Start PuppyGraph using Docker by running the following command:
  ```bash
  docker run -p 8081:8081 -p 8182:8182 -p 7687:7687 -e PUPPYGRAPH_PASSWORD=puppygraph123 -d --name puppy --rm --pull=always puppygraph/puppygraph:stable
  ```

* Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
  - Username: `puppygraph`
  - Password: `puppygraph123`

* Upload the schema:
  - Fill the `username`, `password` and `jdbcUri` fields in the `schema.json` file with your MongoDB Atlas database credentials and JDBC URI.
  - Select the file `schema.json` in the **Upload Graph Schema JSON** section and click on **Upload**. You can also upload the schema from the terminal using the `curl` command below.
      ```sh
      curl -XPOST -H "content-type: application/json" --data-binary @./schema.json --user "puppygraph:puppygraph123" localhost:8081/schema
      ```
  Wait for the schema to be uploaded successfully. It takes about 5 minutes.


## Querying the Graph using Cypher and Gremlin
- Navigate to the Query panel on the left side. The Graph Query tab offers an interactive environment for querying the graph using Gremlin and Cypher.
- After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. 
  
You can do this by clicking the "Clear Canvas" button located in the top-right corner of the page.

Here are some example queries to get you started.

Let's say, we want to investigate the activity of a specific account. First, we count the number of sessions associated with the account.

  ```gremlin
  g.V("Account[811596193553]").out("HasIdentity").out("HasSession").count()
  ```

  ```cypher
  MATCH (a:Account)-[:HasIdentity]->(i:Identity)-[:HasSession]->(s:Session)
  WHERE id(a) = "Account[811596193553]"
  RETURN count(s)
  ```

Then we want to see how many of these sessions are MFA authenticated or not.

  ```gremlin
  g.V("Account[811596193553]").out("HasIdentity").out("HasSession")
    .groupCount().by("mfa_authenticated")
  ```
  
  ```cypher
  MATCH (a:Account)-[:HasIdentity]->(i:Identity)-[:HasSession]->(s:Session)
  WHERE id(a) = "Account[811596193553]"
  RETURN s.mfa_authenticated AS mfaStatus, count(s) AS count
  ```


Next, we investigate those sessions that are not MFA authenticated and see what resources they accessed.
  
  ```gremlin
  g.V("Account[811596193553]").out("HasIdentity").out("HasSession")
    .has("mfa_authenticated", false).out('RecordsEvent').out('OperatesOn')
	  .groupCount().by("resource_type")
  ```

  ```cypher
  MATCH (a:Account)-[:HasIdentity]->
    (i:Identity)-[:HasSession]->
    (s:Session {mfa_authenticated: false})-[:RecordsEvent]->
    (e:Event)-[:OperatesOn]->(r:Resource)
  WHERE id(a) = "Account[811596193553]"
  RETURN r.resource_type AS resourceType, count(r) AS count
  ```

We show those access paths in a graph.

  ```gremlin
  g.V("Account[811596193553]").out("HasIdentity").out("HasSession").has("mfa_authenticated", false)
    .out('RecordsEvent').out('OperatesOn')
	  .path()
  ```

  ```cypher
  MATCH path = (a:Account)-[:HasIdentity]->
    (i:Identity)-[:HasSession]->
    (s:Session {mfa_authenticated: false})-[:RecordsEvent]->
    (e:Event)-[:OperatesOn]->(r:Resource)
  WHERE id(a) = "Account[811596193553]"
  RETURN path
  ```

## Cleanup and Teardown
- To stop and remove the Puppygraph container, run:
```bash
docker stop puppy
```