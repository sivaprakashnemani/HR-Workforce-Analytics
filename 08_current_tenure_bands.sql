-- 08_current_tenure_bands
-- SQLite; snapshot date: 2025-12-31.
WITH tenure AS (
 SELECT CAST((julianday('2025-12-31')-julianday(hire_date))/365.25 AS INTEGER) AS completed_years
 FROM employees WHERE exit_date IS NULL
), bands AS (
 SELECT CASE WHEN completed_years<1 THEN 'Under 1 year' WHEN completed_years<3 THEN '1-2 years'
 WHEN completed_years<5 THEN '3-4 years' ELSE '5+ years' END AS tenure_band,
 CASE WHEN completed_years<1 THEN 1 WHEN completed_years<3 THEN 2 WHEN completed_years<5 THEN 3 ELSE 4 END AS sort_order FROM tenure
)
SELECT tenure_band,COUNT(*) AS active_employees FROM bands GROUP BY tenure_band,sort_order ORDER BY sort_order;
