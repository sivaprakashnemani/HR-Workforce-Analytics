-- 01_workforce_summary
SELECT COUNT(*) AS recorded_employees,
 SUM(CASE WHEN exit_date IS NULL THEN 1 ELSE 0 END) AS active_employees,
 SUM(CASE WHEN exit_date IS NOT NULL THEN 1 ELSE 0 END) AS exited_employees,
 ROUND(AVG(CASE WHEN exit_date IS NULL THEN annual_salary_usd END),2) AS active_average_salary_usd
FROM employees;

-- 02_department_headcount
SELECT d.department_name,COUNT(e.employee_id) AS active_employees
FROM departments d LEFT JOIN employees e
 ON d.department_id=e.department_id AND e.exit_date IS NULL
GROUP BY d.department_id,d.department_name ORDER BY active_employees DESC,d.department_name;

-- 03_department_salary
SELECT d.department_name,COUNT(*) AS active_employees,
 ROUND(AVG(e.annual_salary_usd),2) AS average_salary_usd,
 SUM(e.annual_salary_usd) AS annual_base_salary_commitment_usd
FROM employees e JOIN departments d USING(department_id)
WHERE e.exit_date IS NULL GROUP BY d.department_id,d.department_name
ORDER BY average_salary_usd DESC;

-- 04_top_three_salaries_per_department
WITH ranked AS (
 SELECT d.department_name,e.employee_id,e.employee_name,e.annual_salary_usd,
 DENSE_RANK() OVER(PARTITION BY e.department_id ORDER BY e.annual_salary_usd DESC) AS salary_rank
 FROM employees e JOIN departments d USING(department_id) WHERE e.exit_date IS NULL
)
SELECT * FROM ranked WHERE salary_rank<=3 ORDER BY department_name,salary_rank,employee_id;

-- 05_monthly_hiring_and_exits
WITH RECURSIVE months(month) AS (
 SELECT '2025-01-01' UNION ALL SELECT date(month,'+1 month') FROM months WHERE month<'2025-12-01'
)
SELECT substr(m.month,1,7) AS month,
 (SELECT COUNT(*) FROM employees WHERE hire_date>=m.month AND hire_date<date(m.month,'+1 month')) AS hires,
 (SELECT COUNT(*) FROM employees WHERE exit_date>=m.month AND exit_date<date(m.month,'+1 month')) AS exits
FROM months m ORDER BY m.month;

-- 06_annual_separation_rate
WITH counts AS (
 SELECT SUM(CASE WHEN hire_date<'2025-01-01' AND (exit_date IS NULL OR exit_date>='2025-01-01') THEN 1 ELSE 0 END) AS opening_headcount,
 SUM(CASE WHEN hire_date<='2025-12-31' AND (exit_date IS NULL OR exit_date>'2025-12-31') THEN 1 ELSE 0 END) AS closing_headcount,
 SUM(CASE WHEN exit_date>='2025-01-01' AND exit_date<'2026-01-01' THEN 1 ELSE 0 END) AS annual_exits
 FROM employees
)
SELECT *,ROUND((opening_headcount+closing_headcount)/2.0,2) AS average_endpoint_headcount,
 ROUND(100.0*annual_exits/NULLIF((opening_headcount+closing_headcount)/2.0,0),2) AS separation_rate_pct
FROM counts;

-- 07_latest_review_by_department
WITH latest AS (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY employee_id ORDER BY review_date DESC,review_id DESC) AS rn
 FROM performance_reviews WHERE review_date<='2025-12-31'
)
SELECT d.department_name,COUNT(e.employee_id) AS active_employees,
 COUNT(l.review_id) AS employees_with_reviews,ROUND(AVG(l.rating),2) AS average_latest_rating
FROM departments d LEFT JOIN employees e ON e.department_id=d.department_id AND e.exit_date IS NULL
LEFT JOIN latest l ON e.employee_id=l.employee_id AND l.rn=1
GROUP BY d.department_id,d.department_name ORDER BY d.department_name;

-- 08_current_tenure_bands
WITH tenure AS (
 SELECT CAST((julianday('2025-12-31')-julianday(hire_date))/365.25 AS INTEGER) AS completed_years
 FROM employees WHERE exit_date IS NULL
), bands AS (
 SELECT CASE WHEN completed_years<1 THEN 'Under 1 year' WHEN completed_years<3 THEN '1-2 years'
 WHEN completed_years<5 THEN '3-4 years' ELSE '5+ years' END AS tenure_band,
 CASE WHEN completed_years<1 THEN 1 WHEN completed_years<3 THEN 2 WHEN completed_years<5 THEN 3 ELSE 4 END AS sort_order FROM tenure
)
SELECT tenure_band,COUNT(*) AS active_employees FROM bands GROUP BY tenure_band,sort_order ORDER BY sort_order;

-- 09_work_mode_distribution
SELECT work_mode,COUNT(*) AS active_employees,
 ROUND(100.0*COUNT(*)/NULLIF((SELECT COUNT(*) FROM employees WHERE exit_date IS NULL),0),2) AS active_share_pct
FROM employees WHERE exit_date IS NULL GROUP BY work_mode ORDER BY active_employees DESC;

-- 10_review_training_summary
SELECT substr(review_date,1,4) AS review_year,COUNT(*) AS review_records,
 ROUND(AVG(rating),2) AS average_rating,ROUND(AVG(training_hours),2) AS average_training_hours,
 SUM(training_hours) AS total_training_hours
FROM performance_reviews GROUP BY substr(review_date,1,4) ORDER BY review_year;