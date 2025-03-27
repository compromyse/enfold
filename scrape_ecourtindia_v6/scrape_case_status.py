import csv
from modules.scraper_case_status import ScraperCaseStatus
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

SCRAPE_ESTABLISHMENTS = True

class ThreadSafeCSVWriter:
    def __init__(self, filename):
        self.file = open(filename, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.lock = threading.Lock()

    def writerow(self, row):
        with self.lock:
            self.writer.writerow(row)

    def close(self):
        self.file.close()

def scrape_state_thread(state, config, csv_writer):
    scraper = ScraperCaseStatus(config)
    scraper.close_modal()
    try:
        scraper.select('sess_state_code', state)
        for district in scraper.scrape_districts():
            scraper.select('sess_dist_code', district)
            for cmplx in scraper.scrape_complexes():
                scraper.select('court_complex_code', cmplx)
                if SCRAPE_ESTABLISHMENTS:
                    establishments = []
                    for establishment in scraper.scrape_establishments():
                        establishments.append(establishment)

                    csv_writer.writerow([ state, district, cmplx ] + establishments)
                else:
                    csv_writer.writerow([ state, district, cmplx ])
    except Exception as e:
        print(f"Error scraping {state}: {e}")
    finally:
        scraper.driver.quit()

def scrape_courts():
    config = {}

    m = ScraperCaseStatus(config)
    m.close_modal()

    csv_writer = ThreadSafeCSVWriter('csv/courts.csv')
    csv_writer.writerow(['State', 'District', 'Complex'])

    states = m.scrape_states()
    m.driver.close()

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(scrape_state_thread, state, config, csv_writer) 
            for state in states
        ]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"A thread encountered an error: {e}")

    csv_writer.close()

def scrape_orders():
    config = {}

    m = ScraperCaseStatus(config)
    m.close_modal()

    config['state'] = input('Select a state: ')
    config['district'] = input('Select a district: ')
    config['court_complex'] = input('Select a court complex: ')
    config['court_establishment'] = input('Select a court establishment: ')
    config['act'] = input('Select an act: ')

    m.select_court()
    m.goto_acts()
    m.select_act()
    m.handle_table()

    m.driver.close()

if __name__ == '__main__':
    scrape_courts()
