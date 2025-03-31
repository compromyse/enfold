from time import sleep

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select

class Scraper:
    def __init__(self, base_url, headless=True):
        options = Options()
        if headless:
            options.add_argument("--headless")

        self.driver = Firefox(options=options)
        self.driver.get(base_url)

    def close_modal(self):
        sleep(3)
        self.driver.execute_script('closeModel({modal_id:"validateError"})')
        sleep(1)

    def select(self, i_d, value):
        while True:
            try:
                element = self.driver.find_element(By.ID, i_d)
                break
            except:
                sleep(0.2)
                pass

        select = Select(element)
        select.select_by_visible_text(value)
        sleep(1)

    def scrape_states(self):
        element = self.driver.find_element(By.ID, 'sess_state_code')
        options = Select(element).options
        states = [ option.text for option in options[1:] ]
        print(f'STATES: {states}')

        sleep(0.2)

        return states

    def scrape_districts(self):
        element = self.driver.find_element(By.ID, 'sess_dist_code')
        options = Select(element).options
        districts = [ option.text for option in options[1:] ]
        print(f'DISTRICTS: {districts}')

        return districts

    def scrape_complexes(self):
        element = self.driver.find_element(By.ID, 'court_complex_code')
        options = Select(element).options
        complexes = [ option.text for option in options[1:] ]
        print(f'COMPLEXES: {complexes}')

        return complexes

    def establishments_visible(self):
        return self.driver.find_element(By.ID, 'court_est_code').is_displayed()

    def scrape_establishments(self):
        element = self.driver.find_element(By.ID, 'court_est_code')
        options = Select(element).options
        establishments = [ option.text for option in options[1:] if option.text != '' ]
        print(f'ESTABLISHMENTS: {establishments}')

        return establishments
