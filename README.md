# HR Workforce Analytics with SQL

A small independent portfolio project analyzing workforce composition, base salaries, hiring, employee exits and performance reviews. The dataset contains **200 synthetic employees, six departments and 344 performance reviews**. All records are fictional. Snapshot date: **December 31, 2025**.

## Business questions

1. How many employees are active, and how are they distributed by department?
2. How do annual base salaries differ across departments?
3. Which salary levels rank highest within each department?
4. How do hiring and exits vary across 2025?
5. What is the annual separation rate using the average opening/closing headcount?
6. What do the latest recorded performance reviews show by department?
7. How are tenure, work modes and review-year training hours distributed?

## Start

Read START_HERE.md, open hr_analytics.sqlite in DB Browser for SQLite, then run the ten files in sql/analysis/. This requires no database server. Expected results are included. Python is optional.

## Model

departments has one row per department. employees has one row per employee. performance_reviews has one row per employee review date. departments.department_id links one-to-many to employees.department_id. employees.employee_id links one-to-many to performance_reviews.employee_id.

Skills demonstrated: SELECT, WHERE, CASE, GROUP BY, HAVING exercises, aggregate functions, INNER/LEFT JOIN, CTEs, recursive CTEs, DENSE_RANK, ROW_NUMBER, date calculations, constraints, keys and null handling.

## Definitions

- Employee records include workers employed at any time in the generated history. There are 160 active employees and 40 exits, all exits occurring in 2025. Active means no exit_date in this fixed snapshot.
- exit_date is the first date an employee is no longer employed. Opening headcount is immediately before January 1, 2025 hiring/exits. Closing headcount is at December 31, 2025 end of day. The reconciliation is 182 opening + 18 hires - 40 exits = 160 closing.
- Annual separation rate = 2025 exits / ((opening headcount + closing headcount) / 2). It includes all recorded exit reasons and is not specifically voluntary attrition. The denominator is an endpoint average, not a daily weighted average.
- annual_salary_usd is an annualized base salary recorded for this snapshot or at departure. It is not actual payroll paid during the year and excludes benefits, taxes and bonuses. Summed active salaries are annual base-salary commitments, not total compensation expense.
- Performance ratings are 1–5. Reviews exist only for employees employed on each December 15 review date. The latest-review query takes one review per active employee before averaging, preventing one-to-many duplicates.
- training_hours describes the completed training recorded for that review year. The review-year summary includes eligible review records, not all employees. It does not establish that training caused a higher rating.
- Tenure is an approximate completed-year band computed from days / 365.25 at the snapshot date. Current department, role and work mode are static attributes; no history of transfers or promotions is modeled.

## Files

- hr_analytics.sqlite: populated local database.
- data/: three CSV source tables.
- sql/01_schema.sql: tables, constraints and indexes.
- sql/02_sample_data.sql: complete INSERT statements.
- sql/analysis/: ten individually runnable analyses.
- sql/03_all_analysis.sql: the same ten analyses in one file for convenience.
- expected_results/: results executed against the supplied database.
- run_analysis.py: optional standard-library runner exporting your results.
- build_project.py: reproducible dataset generator, seed 27. Replaces the generated database and source files when run.
- validation.json: completed database and reconciliation checks.
- PRACTICE.md and RESUME.md: exercises, GitHub guidance and resume entry.

## Validation

All ten queries were executed successfully. Database integrity, foreign keys, review dates, employee totals and headcount reconciliation passed. Running schema plus INSERT scripts in a fresh database reproduced all three supplied tables exactly. No desktop GUI execution is claimed.

## Scope

The synthetic data is suitable for learning and demonstrating SQL. It does not represent an employer or support claims about real compensation, employee outcomes or financial savings. Findings describe this generated sample only.

## License

Project code, SQL, documentation and synthetic data are provided under the MIT license in LICENSE. DB Browser is an independently distributed application with its own license.
