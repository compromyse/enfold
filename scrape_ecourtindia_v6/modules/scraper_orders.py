from time import sleep
import tempfile
import uuid
import os

from urllib import request

from bs4 import BeautifulSoup

import cv2
import pytesseract

from selenium.webdriver.common.by import By

from selenium.webdriver.support.select import Select
from .scraper import Scraper

class ScraperOrders(Scraper):
    def __init__(self, db, config):
        Scraper.__init__(self, 'https://services.ecourts.gov.in/ecourtindia_v6/?p=courtorder/index', headless=True)

        self.db = db
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

    def submit_search(self):
        captcha_incomplete = True
        while captcha_incomplete:
            img = self.driver.find_element(By.ID, 'captcha_image')
            temp = tempfile.NamedTemporaryFile(suffix='.png')
            img.screenshot(temp.name)

            img = cv2.imread(temp.name)
            text = pytesseract.image_to_string(img).strip()

            element = self.driver.find_element(By.ID, 'order_no_captcha_code')
            element.send_keys(text)

            self.driver.execute_script('submitCourtNumber()')
            sleep(3)

            if self.driver.find_element(By.CLASS_NAME, 'alert-danger-cust').is_displayed():
                self.close_modal()
                element.clear()
            else:
                captcha_incomplete = False

    def parse_orders_table(self):
        try:
            table_innerhtml = self.driver.find_element(By.ID, 'dispTable').get_attribute('innerHTML')
        except:
            return

        rows = BeautifulSoup(str(table_innerhtml), 'html.parser').find_all('td')
        self.rows = []
        i = 6
        while i < len(rows):
            self.rows.append([ rows[i], rows[i-1].text, rows[i-2].text, rows[i-3].text ])
            i += 5

    def handle_orders(self, court_name):
        for row in self.rows:
            order = row[0]

            script = order.find_all('a')[0].get_attribute_list('onclick')[0]
            self.driver.execute_script(script)

            sleep(0.7)
            obj = self.driver.find_elements(By.TAG_NAME, 'object')[-1]
            pdf_url = str(obj.get_attribute('data'))

            while True:
                filename = f"pdf/{uuid.uuid4().hex}.pdf"
                if not os.path.exists(filename):
                    break

            cookies = "; ".join([f"{c['name']}={c['value']}" for c in self.driver.get_cookies()])
            r = request.Request(pdf_url)
            r.add_header("Cookie", cookies)

            try:
                with request.urlopen(r) as response, open(filename, "wb") as file:
                    file.write(response.read())
            except:
                print(f'UNABLE TO FETCH PDF: {pdf_url}')

            record = { 'court_name': court_name, 'case_info': row[3], 'petitioner_respondent': row[2], 'date': row[1], 'filename': filename }
            self.db.insert(record)

            self.driver.find_element(By.ID, 'modalOders').find_element(By.CLASS_NAME, 'btn-close').click()
