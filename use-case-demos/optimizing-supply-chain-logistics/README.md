#  Optimizing Supply Chain Logistics Demo

## Summary
In this demo, PuppyGraph navigates a complex supply chain to optimize logistics and sales performance.  
We illustrate how to identify top-selling products and verify their inventory status, ensuring they are adequately stocked.  
Additionally, the demo addresses products with no sales, providing insights into potential market adjustments.  
It also showcases strategic reallocation of resources, offering solutions for transferring necessary parts from the nearest inventory when they are urgently needed at specific locations.  
This holistic view facilitates efficient management of supply and demand within the supply chain.

- **`README.md`**: Provides an overview of the project, including setup instructions and key details about the demo.
- **`csv_data/`**: Contains randomly generated CSV files representing customer orders, product inventories, materials, and locations.
- **`sql/init.sql`**: Creates the `supply` schema and tables in PostgreSQL and imports the CSV data.
- **`docker-compose.yaml`**: Starts PostgreSQL with the data loaded and PuppyGraph.
- **`schema.json`**: Graph schema mapping the tables to vertices and edges.

## Prerequisites:
- Docker
- Docker Compose

## Note:
The data preparation below populates example data for this demo.
For real-world applications, you can connect PuppyGraph directly to your existing data warehouse, enabling real-time supply chain analytics without these steps.

## Demo Data Preparation
Start PostgreSQL and PuppyGraph:
```bash
docker compose up -d
```
PostgreSQL runs `sql/init.sql` on first start, which creates the `supply` schema and tables and imports the CSV files.

## Modeling the Graph
1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
- Username: `puppygraph`
- Password: `puppygraph123`

2. Upload the schema:
- Click **Upload Schema**, select the file `schema.json` and click **Upload**.

## Querying the Graph

- Navigate to the Query panel on the left side. The **Graph Query** tab offers an interactive environment for querying the graph using Gremlin and openCypher.
- After each query, remember to clear the graph panel before executing the next query to maintain a clean visualization. You can do this by clicking the "Clear" button located in the top-right corner of the page.

Example Queries:
1. Query the top 5 best-selling products.
```gremlin
g.V().hasLabel('ProductOrder').as('order')
  .group().by('productid').by(__.values('quantity').sum()).as('sales')
  .order(local).by(values, desc)
  .unfold()
  .limit(5)
  .project('productid', 'total_sales')
    .by(keys)
    .by(values)
```

2. Query the 5 worst selling products.
```gremlin
g.V().hasLabel('ProductOrder').as('order')
  .group().by('productid').by(__.values('quantity').sum()).as('sales')
  .order(local).by(values, asc)
  .unfold()
  .limit(5)
  .project('productid', 'total_sales')
    .by(keys)
    .by(values)
```

3. Query the orders for the best-selling products and their materials, as well as whether the inventory is sufficient.
```gremlin
g.V("Product[88]").as('product')
  .union(
    __.out('ProductInventory').out('InventoryLocation').path(),
    __.in('ProOrderToPro').path(),
    __.out('ProductComposition').out('MaterialInventory').out('MatInventoryLocation').path(),
    __.out('ProductComposition').in('MatOrderToMat').out('MatOrderToFac').out('FactoryLocation').path()
  )
```

4. Query the path from a specific customer's orders through the products, their compositions, 
   the material orders, the factories producing those materials, and finally to the locations of those factories.
```gremlin
g.V("Customer[179]")
  .in('ProOrderToCus')
  .out('ProOrderToPro')
  .out('ProductComposition')
  .in('MatOrderToMat')
  .out('MatOrderToFac')
  .out('FactoryLocation')
  .path()
```

5. Query the distance between the product warehouse and customers, and sort them in descending order of proximity.
```gremlin
g.V("Product[88]")
  .out('ProductInventory').as('inventory')
  .out('InventoryLocation').as('inventoryLocation')
  .outE('Distance').as('distanceEdge')
  .inV().hasLabel('Location').as('location')
  .in('CustomerLocation').has('customername', 'Customer 179').as('customer')
  .select('distanceEdge')
  .order().by('distance')
  .path()
```

## Cleanup and Teardown
- To stop and remove the containers:
```bash
docker compose down
```
