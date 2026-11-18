# Google Analytics 360 Customer Journey Graph Demo

## Summary

This demo showcases how to analyze website customer journeys using PuppyGraph's graph querying capabilities, running directly over MySQL tables with no ETL required.
A visit to an online store is a path: a visitor lands on a page, moves from page to page, and either buys something or leaves. PuppyGraph turns those paths into a graph, so you can follow a single visitor's journey, see which pages lead to a purchase, and find where shoppers drop out of checkout.

By modeling page views as a graph, we can easily analyze:

- The full journey of any single visit
- Which landing pages convert best
- The steps visitors take right before completing an order
- Where shoppers go after the basket when they don't buy

The data is one day (2017-08-01) of the [Google Analytics 360 sample dataset](https://support.google.com/analytics/answer/7586738) for the Google Merchandise Store, exported from the BigQuery public table `bigquery-public-data.google_analytics_sample.ga_sessions_20170801` with one row per hit (13,233 hits across 2,556 visits).
This demo uses MySQL to store the data.

**Overview:**

- **`docker-compose.yaml`**: Defines the docker services needed to run the demo. This includes both the MySQL database and the PuppyGraph instance.
- **`data/`**: Contains the GA360 export as `sample_data.csv` and the MySQL setup script `init.sql`, which loads the CSV and builds the tables the graph is mapped from.
- **`schema.json`**: Maps the tables to the graph described below.

**Graph model:**

| Element | Source table | Description |
| --- | --- | --- |
| `Page` vertex | `pages` | One per page path, with hit count, number of visits, average seconds on page, and entrance and exit rates. |
| `Session` vertex | `sessions` | One per visit, with device, browser, country, hit count, `revenue` in US dollars and `purchased`. |
| `LANDED_ON` edge | `landings` | From a `Session` to the first page of that visit. |
| `NEXT` edge | `transitions` | From one `Page` to the next page viewed in the same visit. `session_id` says which visit it belongs to, and `step` numbers the moves within the visit (1, 2, 3, ...). Repeated hits on the same page are skipped. |

GA360 repeats a visit's total revenue on every hit of that visit, so `init.sql` stores revenue once per visit on the `Session` vertex. A visit is identified by `fullVisitorId` plus `visitId`, because `visitId` alone is the visit's start time and can be shared by different visitors.

## Prerequisites:

- Docker
- An API key for an AI model provider (optional), to ask questions in natural language with PuppyGraph AI. See the [PuppyGraph AI documentation](https://docs.puppygraph.com/ai/puppygraph-ai/) for supported providers.

## Deployment

- Start MySQL and PuppyGraph by running:

```bash
docker compose up -d
```

Example output:

```bash
[+] Running 3/3
✔ Network puppy-mysql     Created
✔ Container mysql         Started
✔ Container puppygraph    Started
```

MySQL runs `data/init.sql` the first time it starts, which takes about 10 seconds. It is done when the following command prints `ready for connections` with `port: 3306`:

```bash
docker logs mysql 2>&1 | grep "port: 3306"
```

## Modeling the Graph

1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:

- Username: `puppygraph`
- Password: `puppygraph123`

2. Upload the schema:

- On the **Upload Schema** card, click **Upload JSON**, then **Select Schema File**, choose `schema.json` and click **Upload**.
- Alternatively, you can upload the schema via the following command:

```bash
curl -XPOST -H "content-type: application/json" --data-binary @./schema.json --user "puppygraph:puppygraph123" localhost:8081/schema
```

PuppyGraph downloads the MySQL JDBC driver from Maven Central the first time the schema is uploaded, using the `driverUrl` in `schema.json`.

## Querying the Graph

You can query the graph in two ways: ask questions in natural language with PuppyGraph AI, or write Cypher yourself in the Query panel.

### Using PuppyGraph AI

PuppyGraph AI is a built-in chatbot that turns natural language questions into Cypher, runs them over the graph, and shows the generated query along with the results.

1. The first time, click **Add API Key** under the question box on the **Home** page and save your key. You can update the key later in **Settings**. PuppyGraph AI uses Anthropic's Claude models by default; to use an OpenAI-style API or your own model endpoint, see the [PuppyGraph AI documentation](https://docs.puppygraph.com/ai/puppygraph-ai/).
2. Type a question in the box on the **Home** page, or click **Ask AI** on the **Graph** page. For example:

- "What data do I have?"
- "Which landing pages lead to the most purchases?"
- "Show the journey of the visit with the highest revenue."

### Using the Query Panel

To run the example Cypher queries below yourself, navigate to the Query panel on the left side and select **Cypher**. Queries that return a path are drawn on the **Graph** tab; queries that return columns appear on the **Table** tab.

After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization.
You can do this by clicking the **Clear Canvas** button located in the top-right corner of the page.

Example Queries:

1. Show the journey of the visit with the highest revenue

```cypher
MATCH (s:Session)
WITH s ORDER BY s.revenue DESC LIMIT 1
MATCH p = (:Page)-[r:NEXT]->(:Page)
WHERE r.session_id = s.session_id
RETURN p
```

2. Compare purchases and revenue by device

```cypher
MATCH (s:Session)
WHERE s.purchased
RETURN s.device AS device, count(s) AS purchases, round(sum(s.revenue), 2) AS revenue
ORDER BY revenue DESC
```

3. Find the landing pages with the highest conversion rate, among pages that started at least 20 visits

```cypher
MATCH (s:Session)-[:LANDED_ON]->(p:Page)
WITH p, count(s) AS sessions, sum(CASE WHEN s.purchased THEN 1 ELSE 0 END) AS purchases
WHERE sessions >= 20
RETURN p.page_path AS landing_page, sessions, purchases,
       round(100.0 * purchases / sessions, 1) AS conversion_pct
ORDER BY conversion_pct DESC
LIMIT 10
```

4. Find the two pages visitors viewed right before completing an order. The `WHERE` clause keeps only moves made one after the other in the same visit.

```cypher
MATCH (a:Page)-[r1:NEXT]->(b:Page)-[r2:NEXT]->(:Page {page_path: '/ordercompleted.html'})
WHERE r1.session_id = r2.session_id AND r2.step = r1.step + 1
RETURN a.page_path AS two_steps_before, b.page_path AS one_step_before, count(*) AS orders
ORDER BY orders DESC
LIMIT 10
```

To see the same paths drawn on the **Graph** tab, replace the `RETURN` clause with `RETURN p` and start the pattern with `MATCH p = `.

5. See where shoppers go after the basket, split by whether the visit ended in a purchase

```cypher
MATCH (:Page {page_path: '/basket.html'})-[r:NEXT]->(next:Page)
MATCH (s:Session {session_id: r.session_id})
RETURN next.page_path AS next_page,
       sum(CASE WHEN s.purchased THEN 1 ELSE 0 END) AS buyers,
       sum(CASE WHEN s.purchased THEN 0 ELSE 1 END) AS non_buyers
ORDER BY non_buyers DESC
LIMIT 10
```

## Cleanup and Teardown

- To stop and remove the containers and the loaded data, run:

```bash
docker compose down -v
```
