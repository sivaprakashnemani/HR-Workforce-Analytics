-- 02_department_headcount
-- SQLite; snapshot date: 2025-12-31.
SELECT d.department_name,COUNT(e.employee_id) AS active_employees
FROM departments d LEFT JOIN employees e
 ON d.department_id=e.department_id AND e.exit_date IS NULL
GROUP BY d.department_id,d.department_name ORDER BY active_employees DESC,d.department_name;
