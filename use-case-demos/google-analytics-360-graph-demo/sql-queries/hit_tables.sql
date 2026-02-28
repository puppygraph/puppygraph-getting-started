use journey;
drop table if exists edges;
drop table if exists nodes;
CREATE TABLE nodes (
    node_id INT PRIMARY KEY AUTO_INCREMENT,
    page_path VARCHAR(255) NOT NULL UNIQUE,
    page_title TEXT,
    total_visits INTEGER,
    avg_time_on_page INTEGER,
    unique_visitors INTEGER,
    total_revenue DECIMAL(10 , 2 ),
    entrance_rate FLOAT,
    exit_rate FLOAT
);
CREATE TABLE edges (
    hit_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    visit_id INT NOT NULL,
    source_node_id INT NOT NULL,
    target_node_id INT NOT NULL,
    hit_number INT NOT NULL,
    edge_count INT,
    action_type VARCHAR(50),
    device VARCHAR(50),
    browser VARCHAR(50),
    country VARCHAR(50),
    total_revenue DECIMAL(10 , 2 ),
    time_stamp BIGINT,
    FOREIGN KEY (source_node_id)
        REFERENCES nodes (node_id),
    FOREIGN KEY (target_node_id)
        REFERENCES nodes (node_id)
);






