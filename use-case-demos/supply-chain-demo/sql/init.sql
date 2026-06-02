-- Create Tables
CREATE TABLE nodes_car_model (
    vertex_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    number INTEGER,
    year INTEGER,
    type VARCHAR(255),
    engine_type VARCHAR(255),
    size VARCHAR(255),
    seats INTEGER
);

CREATE TABLE nodes_feature (
    vertex_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    number VARCHAR(255),
    type VARCHAR(255),
    state VARCHAR(255)
);

CREATE TABLE nodes_part (
    vertex_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    number VARCHAR(255),
    price INTEGER,
    date VARCHAR(255)
);

CREATE TABLE nodes_supplier (
    vertex_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    address VARCHAR(255),
    contact VARCHAR(255),
    phone_number VARCHAR(255) 
);

CREATE TABLE with_feature (
    src_node_id VARCHAR(255),
    dst_node_id VARCHAR(255),
    version FLOAT
);

CREATE TABLE is_composed_of (
    src_id VARCHAR(255),
    dst_id VARCHAR(255),
    version FLOAT
);

CREATE TABLE is_supplied_by (
    src_id VARCHAR(255),
    dst_id VARCHAR(255),
    version FLOAT
);

-- Load Data from the CSV files (mapped to /data inside the container)
COPY nodes_car_model FROM '/data/nodes_car_model.csv' DELIMITER ',' CSV HEADER;
COPY nodes_feature FROM '/data/nodes_feature.csv' DELIMITER ',' CSV HEADER;
COPY nodes_part FROM '/data/nodes_part.csv' DELIMITER ',' CSV HEADER;
COPY nodes_supplier FROM '/data/nodes_supplier.csv' DELIMITER ',' CSV HEADER;
COPY with_feature FROM '/data/with_feature.csv' DELIMITER ',' CSV HEADER;
COPY is_composed_of FROM '/data/is_composed_of.csv' DELIMITER ',' CSV HEADER;
COPY is_supplied_by FROM '/data/is_supplied_by.csv' DELIMITER ',' CSV HEADER;