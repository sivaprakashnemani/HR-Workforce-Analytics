-- 10_review_training_summary
-- SQLite; snapshot date: 2025-12-31.
SELECT substr(review_date,1,4) AS review_year,COUNT(*) AS review_records,
 ROUND(AVG(rating),2) AS average_rating,ROUND(AVG(training_hours),2) AS average_training_hours,
 SUM(training_hours) AS total_training_hours
FROM performance_reviews GROUP BY substr(review_date,1,4) ORDER BY review_year;
