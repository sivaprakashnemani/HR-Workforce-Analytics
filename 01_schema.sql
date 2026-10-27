PRAGMA foreign_keys=ON;
CREATE TABLE departments (
 department_id INTEGER PRIMARY KEY,
 department_name TEXT NOT NULL UNIQUE
);
CREATE TABLE employees (
 employee_id INTEGER PRIMARY KEY,
 employee_name TEXT NOT NULL,
 department_id INTEGER NOT NULL REFERENCES departments(department_id),
 job_title TEXT NOT NULL,
 hire_date TEXT NOT NULL CHECK(date(hire_date) IS NOT NULL),
 exit_date TEXT CHECK(exit_date IS NULL OR (date(exit_date) IS NOT NULL AND exit_date>=hire_date)),
 annual_salary_usd INTEGER NOT NULL CHECK(annual_salary_usd>0),
 work_mode TEXT NOT NULL CHECK(work_mode IN ('Remote','Hybrid','On-site'))
);
CREATE TABLE performance_reviews (
 review_id INTEGER PRIMARY KEY,
 employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
 review_date TEXT NOT NULL CHECK(date(review_date) IS NOT NULL),
 rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
 training_hours INTEGER NOT NULL CHECK(training_hours>=0),
 UNIQUE(employee_id,review_date)
);
CREATE INDEX idx_employee_department ON employees(department_id);
CREATE INDEX idx_review_employee_date ON performance_reviews(employee_id,review_date);
