#  E-Commerce Order Exploration & Analysis Demo

## Summary
This e-commerce analytics demo showcases a comprehensive knowledge graph that connects orders, products, sellers, and more, offering a multidimensional view of transactions.  
Starting from individual orders, we expand the analysis to include associated products and sellers, while dynamically filtering data by delivery status to highlight key metrics in the visualization.  
This approach provides deeper insights into e-commerce operations, supporting better decision-making and improved customer service strategies.

- **`README.md`**: Provides an overview of the project, including setup instructions and key details about the demo.

- **`docker-compose.yaml`**: Sets up the necessary services using Docker, defining containers and environments such as databases and applications for running the demo.

- **`CsvToParquet.py`**: Converts CSV files into Parquet format for easier data import into Iceberg.

## Prerequisites:
- Docker
- Docker Compose
- Python 3


## Data Preparation
- Download the Brazilian E-Commerce Public Dataset:
```bash
curl -L -o archive.zip https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce
```
You can view more details about the dataset on the [Kaggle website](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

- Unzip the downloaded file:
```bash
unzip archive.zip -d ./csv_data/
```
- Convert CSV files to Parquet format:
```bash
python3 CsvToParquet.py ./csv_data ./parquet_data
```

## Deployment
- Start the Apache Iceberg services and PuppyGraph by running:
```bash
sudo docker compose up -d
```
Example output:
```bash
[+] Running 6/6
✔ Network puppy-iceberg         Created
✔ Container minio               Started
✔ Container mc                  Started
✔ Container iceberg-rest        Started
✔ Container spark-iceberg       Started
✔ Container puppygraph          Started
```

## Data Import
- Start the Spark-SQL shell to access Iceberg:
```bash
sudo docker exec -it spark-iceberg spark-sql
```
The shell prompt will appear as:
```shell
spark-sql ()>
```

- Execute the following SQL commands to create tables and import data:
```sql
CREATE DATABASE brazil_e_commerce;

CREATE EXTERNAL TABLE brazil_e_commerce.olist_customers (
  customer_unique_id        STRING,
  customer_zip_code_prefix  STRING,
  customer_city             STRING,
  customer_state            STRING
) USING iceberg;

CREATE EXTERNAL TABLE brazil_e_commerce.olist_geolocation (
  geolocation_zip_code_prefix   STRING,
  geolocation_lat               DOUBLE,
  geolocation_lng               DOUBLE,
  geolocation_city              STRING,
  geolocation_state             STRING
) USING iceberg;

CREATE EXTERNAL TABLE brazil_e_commerce.olist_order_items (
  unique_item_id        STRING,
  order_id              STRING,
  order_item_id         INT,
  product_id            STRING,
  seller_id             STRING,
  shipping_limit_date   TIMESTAMP,
  price                 FLOAT,
  freight_value         FLOAT
) USING iceberg;

CREATE EXTERNAL TABLE brazil_e_commerce.olist_order_payments (
  payment_id            STRING,
  order_id              STRING,
  payment_sequential    INT,
  payment_type          STRING,
  payment_installments  INT,
  payment_value         FLOAT
) USING iceberg;

CREATE EXTERNAL TABLE brazil_e_commerce.olist_order_reviews (
  review_id                 STRING,
  order_id                  STRING,
  review_score              INT,
  review_comment_title      STRING,
  review_comment_message    STRING,
  review_creation_date      TIMESTAMP,
  review_answer_timestamp   TIMESTAMP
) USING iceberg;

CREATE EXTERNAL TABLE brazil_e_commerce.olist_orders (
  order_id                      STRING,
  customer_unique_id            STRING,
  order_status                  STRING,
  order_purchase_timestamp      TIMESTAMP,
  order_approved_at             TIMESTAMP,
  order_delivered_carrier_date  TIMESTAMP,
  order_delivered_customer_date TIMESTAMP,
  order_estimated_delivery_date TIMESTAMP
) USING iceberg;

CREATE EXTERNAL TABLE brazil_e_commerce.olist_products (
  product_id                    STRING,
  product_category_name         STRING,
  product_description_lenght    INT,
  product_name_lenght           INT,
  product_photos_qty            INT,
  product_weight_g              INT,
  product_length_cm             INT,
  product_height_cm             INT,
  product_width_cm              INT
) USING iceberg;

CREATE EXTERNAL TABLE brazil_e_commerce.olist_sellers (
  seller_id                 STRING,
  seller_zip_code_prefix    STRING,
  seller_city               STRING,
  seller_state              STRING
) USING iceberg;

CREATE EXTERNAL TABLE brazil_e_commerce.product_category_name_translation (
  product_category_name         STRING,
  product_category_name_english STRING
) USING iceberg;

INSERT INTO brazil_e_commerce.olist_customers
SELECT customer_unique_id, customer_zip_code_prefix, customer_city, customer_state
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY customer_unique_id ORDER BY customer_id) as row_num
    FROM parquet.`/parquet_data/olist_customers_dataset.parquet`
) AS filtered_data
WHERE row_num = 1;


INSERT INTO brazil_e_commerce.olist_geolocation 
SELECT * FROM parquet.`/parquet_data/olist_geolocation_dataset.parquet`;

INSERT INTO brazil_e_commerce.olist_order_items 
SELECT order_id || '-' || order_item_id as unique_item_id,
       order_id, 
       order_item_id,
       product_id,
       seller_id,
       CAST(shipping_limit_date AS TIMESTAMP), 
       price, 
       freight_value 
FROM parquet.`/parquet_data/olist_order_items_dataset.parquet`;

INSERT INTO brazil_e_commerce.olist_order_payments 
SELECT order_id || '-' || payment_sequential as payment_id, * 
FROM parquet.`/parquet_data/olist_order_payments_dataset.parquet`;

INSERT INTO brazil_e_commerce.olist_order_reviews 
SELECT review_id, 
       order_id,
       review_score,
       review_comment_title,
       review_comment_message,
       CAST(review_creation_date AS TIMESTAMP), 
       CAST(review_answer_timestamp AS TIMESTAMP)
FROM parquet.`/parquet_data/olist_order_reviews_dataset.parquet`;

INSERT INTO brazil_e_commerce.olist_orders 
SELECT a.order_id, 
       b.customer_unique_id,
       a.order_status,
       CAST(a.order_purchase_timestamp AS TIMESTAMP), 
       CAST(a.order_approved_at AS TIMESTAMP),
       CAST(a.order_delivered_carrier_date AS TIMESTAMP), 
       CAST(a.order_delivered_customer_date AS TIMESTAMP), 
       CAST(a.order_estimated_delivery_date AS TIMESTAMP)
FROM parquet.`/parquet_data/olist_orders_dataset.parquet` a
JOIN parquet.`/parquet_data/olist_customers_dataset.parquet` b
ON a.customer_id = b.customer_id;

INSERT INTO brazil_e_commerce.olist_products 
SELECT * FROM parquet.`/parquet_data/olist_products_dataset.parquet`;

INSERT INTO brazil_e_commerce.olist_sellers 
SELECT * FROM parquet.`/parquet_data/olist_sellers_dataset.parquet`;

INSERT INTO brazil_e_commerce.product_category_name_translation 
SELECT * FROM parquet.`/parquet_data/product_category_name_translation.parquet`;

```
- Exit the Spark-SQL shell:
```sql
quit;
```

## Modeling the Graph
1. Log into the PuppyGraph Web UI at http://localhost:8081 with the following credentials:
- Username: `puppygraph`
- Password: `puppygraph123`

2. Upload the schema:
- Select the file `schema.json` in the Upload Graph Schema JSON section and click on Upload.


## Querying the Graph

- Navigate to the Query panel on the left side. The **Graph Query** tab offers an interactive environment for querying the graph using Gremlin and openCypher.

Example Queries:
1. City Sales Ranking (Top 10):
```gremlin
g.V().hasLabel('Order')
  .out('OrderToSeller').hasLabel('Seller')
  .map{ it.get().value('seller_city') + ", " + it.get().value('seller_state') }
  .groupCount()
  .order(local).by(values, desc)
  .unfold()
  .limit(10)
  .project('location', 'count')
    .by(keys)
    .by(values)
```

2. Product Category Sales Ranking (Top 10):
```gremlin
g.E().hasLabel('OrderToProduct')
  .inV().hasLabel('Product').has('product_category_name')
  .groupCount().by('product_category_name')
  .order(local).by(values, desc)
  .unfold()
  .limit(10)
  .project('category', 'count')
    .by(keys)
    .by(values)
```

3. Seller Sales Ranking in 2017:
```gremlin
g.V().hasLabel('Order').has('purchase_timestamp', between('2017-01-01', '2018-01-01'))
  .outE('OrderToSeller')
  .group().by('seller_id')
    .by(values('price').sum())
  .order(local).by(values, desc)
  .unfold()
  .project('seller_id', 'total_sales')
    .by(keys)
    .by(values)
```

4. Product Sales Volume Ranking (by São Paulo's Customers):
```gremlin
g.V().hasLabel('Customer').has('customer_city', 'sao paulo')
  .out('CusToOrder')
  .out('OrderToProduct')
  .groupCount().by(id)
  .order(local).by(values, desc)
  .unfold()
  .project('product_id', 'sales_count')
    .by(keys)
    .by(values)
```

5. Seller Rating Ranking:
```gremlin
g.V().hasLabel('Seller')
  .as('seller')
  .in('OrderToSeller')
  .in('ReviewToOrder')
  .has('review_score')
  .group()
    .by(select('seller'))
    .by(__.values('review_score').mean().coalesce(__.identity(), __.constant(0)))
  .unfold()
  .project('seller', 'reviews')
    .by(select(keys))
    .by(select(values))
  .order()
    .by('reviews', desc)
  .limit(10)
```

## Cleanup and Teardown
- To stop and remove the containers, networks, and volumes, run:
```bash
sudo docker compose down --volumes --remove-orphans
```
