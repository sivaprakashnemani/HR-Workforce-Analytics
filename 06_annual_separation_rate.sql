-- 06_annual_separation_rate
-- SQLite; snapshot date: 2025-12-31.
WITH counts AS (
 SELECT SUM(CASE WHEN hire_date<'2025-01-01' AND (exit_date IS NULL OR exit_date>='2025-01-01') THEN 1 ELSE 0 END) AS opening_headcount,
 SUM(CASE WHEN hire_date<='2025-12-31' AND (exit_date IS NULL OR exit_date>'2025-12-31') THEN 1 ELSE 0 END) AS closing_headcount,
 SUM(CASE WHEN exit_date>='2025-01-01' AND exit_date<'2026-01-01' THEN 1 ELSE 0 END) AS annual_exits
 FROM employees
)
SELECT *,ROUND((opening_headcount+closing_headcount)/2.0,2) AS average_endpoint_headcount,
 ROUND(100.0*annual_exits/NULLIF((opening_headcount+closing_headcount)/2.0,0),2) AS separation_rate_pct
FROM counts;
