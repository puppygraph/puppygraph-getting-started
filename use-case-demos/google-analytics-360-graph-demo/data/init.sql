-- Loads the GA360 sample export and derives the graph tables.
-- MySQL runs this file once, the first time the container starts.
USE journey;

-- One row per hit (page view or event) in the GA360 export.
CREATE TABLE sample_data (
    visitId BIGINT,
    visitNumber INT,
    visitStartTime INT,
    date DATE,
    fullVisitorId VARCHAR(255),
    total_visits INT,
    total_hits INT,
    total_pageviews INT,
    total_bounces INT,
    total_session_quality INT,
    total_revenue BIGINT,
    source VARCHAR(255),
    medium VARCHAR(255),
    campaign VARCHAR(255),
    keyword VARCHAR(255),
    device VARCHAR(50),
    browser VARCHAR(50),
    operatingSystem VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    hit_number INT,
    page_path TEXT,
    page_title TEXT,
    is_entrance VARCHAR(5),
    is_exit VARCHAR(5),
    time INT,
    action_type INT,
    action_step INT,
    transaction_id VARCHAR(255),
    event_category VARCHAR(255),
    event_action VARCHAR(255),
    event_label VARCHAR(255),
    product_names TEXT,
    product_skus TEXT,
    product_categories TEXT
);

LOAD DATA INFILE '/docker-entrypoint-initdb.d/sample_data.csv'
INTO TABLE sample_data
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- A visit is identified by fullVisitorId + visitId: visitId alone is the
-- visit start time and is shared by different visitors.
ALTER TABLE sample_data ADD COLUMN session_id VARCHAR(64);
UPDATE sample_data SET session_id = CONCAT(fullVisitorId, '-', visitId);

-- Page vertices: one row per page path.
CREATE TABLE pages (
    page_path VARCHAR(255) PRIMARY KEY,
    page_title VARCHAR(255),
    hits INT,
    sessions INT,
    avg_seconds_on_page DOUBLE,
    entrance_rate DOUBLE,
    exit_rate DOUBLE
);
INSERT INTO pages
SELECT
    page_path,
    ANY_VALUE(page_title),
    COUNT(*),
    COUNT(DISTINCT session_id),
    ROUND(AVG(next_time - time) / 1000, 1),
    ROUND(SUM(is_entrance = 'true') / COUNT(*), 3),
    ROUND(SUM(is_exit = 'true') / COUNT(*), 3)
FROM (
    SELECT session_id, page_path, page_title, is_entrance, is_exit, time,
           LEAD(time) OVER (PARTITION BY session_id ORDER BY hit_number) AS next_time
    FROM sample_data
) h
GROUP BY page_path;

-- Session vertices: one row per visit. GA360 repeats the visit's revenue
-- (in micros) on every hit, so it is stored here once, in dollars.
CREATE TABLE sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    visitor_id VARCHAR(32),
    visit_number INT,
    device VARCHAR(50),
    browser VARCHAR(50),
    operating_system VARCHAR(50),
    country VARCHAR(100),
    hits INT,
    revenue DOUBLE,
    purchased BOOLEAN
);
INSERT INTO sessions
SELECT
    session_id,
    ANY_VALUE(fullVisitorId),
    ANY_VALUE(visitNumber),
    ANY_VALUE(device),
    ANY_VALUE(browser),
    ANY_VALUE(operatingSystem),
    ANY_VALUE(country),
    COUNT(*),
    ROUND(COALESCE(MAX(total_revenue), 0) / 1000000, 2),
    COALESCE(MAX(total_revenue), 0) > 0
FROM sample_data
GROUP BY session_id;

-- LANDED_ON edges: the first page of each visit.
CREATE TABLE landings (
    session_id VARCHAR(64) PRIMARY KEY,
    page_path VARCHAR(255)
);
INSERT INTO landings
SELECT session_id, page_path
FROM sample_data
WHERE is_entrance = 'true';

-- NEXT edges: one row per move from one page to a different page within a
-- visit. Repeated hits on the same page (refreshes, events) are skipped.
-- step numbers the moves of a visit 1, 2, 3, ... so consecutive moves can be
-- matched with r2.step = r1.step + 1.
CREATE TABLE transitions (
    transition_id VARCHAR(80) PRIMARY KEY,
    session_id VARCHAR(64),
    step INT,
    from_page VARCHAR(255),
    to_page VARCHAR(255)
);
INSERT INTO transitions
SELECT
    CONCAT(session_id, '-', hit_number),
    session_id,
    ROW_NUMBER() OVER (PARTITION BY session_id ORDER BY hit_number),
    from_page,
    page_path
FROM (
    SELECT session_id, hit_number, page_path,
           LAG(page_path) OVER (PARTITION BY session_id ORDER BY hit_number) AS from_page
    FROM sample_data
) h
WHERE from_page IS NOT NULL AND from_page <> page_path;

-- LINKS_TO edges: one row per pair of pages, summing the NEXT moves between
-- them. Used to draw the site's navigation without one line per move.
CREATE TABLE page_links (
    link_id VARCHAR(520) PRIMARY KEY,
    from_page VARCHAR(255),
    to_page VARCHAR(255),
    moves INT,
    sessions INT,
    buyer_sessions INT
);
INSERT INTO page_links
SELECT
    CONCAT(t.from_page, ' -> ', t.to_page),
    t.from_page,
    t.to_page,
    COUNT(*),
    COUNT(DISTINCT t.session_id),
    COUNT(DISTINCT CASE WHEN s.purchased THEN t.session_id END)
FROM transitions t
JOIN sessions s ON s.session_id = t.session_id
GROUP BY t.from_page, t.to_page;

-- Visitor vertices: one row per visitor. HAD_VISIT edges are read from the
-- sessions table (visitor_id -> session_id).
CREATE TABLE visitors (
    visitor_id VARCHAR(32) PRIMARY KEY,
    sessions INT,
    revenue DOUBLE
);
INSERT INTO visitors
SELECT visitor_id, COUNT(*), ROUND(SUM(revenue), 2)
FROM sessions
GROUP BY visitor_id;
