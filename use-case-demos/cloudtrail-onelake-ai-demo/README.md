# Cloud Security Graph Demo with PuppyGraph AI Chatbot and Microsoft OneLake

## Summary

This demo shows how to investigate AWS CloudTrail activity as a graph without moving the analytical tables out of Microsoft OneLake. It uses the public anonymized CloudTrail dataset from [flaws.cloud](https://summitroute.com/blog/2020/10/09/public_dataset_of_cloudtrail_logs_from_flaws_cloud/) and preserves the original security graph model.

You will:

1. Create a Microsoft Fabric workspace and a schema-enabled lakehouse.
2. Transform the CloudTrail JSON records into six Delta tables in OneLake.
3. Let OneLake virtualize the Delta metadata for Iceberg-compatible access.
4. Connect PuppyGraph to the OneLake Iceberg REST endpoint.
5. Ask PuppyGraph AI Chatbot to inspect the tables and propose the graph schema.
6. Approve the schema changes and investigate accounts, identities, sessions, events, and resources in natural language.

PuppyGraph reads the existing OneLake tables in place. The demo does not copy the tables into a separate graph database or create a second graph data pipeline.

## Prerequisites

Before starting, make sure you have:

- A [Microsoft Fabric workspace](https://learn.microsoft.com/fabric/get-started/create-workspaces) backed by Fabric capacity.
- Permission to create a lakehouse and run notebooks in the workspace.
- A Microsoft Entra ID service principal that PuppyGraph can use to read the lakehouse.
- Docker on the machine where PuppyGraph will run.
- An API key for an Anthropic-compatible or OpenAI-compatible model endpoint.
- The `import_to_onelake.py` file in this demo directory.

The host running PuppyGraph must be able to reach the OneLake endpoints, the Microsoft Entra token endpoint, and the configured model API.

## Demo data

The demo uses the public anonymized AWS CloudTrail dataset from [flaws.cloud](https://summitroute.com/blog/2020/10/09/public_dataset_of_cloudtrail_logs_from_flaws_cloud/), a security training environment created by Scott Piper. The archive contains approximately 1.9 million CloudTrail events that simulate realistic activity and attack scenarios in AWS. Although CloudTrail produced the source records, the demo stores the processed data in Microsoft OneLake as Delta tables.

CloudTrail records contain useful investigation context, including the AWS account, acting identity, assumed-role session, API operation, event timestamp, source IP address, user agent, request and response data, and affected cloud resource. The preparation script normalizes those nested JSON records into six tables under the `security_graph` schema:

| **Table** | **Purpose** | **Key fields** |
| --- | --- | --- |
| account | AWS account boundary | `account_id`, `account_alias` |
| identity | IAM users, roles, and assumed identities | `identity_id`, `type`, `principal_id`, `account_id` |
| session | Authenticated or assumed-role sessions | `session_id`, `creation_date`, `mfa_authenticated`, `identity_id` |
| event | Normalized CloudTrail events | `event_id`, `event_time`, `event_name`, `source_ip`, `session_id`, `identity_id` |
| resource | Cloud infrastructure and service resources | `resource_id`, `resource_name`, `resource_type` |
| eventresource | Event-to-resource relationships | `event_id`, `resource_id`, `pre_state`, `post_state` |

The preparation step exists only to populate the public sample data. For a production deployment, PuppyGraph can map equivalent tables that already exist in OneLake.

## 1. Prepare Microsoft Fabric and OneLake

### 1.1 Create a workspace and lakehouse

1. Create or open a Microsoft Fabric workspace backed by Fabric capacity.
2. In the workspace, create a **schema-enabled lakehouse**.
3. Record the workspace ID and lakehouse item ID. PuppyGraph will use them as the Iceberg REST warehouse identifier:

   ```text
   <workspace_id>/<lakehouse_id>
   ```

You can obtain both IDs from the Fabric URL while the lakehouse is open.

### 1.2 Enable Delta-to-Iceberg virtualization

In the Fabric workspace settings, enable **Delta Lake to Apache Iceberg table format virtualization**.

For external access, ask a Fabric tenant administrator to confirm that the following tenant settings are enabled:

- **Service principals can use Fabric APIs**
- **Users can access data stored in OneLake with apps external to Fabric**

OneLake generates virtual Iceberg metadata for eligible Delta tables stored in the `Tables` area of the lakehouse. PuppyGraph reads that Iceberg representation while the authoritative tables remain Delta tables.

## 2. Load the CloudTrail dataset into OneLake

### 2.1 Download the source dataset

Download the archive to your local machine:

```bash
curl -LO https://summitroute.com/downloads/flaws_cloudtrail_logs.tar
```

Do not commit the extracted dataset to Git.

### 2.2 Upload the input files

In the Fabric lakehouse explorer:

1. Open **Files**.
2. Create a folder named `cloudtrail_raw`.
3. Upload `flaws_cloudtrail_logs.tar` to that folder.
4. Add the contents of `import_to_onelake.py` to a Fabric notebook.

### 2.3 Run the import in a Fabric notebook

Create a Fabric notebook and attach the lakehouse. In the first cell, install the streaming JSON parser:

```python
%pip install ijson
```

Restart the Python session if Fabric asks you to do so. Add the contents of `import_to_onelake.py` to a Python cell and run it. The script reads the archive from:

```text
/lakehouse/default/Files/cloudtrail_raw/flaws_cloudtrail_logs.tar
```

and writes the resulting DataFrames as Delta tables under:

```text
security_graph.<table_name>
```

The script retains the original table fields and graph-key generation logic, but writes with the Fabric Spark catalog instead of the Amazon S3 Tables catalog. It parses the archive as a stream and writes rows in batches to avoid loading all 1.9 million events into driver memory at once.

Running the script truncates the six demo tables before loading them. Do not point it at production tables.

After the job completes, confirm that the six expected tables appear under the `security_graph` schema in the lakehouse explorer.

### 2.4 Verify Iceberg virtualization

For each Delta table:

1. Open the table menu in the Fabric lakehouse explorer.
2. Select **View files**.
3. Confirm that the table directory contains a `metadata` folder.
4. Confirm that the folder contains one or more files ending in `.metadata.json`.
5. Check the conversion log if Fabric reports a virtualization error.

Metadata generation is asynchronous and can take a short time. Do not configure PuppyGraph until all six tables expose valid virtual Iceberg metadata.

## 3. Configure OneLake authentication

Create or select a Microsoft Entra ID application and service principal for PuppyGraph.

Record these values:

| Placeholder | Description |
| --- | --- |
| `<tenant_id>` | Microsoft Entra tenant ID |
| `<client_id>` | Application/client ID |
| `<client_secret>` | Client secret value |
| `<workspace_id>` | Fabric workspace ID |
| `<lakehouse_id>` | Fabric lakehouse item ID |

Grant the service principal read access to the target workspace or lakehouse. Use the minimum permissions required by your environment.

Keep the client secret outside source control. You enter it when creating the OneLake catalog in PuppyGraph; do not add it to this repository.

## 4. Start PuppyGraph with AI Chatbot

PuppyGraph AI Chatbot calls an external model API. Create a file named `puppygraph.env` using one of the following configurations.

```dotenv
PUPPYGRAPH_USERNAME=puppygraph
PUPPYGRAPH_PASSWORD=puppygraph123
QUERY_TIMEOUT=5m
AI_ENABLED=true
AI_API_STRUCTURE=anthropic_style
AI_BASE_URL=https://api.anthropic.com
AI_MODELS=<anthropic-model-id>
AI_API_KEY=<your-api-key>
```

For OpenAI, please check out more details in our [documents for the built-in Chatbot](https://docs.puppygraph.com/ai/built-in-chatbot/).

Replace the model ID and API key placeholders with your actual values. The selected model must support streaming and tool calling. Replace the example password before exposing PuppyGraph outside your local machine.

Use plain `KEY=value` entries without surrounding quotes or `export`. Enter the API key directly; Docker's `--env-file` does not expand shell variables such as `$ANTHROPIC_API_KEY`.

### Start PuppyGraph

From the directory containing `puppygraph.env`, run:

```bash
docker run -d --name puppygraph \
  -p 8081:8081 \
  -p 8182:8182 \
  -p 7687:7687 \
  --env-file ./puppygraph.env \
  --pull=always \
  puppygraph/puppygraph:1.8.1
```

For the purpose of stability and reproducibility, we use the version `1.8.1` instead of `latest` or `stable`.

Keep `puppygraph.env` out of version control by adding the following entry to your `.gitignore`:

```gitignore
puppygraph.env
```

## 5. Connect PuppyGraph to OneLake

Open [http://localhost:8081](http://localhost:8081) and sign in with the credentials supplied to the container.

Select **Catalogs** in the left navigation, select **Create Catalog**, and choose Apache Iceberg. Use the following settings:

| Field | Value |
| --- | --- |
| Catalog type | Apache Iceberg |
| Metastore type | Iceberg REST |
| REST endpoint | `https://onelake.table.fabric.microsoft.com/iceberg` |
| REST warehouse | `<workspace_id>/<lakehouse_id>` |
| Authentication | OAuth 2.0 client credentials |
| OAuth credential | `<client_id>:<client_secret>` |
| OAuth scope | `https://storage.azure.com/.default` |
| OAuth server URI | `https://login.microsoftonline.com/<tenant_id>/oauth2/v2.0/token` |
| Storage type | Azure Data Lake Storage Gen2 |
| Storage authentication | Service principal |

Select **Create Catalog** and confirm that PuppyGraph can discover the `security_graph` schema and its six tables. This demo does not store OneLake credentials in a schema file.

## 6. Ask AI Chatbot to build the graph

Select **Chatbot** in the PuppyGraph navigation. Leave **Auto-confirm** turned off so you can inspect the proposed nodes, edges, identifiers, and key mappings before PuppyGraph applies them.

Enter this prompt:

```text
Inspect the security_graph schema in the connected onelake_security
catalog and build a security investigation graph.

Use account, identity, session, event, and resource as nodes.

Create these relationships:
- HasIdentity from Account to Identity, using account_id.
- HasSession from Identity to Session, using identity_id.
- RecordsEvent from Session to Event, using session_id.
- OperatesOn from Event to Resource, using the eventresource table,
  with event_id and resource_id as the endpoint keys.

Use account_id, identity_id, session_id, event_id, and resource_id
as the corresponding node identifiers. Profile the tables and verify
the proposed joins against the data before applying the graph.
```

AI Chatbot inspects catalog metadata, samples rows, profiles columns, and probes the proposed joins. Review every schema-change proposal before selecting **Approve**.

Verify the following mappings:

- The source catalog is `onelake_security` and the source schema is `security_graph`.
- Each node uses its same-named source table and the identifier stated in the prompt.
- `HasIdentity` maps `account.account_id` to `identity.account_id`.
- `HasSession` maps `identity.identity_id` to `session.identity_id`.
- `RecordsEvent` maps `session.session_id` to `event.session_id`.
- `OperatesOn` maps `event.event_id` to `eventresource.event_id`, then `eventresource.resource_id` to `resource.resource_id`.

If a proposal uses the wrong key, label, or relationship direction, reject it and tell AI Chatbot what to change. After approving all proposals, open **Graph** and confirm that the active schema represents:

```text
Account --HasIdentity--> Identity
Identity --HasSession--> Session
Session --RecordsEvent--> Event
Event --OperatesOn--> Resource
```

The graph schema is metadata. Applying it does not copy or rewrite the OneLake data.

## 7. Investigate threats with AI Chatbot

After the graph is active, continue in **Chat**. Select the configured model if the deployment exposes more than one model.

AI Chatbot translates a natural-language investigation into a graph query, executes it, and explains the result. Review the generated query to confirm that the intended labels, relationships, filters, and limits were used.

### 7.1 Trace activity chains to resources

Ask AI Chatbot:

```text
Show up to 50 complete paths from an Account through Identity,
Session, and Event to Resource. Include the account ID, identity ID,
session ID, event name, event time, resource name, and resource type.
```

Equivalent openCypher:

```cypher
MATCH (a:Account)-[:HasIdentity]->(i:Identity)-[:HasSession]->(s:Session)-[:RecordsEvent]->(e:Event)-[:OperatesOn]->(r:Resource)
RETURN elementId(a) AS account_id,
       elementId(i) AS identity_id,
       elementId(s) AS session_id,
       e.event_name AS event_name,
       e.event_time AS event_time,
       r.resource_name AS resource_name,
       r.resource_type AS resource_type
LIMIT 50
```

If no complete paths are returned, ask AI Chatbot which relationship produced no rows. Some events do not contain the session context required to connect every stage.

### 7.2 Find unusually active identities

Ask AI Chatbot:

```text
Between February 1 and March 1, 2017, find the 25 identities with
the most recorded events. Return the identity ID, identity type,
and event count, ordered from highest to lowest.
```

Equivalent openCypher:

```cypher
MATCH (e:Event)
WHERE e.event_time >= datetime('2017-02-01T00:00:00') AND e.event_time < datetime('2017-03-01T00:00:00')
WITH e.identity_id AS arn, count(e) AS event_count
ORDER BY event_count DESC
LIMIT 25
OPTIONAL MATCH (i:Identity {arn: arn})
RETURN arn AS identity_id, i.type AS identity_type, event_count
ORDER BY event_count DESC
```

Event volume is not proof of compromise. Use it as a starting signal alongside event names, source IPs, user agents, and resource activity.

### 7.3 Find activity involving a resource type

Ask AI Chatbot:

```text
Find up to 100 events that operated on S3 bucket resources.
Return the identity ID recorded on the event, source IP address,
event name, event time, resource name, and resource type.
Order the results by event time from newest to oldest.
```

Equivalent openCypher:

```cypher
MATCH (e:Event)-[:OperatesOn]->(r:Resource)
WHERE r.resource_type = 's3bucket'
RETURN e.identity_id AS identity_id,
       e.source_ip AS source_ip,
       e.event_name AS event_name,
       e.event_time AS event_time,
       r.resource_name AS resource_name,
       r.resource_type AS resource_type
ORDER BY e.event_time DESC
LIMIT 100
```

Change `resource_type` to another value present in the dataset, such as `ec2instance`, `volume`, `snapshot`, `iamrole`, `iampolicy`, or `lambdafunction`.

### 7.4 Discover resource paths associated with identities

Ask AI Chatbot:

```text
Show up to 100 Event-to-Resource paths where the Event has a
non-empty identity_id. Return the identity ID with each path.
```

This test avoids requiring a complete session path. It uses the identity stored directly on each event.

### 7.5 Detect shared source infrastructure

Ask AI Chatbot:

```text
Find source IP addresses associated with at least three distinct
identities. Use the source_ip stored on Event and the identity_id
recorded on the same Event. Return the source IP address, distinct
identity count, and identity IDs, ordered by identity count.
```

Shared IP addresses can be benign proxies, NAT gateways, scanners, corporate egress addresses, or automation. Because the dataset is anonymized, treat its IPs as analytical identifiers rather than actionable threat intelligence.

## Cleanup

Stop and remove the PuppyGraph container:

```bash
docker stop puppygraph
docker rm puppygraph
```

When you no longer need the demo:

1. Drop the six tables from the `security_graph` schema or delete the demo lakehouse.
2. Remove the uploaded source archive from the lakehouse `Files` area.
3. Remove unnecessary workspace permissions from the service principal.
4. Delete or rotate credentials created specifically for the demo.

## References

- [Use Iceberg tables with OneLake](https://learn.microsoft.com/fabric/onelake/onelake-iceberg-tables)
- [Querying OneLake Data as a Graph](https://docs.puppygraph.com/getting-started/querying-onelake-data-as-a-graph/)
- [PuppyGraph built-in AI chatbot](https://docs.puppygraph.com/ai/built-in-chatbot/)

