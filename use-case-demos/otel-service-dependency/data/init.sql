-- Runs once when the postgres container is first created.
-- Loads the service-level dependency CSVs from this directory.
CREATE TABLE services (
    service TEXT PRIMARY KEY
);

CREATE TABLE service_edges (
    src_service    TEXT NOT NULL,
    dst_service    TEXT NOT NULL,
    call_count     INT,
    avg_latency_ms DOUBLE PRECISION,
    PRIMARY KEY (src_service, dst_service)
);

COPY services FROM '/docker-entrypoint-initdb.d/services.csv' CSV HEADER;
COPY service_edges FROM '/docker-entrypoint-initdb.d/service_edges.csv' CSV HEADER;
