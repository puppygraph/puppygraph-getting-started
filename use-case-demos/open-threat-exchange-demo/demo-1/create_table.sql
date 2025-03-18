CREATE TABLE pulse (
    id VARCHAR PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    tlp TEXT,
    public BOOLEAN NOT NULL,
    adversary TEXT,
    created TIMESTAMP,
    modified TIMESTAMP,
    author_name TEXT,
    revision INTEGER
);

CREATE TABLE indicator (
    id BIGINT PRIMARY KEY,
    indicator TEXT NOT NULL,
    type TEXT NOT NULL,
    created TIMESTAMP,
    expiration TIMESTAMP,
    is_active BOOLEAN,
    role TEXT
);

CREATE TABLE pulse_indicator (
    pulse_id VARCHAR REFERENCES pulse(id) ON DELETE CASCADE,
    indicator_id BIGINT REFERENCES indicator(id) ON DELETE CASCADE,
    PRIMARY KEY (pulse_id, indicator_id)
);

CREATE TABLE tag (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE pulse_tag (
    pulse_id VARCHAR REFERENCES pulse(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tag(id) ON DELETE CASCADE,
    PRIMARY KEY (pulse_id, tag_id)
);

CREATE TABLE country (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE pulse_country (
    pulse_id VARCHAR REFERENCES pulse(id) ON DELETE CASCADE,
    country_id INTEGER REFERENCES country(id) ON DELETE CASCADE,
    PRIMARY KEY (pulse_id, country_id)
);

CREATE TABLE industry (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE pulse_industry (
    pulse_id VARCHAR REFERENCES pulse(id) ON DELETE CASCADE,
    industry_id INTEGER REFERENCES industry(id) ON DELETE CASCADE,
    PRIMARY KEY (pulse_id, industry_id)
);

CREATE TABLE malware (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE pulse_malware (
    pulse_id VARCHAR REFERENCES pulse(id) ON DELETE CASCADE,
    malware_id INTEGER REFERENCES malware(id) ON DELETE CASCADE,
    PRIMARY KEY (pulse_id, malware_id)
);

CREATE TABLE attack (
    id VARCHAR PRIMARY KEY
);

CREATE TABLE pulse_attack (
    pulse_id VARCHAR REFERENCES pulse(id) ON DELETE CASCADE,
    attack_id VARCHAR REFERENCES attack(id) ON DELETE CASCADE,
    PRIMARY KEY (pulse_id, attack_id)
);

CREATE TABLE reference (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL
);

CREATE TABLE pulse_reference (
    pulse_id VARCHAR REFERENCES pulse(id) ON DELETE CASCADE,
    reference_id INTEGER REFERENCES reference(id) ON DELETE CASCADE,
    PRIMARY KEY (pulse_id, reference_id)
);

CREATE TABLE groups (
    id INTEGER PRIMARY KEY
);

CREATE TABLE pulse_groups (
    pulse_id VARCHAR REFERENCES pulse(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES groups(id) ON DELETE CASCADE,
    PRIMARY KEY (pulse_id, group_id)
);
