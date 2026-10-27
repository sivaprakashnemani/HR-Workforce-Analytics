-- 07_latest_review_by_department
-- SQLite; snapshot date: 2025-12-31.
WITH latest AS (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY employee_id ORDER BY review_date DESC,review_id DESC) AS rn
 FROM performance_reviews WHERE review_date<='2025-12-31'
)
SELECT d.department_name,COUNT(e.employee_id) AS active_employees,
 COUNT(l.review_id) AS employees_with_reviews,ROUND(AVG(l.rating),2) AS average_latest_rating
FROM departments d LEFT JOIN employees e ON e.department_id=d.department_id AND e.exit_date IS NULL
LEFT JOIN latest l ON e.employee_id=l.employee_id AND l.rn=1
GROUP BY d.department_id,d.department_name ORDER BY d.department_name;
