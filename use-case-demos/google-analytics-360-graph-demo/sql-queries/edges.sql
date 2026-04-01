INSERT INTO edges (
	visit_id,
    source_node_id,
    target_node_id,
    hit_number,
    edge_count,
    action_type,
    device,
    browser,
    country,
    total_revenue,
    time_stamp
)
SELECT
	visitId as visit_id,
    source_nodes.node_id AS source_node_id,
    target_nodes.node_id AS target_node_id,
    hit_number AS hit_number,
    COUNT(*) AS edge_count,
    'pageview' AS action_type,
    ANY_VALUE(CombinedEdges.device) AS device,
    ANY_VALUE(CombinedEdges.browser) AS browser,
    ANY_VALUE(CombinedEdges.country) AS country,
    SUM(CombinedEdges.total_revenue) AS total_revenue,
    ANY_VALUE(CombinedEdges.time_stamp) AS time_stamp
FROM
    (
        SELECT
        -- regular page transition edges
            fullVisitorId,
            visitId,
            hit_number,
            page_path AS target_page_path,
            LAG(page_path, 1) OVER (
                PARTITION BY fullVisitorId, visitId
                ORDER BY hit_number
            ) AS source_page_path,
            COALESCE(total_revenue, 0)/1000000 AS total_revenue,
            device,
            browser,
            country,
            time AS time_stamp
        FROM
            sample_data
        WHERE
            page_path IS NOT NULL
        UNION ALL
        SELECT
		-- entrance edges
            fullVisitorId,
            visitId,
            hit_number,
            source AS source_page_path,
            page_path AS target_page_path,
            COALESCE(total_revenue, 0)/1000000 AS total_revenue,
            device,
            browser,
            country,
            time AS time_stamp
        FROM
            sample_data
        WHERE
            is_entrance = 'true'
    ) AS CombinedEdges
JOIN
    nodes AS source_nodes ON CombinedEdges.source_page_path = source_nodes.page_path
JOIN
    nodes AS target_nodes ON CombinedEdges.target_page_path = target_nodes.page_path
GROUP BY
	visit_id,
    source_node_id,
    target_node_id,
    hit_number,
    CombinedEdges.device,
    CombinedEdges.browser,
    CombinedEdges.country;
