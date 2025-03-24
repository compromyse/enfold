from scraper import Scraper
from tinydb import TinyDB
import os

db = TinyDB('db.json')

os.makedirs("html", exist_ok=True)
os.makedirs("pdf", exist_ok=True)

if __name__ == '__main__':
    m = Scraper(db)
    m.run()
    m.handle_views()
    m.driver.close()
