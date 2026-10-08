# Car Insurance Fraud Detection Demo

## Summary

This demo showcases how PuppyGraph can model and investigate car insurance fraud using a graph-based approach.

By representing drivers, claims, vehicles, accident locations, claim submission channels, dates, and geographic regions as connected entities, investigators can uncover suspicious patterns that are difficult to identify with traditional relational queries.

## Prerequisites

- Docker
- Docker Compose
- Apache Iceberg environment
- PuppyGraph

## Deployment

```bash
docker compose up -d
```

## Data Import

Open Spark SQL:

```bash
docker exec -it spark-iceberg spark-sql
```

Create the database:

```sql
CREATE DATABASE IF NOT EXISTS demo.insurance;
```

### Create Node Tables

```sql
CREATE TABLE demo.insurance.drivers USING iceberg AS
SELECT DISTINCT
    CONCAT('driver_', CAST(claim_number AS STRING)) AS driver_id
FROM raw_insurance;

CREATE TABLE demo.insurance.claims USING iceberg AS
SELECT DISTINCT
    CAST(claim_number AS STRING) AS claim_id,
    CAST(total_claim AS DOUBLE) AS total_claim,
    CAST(injury_claim AS DOUBLE) AS injury_claim,
    CAST(`fraud reported` AS STRING) AS fraud_reported
FROM raw_insurance;

CREATE TABLE demo.insurance.vehicles USING iceberg AS
SELECT DISTINCT
    CONCAT(
        'vehicle_',
        regexp_replace(CAST(vehicle_category AS STRING), ' ', '_'),
        '_',
        regexp_replace(CAST(vehicle_color AS STRING), ' ', '_'),
        '_',
        CAST(age_of_vehicle AS STRING),
        '_',
        CAST(claim_number AS STRING)
    ) AS vehicle_id
FROM raw_insurance;

CREATE TABLE demo.insurance.accident_sites USING iceberg AS
SELECT DISTINCT
    CONCAT('site_', regexp_replace(CAST(accident_site AS STRING), ' ', '_')) AS site_id
FROM raw_insurance;

CREATE TABLE demo.insurance.channels USING iceberg AS
SELECT DISTINCT
    CONCAT('channel_', regexp_replace(CAST(channel AS STRING), ' ', '_')) AS channel_id
FROM raw_insurance;

CREATE TABLE demo.insurance.claim_dates USING iceberg AS
SELECT DISTINCT
    CONCAT('date_', regexp_replace(CAST(claim_date AS STRING), '/', '_')) AS date_id
FROM raw_insurance;

CREATE TABLE demo.insurance.zipcodes USING iceberg AS
SELECT DISTINCT
    CONCAT('zip_', CAST(zip_code AS STRING)) AS zip_id
FROM raw_insurance;
```

### Create Edge Tables

```sql
CREATE TABLE demo.insurance.driver_claim_edges USING iceberg AS
SELECT DISTINCT
    CONCAT('filed_', CAST(claim_number AS STRING)) AS edge_id,
    CONCAT('driver_', CAST(claim_number AS STRING)) AS driver_id,
    CAST(claim_number AS STRING) AS claim_id
FROM raw_insurance;

CREATE TABLE demo.insurance.claim_vehicle_edges USING iceberg AS
SELECT DISTINCT
    CONCAT('claim_vehicle_', CAST(claim_number AS STRING)) AS edge_id,
    CAST(claim_number AS STRING) AS claim_id,
    CONCAT('vehicle_', regexp_replace(CAST(vehicle_category AS STRING), ' ', '_'),'_',regexp_replace(CAST(vehicle_color AS STRING), ' ', '_'),'_',CAST(age_of_vehicle AS STRING),'_',CAST(claim_number AS STRING)) AS vehicle_id
FROM raw_insurance;

CREATE TABLE demo.insurance.claim_zip_edges USING iceberg AS
SELECT DISTINCT
    CONCAT('claim_zip_', CAST(claim_number AS STRING)) AS edge_id,
    CAST(claim_number AS STRING) AS claim_id,
    CONCAT('zip_', CAST(zip_code AS STRING)) AS zip_id
FROM raw_insurance;

CREATE TABLE demo.insurance.claim_site_edges USING iceberg AS
SELECT DISTINCT
    CONCAT('claim_site_', CAST(claim_number AS STRING)) AS edge_id,
    CAST(claim_number AS STRING) AS claim_id,
    CONCAT('site_', regexp_replace(CAST(accident_site AS STRING), ' ', '_')) AS site_id
FROM raw_insurance;

CREATE TABLE demo.insurance.claim_channel_edges USING iceberg AS
SELECT DISTINCT
    CONCAT('claim_channel_', CAST(claim_number AS STRING)) AS edge_id,
    CAST(claim_number AS STRING) AS claim_id,
    CONCAT('channel_', regexp_replace(CAST(channel AS STRING), ' ', '_')) AS channel_id
FROM raw_insurance;

CREATE TABLE demo.insurance.claim_date_edges USING iceberg AS
SELECT DISTINCT
    CONCAT('claim_date_', CAST(claim_number AS STRING)) AS edge_id,
    CAST(claim_number AS STRING) AS claim_id,
    CONCAT('date_', regexp_replace(CAST(claim_date AS STRING), '/', '_')) AS date_id
FROM raw_insurance;
```

## Graph Model

Nodes:
- drivers
- claims
- vehicles
- accident_sites
- channels
- claim_dates
- zipcodes

Relationships:
- (drivers)-[:FILED]->(claims)
- (claims)-[:INVOLVES]->(vehicles)
- (claims)-[:OCCURRED_AT]->(accident_sites)
- (claims)-[:OCCURRED_IN]->(zipcodes)
- (claims)-[:SUBMITTED_THROUGH]->(channels)
- (claims)-[:HAPPENED_ON]->(claim_dates)

## Example Queries

```cypher
MATCH (d:drivers)-[:FILED]->(c:claims)
RETURN d,c
LIMIT 20
```

```cypher
MATCH (d:drivers)-[:FILED]->(c:claims)-[:INVOLVES]->(v:vehicles)
WHERE c.total_claim > 20000
RETURN d,c,v
LIMIT 25
```
