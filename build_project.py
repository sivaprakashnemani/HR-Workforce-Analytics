"""Rebuild this synthetic HR project using Python 3 standard library only."""
from pathlib import Path
import random, datetime, sqlite3, csv, json, io

P=Path(__file__).resolve().parent
def write(path,text):
    f=P/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(text,encoding='utf-8')
r=random.Random(27)
departments=[(1,'Human Resources'),(2,'Finance'),(3,'Information Technology'),(4,'Sales'),(5,'Operations'),(6,'Marketing')]
employees=[];reviews=[]
leavers=set(r.sample(range(1,201),40))
for i in range(1,201):
    dep=r.randint(1,6);hire=datetime.date(2018,1,1)+datetime.timedelta(days=r.randrange(2800))
    hire=min(hire,datetime.date(2025,9,1))
    exit_date=max(datetime.date(2025,1,1),hire)+datetime.timedelta(days=r.randrange((datetime.date(2025,12,30)-max(datetime.date(2025,1,1),hire)).days+1)) if i in leavers else None
    employees.append((i,f'Employee {i:03d}',dep,r.choice(['Analyst','Specialist','Coordinator','Manager']),hire.isoformat(),exit_date.isoformat() if exit_date else None,r.randrange(45,131)*1000,r.choice(['Remote','Hybrid','On-site'])))
    for year in (2024,2025):
        rd=datetime.date(year,12,15)
        if hire<=rd and (exit_date is None or exit_date>rd):
            reviews.append((len(reviews)+1,i,rd.isoformat(),r.choices([1,2,3,4,5],[2,10,42,35,11])[0],r.randrange(5,61)))
schema='''PRAGMA foreign_keys=ON;
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
'''
write('sql/01_schema.sql',schema)
db=P/'hr_analytics.sqlite';db.unlink(missing_ok=True);con=sqlite3.connect(db);con.executescript(schema)
seed=[]
for t,rows in [('departments',departments),('employees',employees),('performance_reviews',reviews)]:
    con.executemany(f'INSERT INTO {t} VALUES ({",".join("?" for _ in rows[0])})',rows)
    for row in rows:
        vals=','.join('NULL' if x is None else str(x) if isinstance(x,int) else "'"+x.replace("'","''")+"'" for x in row)
        seed.append(f'INSERT INTO {t} VALUES ({vals});')
    cols=[d[1] for d in con.execute(f'PRAGMA table_info({t})')]
    out=io.StringIO();w=csv.writer(out);w.writerow(cols);w.writerows(rows);write(f'data/{t}.csv',out.getvalue())
write('sql/02_sample_data.sql','-- Synthetic data, seed 27. Run only against the empty schema.\nBEGIN;\n'+'\n'.join(seed)+'\nCOMMIT;\n')
queries={
'01_workforce_summary':'''SELECT COUNT(*) AS recorded_employees,
 SUM(CASE WHEN exit_date IS NULL THEN 1 ELSE 0 END) AS active_employees,
 SUM(CASE WHEN exit_date IS NOT NULL THEN 1 ELSE 0 END) AS exited_employees,
 ROUND(AVG(CASE WHEN exit_date IS NULL THEN annual_salary_usd END),2) AS active_average_salary_usd
FROM employees''',
'02_department_headcount':'''SELECT d.department_name,COUNT(e.employee_id) AS active_employees
FROM departments d LEFT JOIN employees e
 ON d.department_id=e.department_id AND e.exit_date IS NULL
GROUP BY d.department_id,d.department_name ORDER BY active_employees DESC,d.department_name''',
'03_department_salary':'''SELECT d.department_name,COUNT(*) AS active_employees,
 ROUND(AVG(e.annual_salary_usd),2) AS average_salary_usd,
 SUM(e.annual_salary_usd) AS annual_base_salary_commitment_usd
FROM employees e JOIN departments d USING(department_id)
WHERE e.exit_date IS NULL GROUP BY d.department_id,d.department_name
ORDER BY average_salary_usd DESC''',
'04_top_three_salaries_per_department':'''WITH ranked AS (
 SELECT d.department_name,e.employee_id,e.employee_name,e.annual_salary_usd,
 DENSE_RANK() OVER(PARTITION BY e.department_id ORDER BY e.annual_salary_usd DESC) AS salary_rank
 FROM employees e JOIN departments d USING(department_id) WHERE e.exit_date IS NULL
)
SELECT * FROM ranked WHERE salary_rank<=3 ORDER BY department_name,salary_rank,employee_id''',
'05_monthly_hiring_and_exits':'''WITH RECURSIVE months(month) AS (
 SELECT '2025-01-01' UNION ALL SELECT date(month,'+1 month') FROM months WHERE month<'2025-12-01'
)
SELECT substr(m.month,1,7) AS month,
 (SELECT COUNT(*) FROM employees WHERE hire_date>=m.month AND hire_date<date(m.month,'+1 month')) AS hires,
 (SELECT COUNT(*) FROM employees WHERE exit_date>=m.month AND exit_date<date(m.month,'+1 month')) AS exits
FROM months m ORDER BY m.month''',
'06_annual_separation_rate':'''WITH counts AS (
 SELECT SUM(CASE WHEN hire_date<'2025-01-01' AND (exit_date IS NULL OR exit_date>='2025-01-01') THEN 1 ELSE 0 END) AS opening_headcount,
 SUM(CASE WHEN hire_date<='2025-12-31' AND (exit_date IS NULL OR exit_date>'2025-12-31') THEN 1 ELSE 0 END) AS closing_headcount,
 SUM(CASE WHEN exit_date>='2025-01-01' AND exit_date<'2026-01-01' THEN 1 ELSE 0 END) AS annual_exits
 FROM employees
)
SELECT *,ROUND((opening_headcount+closing_headcount)/2.0,2) AS average_endpoint_headcount,
 ROUND(100.0*annual_exits/NULLIF((opening_headcount+closing_headcount)/2.0,0),2) AS separation_rate_pct
FROM counts''',
'07_latest_review_by_department':'''WITH latest AS (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY employee_id ORDER BY review_date DESC,review_id DESC) AS rn
 FROM performance_reviews WHERE review_date<='2025-12-31'
)
SELECT d.department_name,COUNT(e.employee_id) AS active_employees,
 COUNT(l.review_id) AS employees_with_reviews,ROUND(AVG(l.rating),2) AS average_latest_rating
FROM departments d LEFT JOIN employees e ON e.department_id=d.department_id AND e.exit_date IS NULL
LEFT JOIN latest l ON e.employee_id=l.employee_id AND l.rn=1
GROUP BY d.department_id,d.department_name ORDER BY d.department_name''',
'08_current_tenure_bands':'''WITH tenure AS (
 SELECT CAST((julianday('2025-12-31')-julianday(hire_date))/365.25 AS INTEGER) AS completed_years
 FROM employees WHERE exit_date IS NULL
), bands AS (
 SELECT CASE WHEN completed_years<1 THEN 'Under 1 year' WHEN completed_years<3 THEN '1-2 years'
 WHEN completed_years<5 THEN '3-4 years' ELSE '5+ years' END AS tenure_band,
 CASE WHEN completed_years<1 THEN 1 WHEN completed_years<3 THEN 2 WHEN completed_years<5 THEN 3 ELSE 4 END AS sort_order FROM tenure
)
SELECT tenure_band,COUNT(*) AS active_employees FROM bands GROUP BY tenure_band,sort_order ORDER BY sort_order''',
'09_work_mode_distribution':'''SELECT work_mode,COUNT(*) AS active_employees,
 ROUND(100.0*COUNT(*)/NULLIF((SELECT COUNT(*) FROM employees WHERE exit_date IS NULL),0),2) AS active_share_pct
FROM employees WHERE exit_date IS NULL GROUP BY work_mode ORDER BY active_employees DESC''',
'10_review_training_summary':'''SELECT substr(review_date,1,4) AS review_year,COUNT(*) AS review_records,
 ROUND(AVG(rating),2) AS average_rating,ROUND(AVG(training_hours),2) AS average_training_hours,
 SUM(training_hours) AS total_training_hours
FROM performance_reviews GROUP BY substr(review_date,1,4) ORDER BY review_year'''
}
for name,q in queries.items():
    write(f'sql/analysis/{name}.sql','-- '+name+'\n-- SQLite; snapshot date: 2025-12-31.\n'+q+';\n')
    cur=con.execute(q);cols=[c[0] for c in cur.description];rows=cur.fetchall();out=io.StringIO();w=csv.writer(out);w.writerow(cols);w.writerows(rows);write(f'expected_results/{name}.csv',out.getvalue())
write('sql/03_all_analysis.sql','\n\n'.join('-- '+n+'\n'+q+';' for n,q in queries.items()))
checks={
'integrity_ok':con.execute('PRAGMA integrity_check').fetchone()[0]=='ok',
'foreign_keys_valid':not con.execute('PRAGMA foreign_key_check').fetchall(),
'employees_200':con.execute('SELECT COUNT(*) FROM employees').fetchone()[0]==200,
'active_160':con.execute('SELECT COUNT(*) FROM employees WHERE exit_date IS NULL').fetchone()[0]==160,
'exited_40':con.execute('SELECT COUNT(*) FROM employees WHERE exit_date IS NOT NULL').fetchone()[0]==40,
'reviews_within_employment':con.execute('SELECT COUNT(*) FROM performance_reviews r JOIN employees e USING(employee_id) WHERE r.review_date<e.hire_date OR (e.exit_date IS NOT NULL AND r.review_date>=e.exit_date)').fetchone()[0]==0,
'all_ten_analyses_executed':len(queries)==10}
opening,closing=con.execute("SELECT SUM(hire_date<'2025-01-01'),SUM(exit_date IS NULL) FROM employees").fetchone()
hires=con.execute("SELECT COUNT(*) FROM employees WHERE hire_date>='2025-01-01'").fetchone()[0]
checks['headcount_rollforward']=opening+hires-40==closing
assert all(checks.values()),checks
con.commit();con.close()
# Verify all schema + inserts can independently rebuild the exact supplied tables.
other=sqlite3.connect(':memory:');other.executescript(schema);other.executescript((P/'sql/02_sample_data.sql').read_text())
original=sqlite3.connect(db)
for t in ['departments','employees','performance_reviews']:
    assert original.execute(f'SELECT * FROM {t} ORDER BY 1').fetchall()==other.execute(f'SELECT * FROM {t} ORDER BY 1').fetchall()
checks['sql_rebuild_matches_database']=True
write('validation.json',json.dumps(checks,indent=2))
print(json.dumps({'employees':200,'reviews':len(reviews),'opening':opening,'hires_2025':hires,'closing':closing,'checks':checks},indent=2))
