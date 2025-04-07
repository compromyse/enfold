import tinydb
import csv

db = tinydb.TinyDB('db.json')
file = open('ipc.csv', 'r')

reader = csv.reader(file)

header_parsed = False
for row in reader:
    if not header_parsed:
        header_parsed = True
        continue

    record = {
        'section': row[0],
        'section_text': row[1],
        'minimum_punishment': row[2],
        'severity': row[3],
        'comment': row[4]
    }
    db.insert(record)

file.close()
