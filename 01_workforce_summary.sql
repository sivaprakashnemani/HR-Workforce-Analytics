-- 01_workforce_summary
-- SQLite; snapshot date: 2025-12-31.
SELECT COUNT(*) AS recorded_employees,
 SUM(CASE WHEN exit_date IS NULL THEN 1 ELSE 0 END) AS active_employees,
 SUM(CASE WHEN exit_date IS NOT NULL THEN 1 ELSE 0 END) AS exited_employees,
 ROUND(AVG(CASE WHEN exit_date IS NULL THEN annual_salary_usd END),2) AS active_average_salary_usd
FROM employees;
