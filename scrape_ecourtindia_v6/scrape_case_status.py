from time import sleep
from modules.scraper_case_status import ScraperCaseStatus
from tinydb import TinyDB

db = TinyDB('db.json')

scraper = ScraperCaseStatus()

state = 'Karnataka'
act = 'Juvenile Justice (Care and Protection of Children) Act, 2015'

scraper.close_modal()
scraper.select('sess_state_code', state)
sleep(1)

for district in scraper.scrape_districts():
    print(f'SELECTING DISTRICT {district}')
    while True:
        try:
            scraper.close_modal()
            scraper.select('sess_dist_code', district)
            break
        except:
            pass
    sleep(1)

    for cmplx in scraper.scrape_complexes():
        sleep(1)
        print(f'SELECTING COMPLEX {cmplx}')
        while True:
            try:
                scraper.close_modal()
                scraper.select('court_complex_code', cmplx)
                break
            except:
                pass
        try:
            scraper.driver.switch_to.alert.accept();
            scraper.close_modal()
        except:
            pass

        for establishment in scraper.scrape_establishments():
            sleep(1)
            print(f'SELECTING ESTABLISHMENT {establishment}')
            while True:
                try:
                    scraper.close_modal()
                    scraper.select('court_est_code', establishment)
                    break
                except Exception as e:
                    print("EXCEPTION HANDLED:")
                    print(e)

            sleep(1)
            scraper.close_modal()

            sleep(1)
            scraper.goto_acts()
            try:
                scraper.select_act(act)
                scraper.handle_table(db)
            except Exception as e:
                    print("EXCEPTION HANDLED:")
                    print(e)

scraper.driver.close()
