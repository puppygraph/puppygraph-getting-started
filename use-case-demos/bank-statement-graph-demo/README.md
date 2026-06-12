# Bank Statement Graph Demo

## Summary

This demo uses PuppyGraph to model financial relationships between bank accounts, statements, and transactions extracted from PDF bank statements, making it easy to identify hidden connections between entities and follow money flows across accounts.

The pipeline uses CocoIndex and GPT-4o to extract structured data from PDF bank statements into PostgreSQL, which PuppyGraph then models as a graph.

**Overview:**
- **`docker-compose.yaml`**: Defines the Docker services needed to run the demo. This includes both the PostgreSQL database and the PuppyGraph instance.
- **`bank_data/`**: Place your PDF bank statements here before running the pipeline.
- **`coco_main.py`**: Extraction pipeline that reads PDFs, extracts structured data using GPT-4o, and inserts into PostgreSQL.
- **`schema.json`**: PuppyGraph graph schema defining nodes and edges over the PostgreSQL tables.

## Prerequisites

- Python 3.11+
- Docker
- An OpenAI API key (Tier 2 recommended)

## Deployment

### (1) Install Python dependencies

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### (2) Prepare environment variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_key
POSTGRES_DSN=postgresql://myuser:mypassword@localhost:5432/myapp_db
POSTGRES_SCHEMA=public
COCOINDEX_DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/myapp_db
```

### (3) Start PostgreSQL and PuppyGraph

```bash
docker compose up -d
```

Example output:

```bash
[+] Running 3/3
✔ Network puppy-postgres    Created
✔ Container postgres        Started
✔ Container puppygraph      Started
```

### (4) Run the extraction pipeline

Place bank statement PDFs in `bank_data/`, then run:

```bash
uv run coco_main.py
```

This will extract structured data from each PDF and populate three PostgreSQL tables:

- `accounts` — one row per unique account holder
- `statements` — one row per PDF statement
- `transactions` — one row per transaction line, including `counterparty` and `payment_rail` extracted from the description field

## PuppyGraph Setup

1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
   - Username: `puppygraph`
   - Password: `puppygraph123`

2. Upload the schema:
   - Select `schema.json` in the Upload Graph Schema JSON section and click Upload.

## Querying the Graph

Navigate to the Query panel on the left side. The Graph Query tab offers an interactive environment for querying the graph using Cypher.

After each query, click the **Clear Canvas** button in the top-right corner before executing the next query to maintain a clean visualization.

**Graph model:**

```
(Account) ──OwnsStatement──> (Statement) ──HasTransaction──> (Transaction)
    │                                                               │
    └─────────────────OwnsTransaction──────────────────────────────┘
                                                                   │
                                                         TransactsWith
                                                                   │
                                                                   ▼
                                                           (Counterparty)
```

- **Account** — bank account holder
- **Statement** — one PDF statement per account per period
- **Transaction** — individual transaction row with `counterparty` and `payment_rail`
- **Counterparty** — any named entity extracted from transaction descriptions

**Note:** The `counterparty` field is parsed by GPT-4o from each transaction's raw description string. Cross-account relationships are only discoverable where one account's statement explicitly names another account in its descriptions.

### Example Queries

1. Find the most connected counterparty across all accounts

```cypher
MATCH (a:Account)-[:OwnsTransaction]->(t:Transaction)-[:TransactsWith]->(c:Counterparty)
WITH c, COUNT(DISTINCT a) AS account_count
WHERE account_count > 1 AND c.counterparty <> 'SELF'
WITH c ORDER BY account_count DESC LIMIT 1
MATCH path = (a2:Account)-[:OwnsTransaction]->(t2:Transaction)-[:TransactsWith]->(c)
RETURN path
```

2. Show all outgoing payments from the hub account

```cypher
MATCH path = (a:Account {account_holder: 'CYBERCRAFT SYSTEMS'})-[:OwnsTransaction]->(t:Transaction)-[:TransactsWith]->(c:Counterparty)
WHERE t.debit IS NOT NULL AND c.counterparty <> 'SELF'
RETURN path
```

## Cleanup and Teardown

To stop and remove the containers, run:

```bash
docker compose down
```

To also remove the PostgreSQL data volume:

```bash
docker compose down -v
```