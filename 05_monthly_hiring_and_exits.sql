-- 05_monthly_hiring_and_exits
-- SQLite; snapshot date: 2025-12-31.
WITH RECURSIVE months(month) AS (
 SELECT '2025-01-01' UNION ALL SELECT date(month,'+1 month') FROM months WHERE month<'2025-12-01'
)
SELECT substr(m.month,1,7) AS month,
 (SELECT COUNT(*) FROM employees WHERE hire_date>=m.month AND hire_date<date(m.month,'+1 month')) AS hires,
 (SELECT COUNT(*) FROM employees WHERE exit_date>=m.month AND exit_date<date(m.month,'+1 month')) AS exits
FROM months m ORDER BY m.month;
