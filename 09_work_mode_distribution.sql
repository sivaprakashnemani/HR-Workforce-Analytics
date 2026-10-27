-- 09_work_mode_distribution
-- SQLite; snapshot date: 2025-12-31.
SELECT work_mode,COUNT(*) AS active_employees,
 ROUND(100.0*COUNT(*)/NULLIF((SELECT COUNT(*) FROM employees WHERE exit_date IS NULL),0),2) AS active_share_pct
FROM employees WHERE exit_date IS NULL GROUP BY work_mode ORDER BY active_employees DESC;
