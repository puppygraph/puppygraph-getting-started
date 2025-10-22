# Telecom Churn & Call-Network Graph Demo

## Summary

This demo builds a customer graph from synthetic telecom data (calls, family plans, support tickets, devices, locations) to demonstrate how PuppyGraph can be applied in the telecommunications industry using existing relational databases.


## Prerequisites
- **Python 3**
- **pip** (and optionally a virtual environment like `venv` or conda)
- Python packages:
  - `pandas`, `numpy`, `duckdb`
- Docker
- Docker Compose 
---

## Quickstart

### 1) Install Python packages
```bash
pip install pandas numpy duckdb
```

### 2) Generate the Dataset
```bash
python Dataset_generator.py
```
This creates `duckdb/my_project.duckdb` with these tables:

- `customers`
- `customer_calls`
- `family_plans`
- `customer_support`
- `customer_devices`
- `customer_locations`

## Deployment

Run
```bash
docker compose up -d
```
Open http://localhost:8081 and sign in with:
- username: puppygraph
- password: puppygraph123

Select the file schema.json in the Upload Graph Schema JSON section and click on Upload.

## Querying the graph

1. Sort, in descending order, the number of phone calls phone numbers have had with churned customers
```groovy
g.V().hasLabel('Customer').has('churned', 0).as('c')  
  .out('Cust_Number')       
  .both('customer_calls')  
  .in('Cust_Number')        
  .has('churned', 1)                                  
  .group().by(select('c').values('customer_id')).by(count())
  .order(local).by(values, desc)
```
2. Top 5% caller’s customer support tickets

```groovy
topCallers = g.V().hasLabel('Phone_Number')
  .order().by(__.outE('customer_calls').count(), desc)
  .limit((int)(g.V().hasLabel('Phone_Number').count().next() * 0.05))
  .id().toList()

g.V(topCallers)
  .in('Cust_Number').out('Filed')
  .values('ticket_id')
```
3. Find the pairs of customers who each have escalated customer support tickets that have called one another

```groovy
g.V().hasLabel('Customer').as('c')
  .where(
    out('Filed').has('escalated', true)
  )
  .out('Cust_Number').out('customer_calls').in('customer_calls')
  .in('Cust_Number').as('callee')
  .where(
    __.out('Filed').has('escalated', true)
  )
  .where(neq('c'))
  .select('c', 'callee').dedup()
```

4. Filter for family plans where no one calls each other
```groovy
g.V().hasLabel('Family_Plan').as('fp')
  .out('Member').as('m1')
  .out('Cust_Number').as('pn1')
  .not(
    __.out('customer_calls')            
      .in('Cust_Number')                
      .where(__.in('Member').as('fp')) 
  )
  .select('fp')
  .dedup()
```

5. Sort Family Plans by the number of intra-family calls
```groovy
g.V().hasLabel("Family_Plan").as("fp")
  .out("Member").as("member")
  .out("Cust_Number").as("sourcePhone")
  .out("customer_calls").as("targetPhone")
  .in("Cust_Number").as("targetCustomer")
  .where(__.in("Member").where(eq("fp")))
  .where(__.select("targetCustomer").where(neq("member")))  
  .select("fp")
  .group()
    .by()
    .by(count())
  .order(local)
    .by(values, desc)
```

## Clean up

- to stop containers, run
```bash
docker compose down
```
