from tinydb import TinyDB
import csv

db = TinyDB('orders.json')
entries = db.all()

csvfile = open('orders.csv', 'w', newline='')
w = csv.writer(csvfile)
w.writerow(['District', 'Court Name', 'Case Info', 'Petitioner/Respondent', 'Date', 'File'])

for entry in entries:
    ent = [entry['district'], entry['court_name'], entry['case_info'], entry['petitioner_respondent'], entry['date'], f'http://aarch.compromyse.xyz:8000/{entry["filename"]}']
    w.writerow(ent)

csvfile.close()
