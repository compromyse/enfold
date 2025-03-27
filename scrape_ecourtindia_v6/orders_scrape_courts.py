import csv
from time import sleep
from modules.scraper_orders import ScraperOrders
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class ThreadSafeCSVWriter:
    def __init__(self, filename):
        self.file = open(filename, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.lock = threading.Lock()

    def writerow(self, row):
        with self.lock:
            self.writer.writerow(row)
            print(f'Wrote: {row}')

    def close(self):
        self.file.close()

def scrape_district(state, district, csv_writer):
    try:
        config = {}
        scraper = ScraperOrders(config)
        scraper.close_modal()
        
        scraper.select('sess_state_code', state)
        scraper.select('sess_dist_code', district)

        complexes = scraper.scrape_complexes()
        scraper.select('court_complex_code', complexes[0])

        sleep(2)
        scraper.goto_courtnumber()

        for cmplx in complexes:
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
            
            scraper.select('court_complex_code', cmplx)
            sleep(0.5)

            court_numbers = scraper.get_court_numbers()
            for court_number in court_numbers:
                row = [state, district, cmplx, court_number]
                csv_writer.writerow(row)
        
        scraper.driver.quit()
    
    except Exception as e:
        print(f"Error scraping district {district}: {e}")

def scrape_courts():
    state = 'Uttar Pradesh'
    
    config = {}
    scraper = ScraperOrders(config)
    scraper.close_modal()
    scraper.select('sess_state_code', state)
    
    districts = scraper.scrape_districts()
    scraper.driver.quit()
    
    csv_writer = ThreadSafeCSVWriter('csv/court_numbers.csv')
    csv_writer.writerow(['State', 'District', 'Cmplx', 'Court number'])
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(scrape_district, state, district, csv_writer) 
            for district in districts
        ]
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"A thread encountered an error: {e}")
    
    csv_writer.close()

def scrape_orders(courts):
    csvfile = open(courts, newline='')
    reader = csv.reader(csvfile)

    for row in reader:
        print(row)
        config = {}
        scraper = ScraperOrders(config)
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

        break

    csvfile.close()

if __name__ == '__main__':
    scrape_orders('csv/2023-24_pocso.csv')
