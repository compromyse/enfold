from time import sleep

from selenium.webdriver.common.by import By

from selenium.webdriver.support.select import Select
from tinydb import TinyDB

from .scraper import Scraper

class ScraperOrders(Scraper):
    def __init__(self, config):
        Scraper.__init__(self, 'https://services.ecourts.gov.in/ecourtindia_v6/?p=courtorder/index')

        self.db = TinyDB('db.json')
        self.config = config

    def goto_courtnumber(self):
        element = self.driver.find_element(By.ID, 'courtnumber-tabMenu')
        element.click()
        sleep(1)

    def get_court_numbers(self):
        element = self.driver.find_element(By.ID, 'nnjudgecode1')
        select = Select(element)
        options = select.options
        court_numbers = [ option.text for option in options ]
        print(f'COURT NUMBERS: {court_numbers}')

        return court_numbers
