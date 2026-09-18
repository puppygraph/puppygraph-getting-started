# Roblox In-Game Economy Fraud & Bot Tracing Demo

This demo showcases how **PuppyGraph** queries relational data that tracks multi-hop fraud patterns. We are going to track wash trading, asset laundering, mule accounts, and bot rings—without requiring any ETL or data replication.

---

## 📁 Repository Structure

* docker-compose.yaml – Local environment setup for the MySQL databases.
* players_dump.sql – SQL databases containing simulated player accounts, items, and multi-hop trade transaction records.
  * player_service – Manages player profiles, account metadata, and wallet states.
  * trade_service – Tracks item inventories, P2P transactions, and marketplace trade history.
* schema.json – PuppyGraph schema mapping relational tables into graph nodes and edges without data duplication.

---

### 1. Start the Databases
Spin up the MySQL container environment in Command Prompt:

docker compose up -d

### 2. Load the 2 Databases
Put this line into the CMD so that the database can be filled with data:

docker exec -i <CONTAINER_NAME> mysql -u root -p798255 < players_dump.sql

### 3. Add your API Key
Add your Claude API key into your environment or docker-compose.yaml:

PUPPYGRAPH_API_KEY: "<YOUR_PUPPYGRAPH_API_KEY>"
