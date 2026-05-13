CREATE TABLE dependencies (
    id SERIAL PRIMARY KEY,
    package TEXT NOT NULL,
    dependency TEXT NOT NULL
);

CREATE TABLE packages (
    name TEXT PRIMARY KEY,
    weekly_downloads INTEGER,
    last_publish TIMESTAMP
);

CREATE TABLE package_maintained_by (
    id SERIAL PRIMARY KEY,
    package TEXT NOT NULL,
    maintainer TEXT NOT NULL
);

CREATE TABLE maintainers (
    username TEXT PRIMARY KEY,
    email TEXT NOT NULL
);

CREATE TABLE services (
    name TEXT PRIMARY KEY
);

CREATE TABLE service_dependencies (
    id SERIAL PRIMARY KEY,
    service TEXT NOT NULL,
    dependency TEXT NOT NULL
);

CREATE TABLE vulnerabilities (
    id SERIAL PRIMARY KEY,
    package TEXT NOT NULL,
    severity INTEGER NOT NULL
);

COPY dependencies(package, dependency) FROM '/docker-entrypoint-initdb.d/dependencies.csv' DELIMITER ',' CSV HEADER;
COPY packages(name, weekly_downloads, last_publish) FROM '/docker-entrypoint-initdb.d/packages.csv' DELIMITER ',' CSV HEADER;
COPY package_maintained_by(package, maintainer) FROM '/docker-entrypoint-initdb.d/package_maintained_by.csv' DELIMITER ',' CSV HEADER;
COPY maintainers(username, email) FROM '/docker-entrypoint-initdb.d/maintainers.csv' DELIMITER ',' CSV HEADER;
COPY services(name) FROM '/docker-entrypoint-initdb.d/services.csv' DELIMITER ',' CSV HEADER;
COPY service_dependencies(service, dependency) FROM '/docker-entrypoint-initdb.d/service_deps.csv' DELIMITER ',' CSV HEADER;
COPY vulnerabilities(package, severity) FROM '/docker-entrypoint-initdb.d/vulnerabilities.csv' DELIMITER ',' CSV HEADER;