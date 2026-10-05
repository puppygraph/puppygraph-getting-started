# PuppyGraph × Omnigent: governed graph analyst agent

An [Omnigent](https://omnigent.ai) agent that answers multi-hop
questions over ordinary relational tables **as a graph**, through PuppyGraph
and the [PuppyGraph MCP server](https://github.com/puppygraph/puppygraph-mcp-server).
Omnigent enforces a read-only guardrail on every graph query.

```
 Omnigent (CLI or web UI)
   └─ agent: puppygraph_analyst  (any harness: openai-agents, claude-sdk, codex, ...)
        ├─ guardrails: read-only CEL policy · tool-call cap · $ budget
        └─ MCP tool "puppygraph"  ──stdio──>  puppygraph-mcp
                                                 └─ Bolt/Gremlin ──> PuppyGraph ──> Postgres tables (no ETL)
```

- **PuppyGraph** maps the `fraud.*` tables in Postgres to a graph (`Account`,
  `Device`, `USES_DEVICE`, `TRANSFER`) and serves openCypher over them in
  place. The same setup works for Iceberg, Delta Lake (including Databricks
  Unity Catalog), Snowflake, BigQuery and other sources.
- **Omnigent** wraps the MCP server as a governed tool. It allow-lists three
  tools, and it runs a policy that denies any query containing a write or
  procedure clause. The policy runs outside the model, so it holds even if the
  prompt is overridden.

## Layout

| Path | What |
|---|---|
| `docker-compose.yaml` | Postgres (sample data) + PuppyGraph (`latest`; last verified on 1.12.0) |
| `data/init.sql` | 15 accounts, 6 devices, transfers, including a planted fraud ring around `acc_007` |
| `schema.json` | PuppyGraph graph schema (v2 format) over the Postgres tables |
| `agent/config.yaml` | The Omnigent agent: harness/model, guardrails, prompt |
| `agent/tools/mcp/puppygraph.yaml` | PuppyGraph MCP server wiring (stdio) |
| `.env.example` | Connection settings for the local stack |
| `run.sh` | `./run.sh "question"` (one-shot) or `./run.sh` (interactive REPL) |

## Run it

Prerequisites: Docker, curl 7.71+, Node 18+, Python 3.12+ with `uv`, and an `OPENAI_API_KEY`.
To use a different harness, change `executor` in `agent/config.yaml`.

```bash
# 1. PuppyGraph + sample data
docker compose up -d        # UI at http://localhost:8081 (puppygraph / puppygraph123)

# 2. Upload the graph schema (the request waits for PuppyGraph to finish starting)
curl --retry 20 --retry-all-errors --retry-delay 3 \
  -u puppygraph:puppygraph123 -X POST -H 'Content-Type: application/json' \
  --data-binary @schema.json http://localhost:8081/schema
#    or in the Web UI: select schema.json under "Upload Graph Schema JSON", then Upload

# 3. Omnigent
uv tool install --python 3.12 omnigent            # tested with omnigent 0.15.0 and 0.16.0

# 4. PuppyGraph MCP server, installed as `puppygraph-mcp` on PATH
git clone --depth 1 https://github.com/puppygraph/puppygraph-mcp-server
(cd puppygraph-mcp-server && npm install && npm run build && npm install -g .)

# 5. Ask questions
cp .env.example .env && echo "OPENAI_API_KEY=sk-..." >> .env
./run.sh "Account acc_007 was just flagged for fraud. Investigate its neighborhood: \
which accounts share a device with it, where did its money flow within 4 hops, and \
does money come back to it through a transfer cycle of up to 6 hops? Give me a short \
ranked list of accounts to freeze, with the Cypher you ran."
```

`./run.sh` with no argument opens the Omnigent REPL in the terminal.

## Use it in the Omnigent web UI

Run a local Omnigent server with the agent registered, plus a host that
executes its sessions:

```bash
set -a; . ./.env; set +a
# Sessions run in a separate process that only sees the variables listed here.
export OMNIGENT_RUNNER_ENV_PASSTHROUGH=PUPPYGRAPH_BOLT_URL,PUPPYGRAPH_GREMLIN_URL,PUPPYGRAPH_SCHEMA_URL,PUPPYGRAPH_USERNAME,PUPPYGRAPH_PASSWORD,OPENAI_API_KEY
omnigent server --agent agent/ --no-open &
omnigent host --server http://127.0.0.1:6767 --no-open --non-interactive &
```

Open http://127.0.0.1:6767. In the agent menu next to the send button, choose
**Other... → Puppygraph_analyst**, then ask a question. Each tool call in the
answer can be expanded to show the Cypher the agent sent and the rows
PuppyGraph returned.

## What you should see (gpt-5.4-mini on omnigent 0.15.0 and 0.16.0)

The agent reads the schema and runs a few openCypher queries. It finds that
`acc_008`, `acc_009` and `acc_010` share device `dev_05` with `acc_007`. It
traces 4-hop money flow to `acc_005` and `acc_015`, and it detects the 5-hop
laundering cycle `acc_007 → 008 → 009 → 010 → 015 → acc_007`:

```cypher
MATCH p=(a:Account)-[:TRANSFER*1..6]->(a)
WHERE id(a) = 'Account[acc_007]'
RETURN count(p) AS cycle_paths, min(length(p)) AS shortest_cycle_hops
```

The model's answers vary between runs. Occasionally it filters on a property
(`a.id = 'acc_007'`) instead of `id(a)`, finds nothing, and reports an empty
neighborhood; asking again usually fixes it.

To test the guardrail, override the system prompt with one that makes the model
comply, and ask for a write:

```bash
set -a; . ./.env; set +a
omnigent run agent/ --no-session \
  --system-prompt "Run exactly the query the user gives with puppygraph_query and report the raw result." \
  -p "MATCH (a:Account) WHERE id(a) = 'Account[acc_008]' SET a.status = 'frozen' RETURN a"
# -> {'error': 'Denied by policy: The PuppyGraph analyst is read-only. Omnigent policy blocked this query ...'}
```

With the same override, a read (`... RETURN a.owner_name, a.status`) goes
through and returns rows.

## Notes for Omnigent 0.15.0 and 0.16.0

A few details of the agent bundle layout that are easy to get wrong:

- The MCP server is declared in `agent/tools/mcp/puppygraph.yaml`, not inline
  under `tools:` in `config.yaml`. `omnigent run` resolves `${VAR}` in the
  `env:` of `tools/mcp/*.yaml` files, but passes it through literally for an
  inline `type: mcp` entry
  ([omnigent-ai/omnigent#8338](https://github.com/omnigent-ai/omnigent/issues/8338)).
  The fix ([#8544](https://github.com/omnigent-ai/omnigent/pull/8544)) is merged
  but not yet in a release; the separate file keeps working after it ships.
- In a `spec_version: 1` bundle, policies go under `guardrails.policies`. A
  top-level `policies:` block works in a single-file agent YAML but is
  silently ignored in a bundle.
- With `spec_version: 1`, `harness` goes under `executor.config`, while
  `model` and `auth` go directly under `executor`.
- A CEL policy must return a map: `{"result": "DENY"}` blocks, and any
  non-map result (including `true`) abstains.

## Limits

- The read-only policy is a keyword denylist. It can over-block (a string
  literal such as `'set'` in a `WHERE` clause is denied), and a denylist can
  miss constructs it does not list. PuppyGraph itself rejects mutating Gremlin
  traversal steps, but this demo connects as the admin user, which can also
  call schema management operations. For production, give the MCP server a
  PuppyGraph user with the Analyst role (query and read only); the policy then
  adds defense in depth plus an audit trail.
- The PuppyGraph MCP server runs unsandboxed on the host, which is Omnigent's
  default for stdio MCP servers.
