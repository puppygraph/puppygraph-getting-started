# Google Analytics 360 Customer Journey Graph Demo

## Summary

This demo showcases how to analyze website customer journeys using PuppyGraph's graph querying capabilities, running directly over MySQL tables with no ETL required.
A visit to an online store is a path: a visitor lands on a page, moves from page to page, and either buys something or leaves. PuppyGraph turns those paths into a graph, so you can follow a single visitor's journey, see which pages lead to a purchase, and find where shoppers drop out of checkout.

By modeling page views as a graph, we can easily analyze:

- The full journey of any single visit
- The routes buyers take from basket to order
- Where buyers enter the site, and how often they come back before buying
- Which landing pages convert best
- Where shoppers go after the basket when they don't buy

The data is one day (2017-08-01) of the [Google Analytics 360 sample dataset](https://support.google.com/analytics/answer/7586738) for the Google Merchandise Store, exported from the BigQuery public table `bigquery-public-data.google_analytics_sample.ga_sessions_20170801` with one row per hit (13,233 hits across 2,556 visits).
This demo uses MySQL to store the data.

**Overview:**

- **`docker-compose.yaml`**: Defines the docker services needed to run the demo. This includes both the MySQL database and the PuppyGraph instance.
- **`data/`**: Contains the GA360 export as `sample_data.csv` and the MySQL setup script `init.sql`, which loads the CSV and builds the tables the graph is mapped from.
- **`schema.json`**: Maps the tables to `Page`, `Session` and `Visitor` vertices and to the edges between them: `LANDED_ON` for a visit's first page, `NEXT` for each move between pages, `LINKS_TO` for page-to-page traffic, and `HAD_VISIT` for a visitor's visits.

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
- "Which buyers visited the store more than once?"

### Using the Query Panel

To run the example Cypher queries below yourself, navigate to the Query panel on the left side and select **Cypher**. Queries that return a path are drawn on the **Graph** tab; queries that return columns appear on the **Table** tab.

Pages and visits appear as dots on the **Graph** tab. Click one to see its properties, such as `page_path`.

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

2. Show where buyers enter the site: each visit that ended in a purchase, linked to its first page

```cypher
MATCH p = (s:Session)-[:LANDED_ON]->(:Page)
WHERE s.purchased
RETURN p
```

3. Show buyers who visited more than once that day, with all of their visits and the page each visit started on

```cypher
MATCH (v:Visitor)-[:HAD_VISIT]->(b:Session)
WHERE b.purchased AND v.sessions >= 2
MATCH p = (v)-[:HAD_VISIT]->(:Session)-[:LANDED_ON]->(:Page)
RETURN p
```

4. Show the paths buyers took from the basket to a completed order, keeping only moves made in the same visit

```cypher
MATCH p = (:Page {page_path: '/basket.html'})-[:NEXT*3..4]->(:Page {page_path: '/ordercompleted.html'})
WITH p, relationships(p) AS m
WHERE all(r IN m WHERE r.session_id = head(m).session_id)
  AND reduce(prev = head(m).step - 1, r IN m |
             CASE WHEN r.step = prev + 1 THEN r.step ELSE -1 END) <> -1
RETURN p
```

5. Find the landing pages with the highest conversion rate, among pages that started at least 20 visits

```cypher
MATCH (s:Session)-[:LANDED_ON]->(p:Page)
WITH p, count(s) AS sessions, sum(CASE WHEN s.purchased THEN 1 ELSE 0 END) AS purchases
WHERE sessions >= 20
RETURN p.page_path AS landing_page, sessions, purchases,
       round(100.0 * purchases / sessions, 1) AS conversion_pct
ORDER BY conversion_pct DESC
LIMIT 10
```

6. See where shoppers go after the basket, counting visits that ended in a purchase and visits that did not

```cypher
MATCH (:Page {page_path: '/basket.html'})-[l:LINKS_TO]->(next:Page)
RETURN next.page_path AS next_page,
       l.buyer_sessions AS buyers,
       l.sessions - l.buyer_sessions AS non_buyers
ORDER BY non_buyers DESC, next_page
LIMIT 10
```

## Cleanup and Teardown

- To stop and remove the containers and the loaded data, run:

```bash
docker compose down -v
```
