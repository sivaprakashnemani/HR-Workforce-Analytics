# Run the HR SQL project on your desktop

Use DB Browser for SQLite for the easiest desktop workflow. The supplied database is already populated. You do not need Python, a database server, a login or an internet connection after downloading the application and project.

1. Extract the entire project ZIP into a regular folder, such as Documents/HR_SQL_Project. Do not open files while they are still inside the ZIP.
2. Download DB Browser for SQLite from https://sqlitebrowser.org/dl/ and install the version appropriate for your computer.
3. Launch DB Browser for SQLite.
4. Click **Open Database**, then select **hr_analytics.sqlite** from the extracted folder.
5. Select **Browse Data**. Choose employees, departments or performance_reviews to inspect the records.
6. Select **Execute SQL**. Paste the query below and run it:

```sql
SELECT COUNT(*) AS total_employees FROM employees;
```

The result should be **200**.

7. Open sql/analysis/01_workforce_summary.sql in a text editor, copy its SQL into Execute SQL and run it. You should see 200 recorded employees, 160 active employees and 40 exits.
8. Continue through the ten numbered files in sql/analysis/. Run one file at a time. Compare results with the matching CSV in expected_results/.
9. After understanding each query, try the exercises in PRACTICE.md. Save your own SQL answers and screenshots for GitHub.

The SQL dialect is SQLite. These files are not written for SQL Server, MySQL or PostgreSQL. A current DB Browser version supports the window functions used in the project.

## Optional: build a fresh database using SQL

Do this only when you want to practice creating tables and loading data. The provided database already contains them.

1. In DB Browser, select New Database and save it under a different filename, such as hr_practice.sqlite.
2. Run all of sql/01_schema.sql against that new, empty database.
3. Run all of sql/02_sample_data.sql once, then choose Write Changes if prompted.
4. Run the numbered analysis files against your new database.

Do not rerun the schema or inserts against the populated database: existing-table or duplicate-key errors are expected. Use the SELECT queries for ordinary practice. Keep the original hr_analytics.sqlite as a clean reference.

## Optional: use Python instead of a desktop GUI

With Python 3 installed, open a terminal in the extracted folder and run:

```text
python run_analysis.py
```

On Windows, `py -3 run_analysis.py` is another option. This uses Python's built-in SQLite module and exports the analysis results to your_results/. No pip installation is needed.

The supplied SQL and database were executed and checked with SQLite here. The desktop GUI itself was not run in this environment.
