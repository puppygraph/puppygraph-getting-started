INSERT INTO nodes (
    page_path,
    page_title,
    total_visits,
    avg_time_on_page,
    unique_visitors,
    total_revenue,
    entrance_rate,
    exit_rate
)
SELECT
    subquery.page_path,
    ANY_VALUE(subquery.page_title),
    COUNT(*) AS total_visits,
    AVG(CASE WHEN subquery.next_hit_time IS NOT NULL THEN subquery.next_hit_time - subquery.hit_time_in_session ELSE NULL END) AS avg_time_on_page,
    COUNT(DISTINCT subquery.fullVisitorId) AS unique_visitors,
    SUM(subquery.total_revenue) AS total_revenue,
    SUM(CASE WHEN subquery.is_entrance = 'true' THEN 1 ELSE 0 END) / COUNT(*) AS entrance_rate,
    SUM(CASE WHEN subquery.is_exit = 'true' THEN 1 ELSE 0 END) / COUNT(*) AS exit_rate
FROM (
    SELECT
        fullVisitorId,
        visitId,
        page_path,
        page_title,
        is_entrance,
        is_exit,
        COALESCE(total_revenue, 0)/1000000 AS total_revenue,
        time AS hit_time_in_session,
        LEAD(time, 1) OVER (PARTITION BY fullVisitorId, visitId ORDER BY time) AS next_hit_time
    FROM
        sample_data
) AS subquery
WHERE
    subquery.page_path IS NOT NULL
GROUP BY
    subquery.page_path;
