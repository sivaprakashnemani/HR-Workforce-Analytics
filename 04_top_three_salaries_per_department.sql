-- 04_top_three_salaries_per_department
-- SQLite; snapshot date: 2025-12-31.
WITH ranked AS (
 SELECT d.department_name,e.employee_id,e.employee_name,e.annual_salary_usd,
 DENSE_RANK() OVER(PARTITION BY e.department_id ORDER BY e.annual_salary_usd DESC) AS salary_rank
 FROM employees e JOIN departments d USING(department_id) WHERE e.exit_date IS NULL
)
SELECT * FROM ranked WHERE salary_rank<=3 ORDER BY department_name,salary_rank,employee_id;
