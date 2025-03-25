from scraper import Scraper
from tinydb import TinyDB
import os

db = TinyDB('db.json')

if __name__ == '__main__':
    config = {}

    config['state'] = input('Select a state: ')
    config['district'] = input('Select a district: ')
    config['court_complex'] = input('Select a court complex: ')
    config['court_establishment'] = input('Select a court establishment: ')
    config['act'] = input('Select an act: ')

    m = Scraper(db, config)
    m.run()
    m.driver.close()
