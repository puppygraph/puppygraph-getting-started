CREATE SCHEMA supply;

CREATE TABLE supply.customers (
    id bigint,
    customername character varying(64),
    city character varying(64),
    state character varying(64),
    location_id bigint
);

CREATE TABLE supply.distance (
    id bigint,
    from_loc_id bigint,
    to_loc_id bigint,
    distance double precision
);

CREATE TABLE supply.factory (
    id bigint,
    factoryname character varying(64),
    locationid bigint
);

CREATE TABLE supply.inventory (
    id bigint,
    productid bigint,
    locationid bigint,
    quantity integer,
    lastupdated timestamp without time zone,
    status character varying(20)
);

CREATE TABLE supply.locations (
    id bigint,
    address character varying(256),
    city character varying(64),
    country character varying(64),
    lat double precision,
    lng double precision
);
    
CREATE TABLE supply.materialfactory (
    id bigint,
    material_id bigint,
    factory_id bigint
);
    
CREATE TABLE supply.materialinventory (
    id bigint,
    materialid bigint,
    locationid bigint,
    quantity bigint,
    lastupdated timestamp without time zone,
    status character varying(20)
);

CREATE TABLE supply.materialorders (
    id bigint,
    materialid bigint,
    factoryid bigint,
    quantity bigint,
    orderdate timestamp without time zone,
    expectedarrivaldate timestamp without time zone,
    status character varying(32)
);

CREATE TABLE supply.materials (
    id bigint,
    materialname character varying(64)
);

CREATE TABLE supply.productcomposition (
    id bigint,
    productid bigint,
    materialid bigint,
    quantity bigint
);

CREATE TABLE supply.products (
    id bigint,
    productname character varying(64),
    price double precision
);

CREATE TABLE supply.productsales (
    id bigint,
    productid bigint,
    customerid bigint,
    quantity bigint,
    saledate timestamp without time zone,
    totalprice double precision
);

CREATE TABLE supply.productshipment (
    id bigint,
    productid bigint,
    fromlocationid bigint,
    tolocationid bigint,
    quantity bigint,
    shipmentdate timestamp without time zone,
    expectedarrivaldate timestamp without time zone,
    status character varying(32)
);

COPY supply.customers FROM '/csv_data/customers.csv' DELIMITER ',' CSV HEADER;
COPY supply.distance FROM '/csv_data/distance.csv' DELIMITER ',' CSV HEADER;
COPY supply.factory FROM '/csv_data/factory.csv' DELIMITER ',' CSV HEADER;
COPY supply.inventory FROM '/csv_data/inventory.csv' DELIMITER ',' CSV HEADER;
COPY supply.locations FROM '/csv_data/locations.csv' DELIMITER ',' CSV HEADER;
COPY supply.materialfactory FROM '/csv_data/materialfactory.csv' DELIMITER ',' CSV HEADER;
COPY supply.materialinventory FROM '/csv_data/materialinventory.csv' DELIMITER ',' CSV HEADER;
COPY supply.materialorders FROM '/csv_data/materialorders.csv' DELIMITER ',' CSV HEADER;
COPY supply.materials FROM '/csv_data/materials.csv' DELIMITER ',' CSV HEADER;
COPY supply.productcomposition FROM '/csv_data/productcomposition.csv' DELIMITER ',' CSV HEADER;
COPY supply.products FROM '/csv_data/products.csv' DELIMITER ',' CSV HEADER;
COPY supply.productsales FROM '/csv_data/productsales.csv' DELIMITER ',' CSV HEADER;
COPY supply.productshipment FROM '/csv_data/productshipment.csv' DELIMITER ',' CSV HEADER;
