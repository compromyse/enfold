import re
import shutil
from tinydb import TinyDB

def sanitize_filename(filename):
    filename = re.sub(r'[<>:"/\\|?*()]', '_', filename)
    filename = re.sub(r'_+', '_', filename)
    filename = filename.strip('_ ')
    
    return filename

db = TinyDB('orders.json')
entries = db.all()

for entry in entries:
    date = sanitize_filename(entry['date'])
    case_info = sanitize_filename(entry['case_info'])
    court_name = sanitize_filename(entry['court_name'])
    
    newname = f"named_pdf/{date}---{case_info}---{court_name}.pdf"
    
    try:
        shutil.copyfile(entry['filename'], newname)
    except Exception as e:
        print(f"Error copying {entry['filename']}: {e}")
