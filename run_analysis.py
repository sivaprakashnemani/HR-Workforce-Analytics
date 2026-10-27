"""Execute the ten analyses locally and export CSV results. No pip packages needed."""
from pathlib import Path
import sqlite3
import csv

root=Path(__file__).resolve().parent
database=root/'hr_analytics.sqlite'
if not database.is_file():
    raise SystemExit('hr_analytics.sqlite is missing. Extract the full project ZIP first.')
connection=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True)
output=root/'your_results'
output.mkdir(exist_ok=True)
for script in sorted((root/'sql/analysis').glob('*.sql')):
    cursor=connection.execute(script.read_text(encoding='utf-8'))
    rows=cursor.fetchall()
    with (output/(script.stem+'.csv')).open('w',newline='',encoding='utf-8') as file:
        writer=csv.writer(file)
        writer.writerow([column[0] for column in cursor.description])
        writer.writerows(rows)
    print(f'{script.name}: {len(rows)} rows exported')
connection.close()
print('Finished. Open your_results to view the CSV files.')
