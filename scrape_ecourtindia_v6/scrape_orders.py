import csv
from time import sleep

from tinydb import TinyDB
from modules.scraper_orders import ScraperOrders
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor, as_completed

import threading

class ThreadSafeDB:
    def __init__(self):
        self.db = TinyDB('orders.json')
        self.lock = threading.Lock()
    
    def insert(self, record):
        with self.lock:
            self.db.insert(record)
            print(f'INSERTED: {record}')

db = ThreadSafeDB()

def scrape_single_court(row):
    try:
        config = {}
        scraper = ScraperOrders(db, config)
        scraper.close_modal()
        
        scraper.select('sess_state_code', row[0])
        scraper.select('sess_dist_code', row[1])
        
        while True:
            sleep(0.5)
            try:
                modal_is_open = scraper.driver.find_element(By.CLASS_NAME, 'modal').is_displayed()
                if modal_is_open:
                    scraper.close_modal()
                    continue
                break
            except:
                break
        
        scraper.select('court_complex_code', row[2])
        sleep(1)
        scraper.goto_courtnumber()
        scraper.select('nnjudgecode1', row[3])
        
        scraper.driver.find_element(By.ID, 'radBoth2').click()
        
        scraper.submit_search()
        scraper.parse_orders_table()
        scraper.handle_orders()
        
        scraper.driver.quit()
    
    except Exception as e:
        print(f"Error processing court {row}: {e}")

def scrape_orders(courts_csv):
    with open(courts_csv, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        courts = list(reader)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(scrape_single_court, court) 
            for court in courts
        ]
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"A thread encountered an error: {e}")
    
if __name__ == '__main__':
    input_file = 'csv/2023-24_pocso.csv'
    scrape_orders(input_file)
