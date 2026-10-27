-- 03_department_salary
-- SQLite; snapshot date: 2025-12-31.
SELECT d.department_name,COUNT(*) AS active_employees,
 ROUND(AVG(e.annual_salary_usd),2) AS average_salary_usd,
 SUM(e.annual_salary_usd) AS annual_base_salary_commitment_usd
FROM employees e JOIN departments d USING(department_id)
WHERE e.exit_date IS NULL GROUP BY d.department_id,d.department_name
ORDER BY average_salary_usd DESC;
