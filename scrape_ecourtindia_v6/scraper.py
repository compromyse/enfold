from time import sleep
import os
import uuid

from urllib import request

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select

from bs4 import BeautifulSoup

import cv2
import pytesseract
import tempfile

class Scraper:
    def __init__(self, db, config):
        self.db = db
        self.config = config

        options = Options()
        options.add_argument("--headless")

        self.driver = Firefox(options=options)
        self.driver.get('https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index')

        self.current_view = {}

    def close_modal(self):
        sleep(3)
        self.driver.execute_script('closeModel({modal_id:"validateError"})')
        sleep(1)

    def select(self, i_d, value):
        sleep(1)
        element = self.driver.find_element(By.ID, i_d)
        select = Select(element)
        select.select_by_visible_text(value)
        sleep(1)

    def select_act(self):
        self.select('actcode', self.config['act'])
        sleep(1)

        # Disposed only
        self.driver.find_element(By.ID, 'radDAct').click()
        self.submit_search()

    def scrape_states(self):
        element = self.driver.find_element(By.ID, 'sess_state_code')
        options = Select(element).options
        states = [ option.text for option in options[1:] ]
        print(f'STATES: {states}')

        sleep(0.2)

        return states

    def scrape_districts(self, state):
        self.select('sess_state_code', state)
        sleep(0.2)

        element = self.driver.find_element(By.ID, 'sess_dist_code')
        options = Select(element).options
        districts = [ option.text for option in options[1:] ]
        print(f'DISTRICTS: {districts}')

        return districts

    def scrape_complexes(self, state, district):
        self.select('sess_state_code', state)
        sleep(0.2)
        self.select('sess_dist_code', district)
        sleep(0.2)

        element = self.driver.find_element(By.ID, 'court_complex_code')
        options = Select(element).options
        complexes = [ option.text for option in options[1:] ]
        print(f'COMPLEXES: {complexes}')

        return complexes

    def scrape_establishments(self, state, district, cmplx):
        self.select('sess_state_code', state)
        sleep(0.2)
        self.select('sess_dist_code', district)
        sleep(0.2)
        self.select('court_complex_code', cmplx)
        sleep(1)

        element = self.driver.find_element(By.ID, 'court_est_code')
        options = Select(element).options
        establishments = [ option.text for option in options[1:] ]
        print(f'ESTABLISHMENTS: {establishments}')

        return establishments

    def select_court(self):
        sleep(2)
        while True:
            self.select('sess_state_code', self.config['state'])
            self.select('sess_dist_code', self.config['district'])
            self.select('court_complex_code', self.config['court_complex'])

            sleep(2)
            modal_is_open = self.driver.find_element(By.CLASS_NAME, 'alert-danger-cust').is_displayed()
            if modal_is_open:
                self.close_modal()
                continue

            break

        self.select('court_est_code', self.config['court_establishment'])

    def goto_acts(self):
        element = self.driver.find_element(By.ID, 'act-tabMenu')
        element.click()
        sleep(1)

    def submit_search(self):
        captcha_incomplete = True
        while captcha_incomplete:
            sleep(2)
            img = self.driver.find_element(By.ID, 'captcha_image')
            temp = tempfile.NamedTemporaryFile(suffix='.png')
            img.screenshot(temp.name)

            img = cv2.imread(temp.name)
            text = pytesseract.image_to_string(img).strip()

            element = self.driver.find_element(By.ID, 'act_captcha_code')
            element.send_keys(text)

            self.driver.execute_script('submitAct()')
            sleep(3)

            if self.driver.find_element(By.CLASS_NAME, 'alert-danger-cust').is_displayed():
                self.close_modal()
                element.clear()
            else:
                captcha_incomplete = False

    def handle_table(self):
        table_innerhtml = self.driver.find_element(By.ID, 'dispTable').get_attribute('innerHTML')
        self.rows = BeautifulSoup(str(table_innerhtml), 'html.parser').find_all('td')
        self.views = []
        i = 5
        while i < len(self.rows):
            view = self.rows[i]

            self.current_view = {
                'case_info': self.rows[i-2].get_text(strip=True),
                'petitioner_respondent': ' Vs '.join(self.rows[i-1].get_text(strip=True).split('Vs')),
                'htmlfile': '',
                'pdfs': []
            }

            script = view.find_all('a')[0].get_attribute_list('onclick')[0]
            self.driver.execute_script(script)
            sleep(1)

            html = str(self.driver.find_element(By.ID, 'CSact').get_attribute('innerHTML'))

            while True:
                filename = f"html/{uuid.uuid4().hex}.html"
                if not os.path.exists(filename):
                    break

            self.current_view['htmlfile'] = filename
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)

            self.parse_orders_table()

            self.db.insert(self.current_view)
            print(f'INSERTED: {self.current_view}')
            self.driver.find_element(By.ID, 'main_back_act').click()
            i += 4

    def parse_orders_table(self):
        try:
            table_innerhtml = self.driver.find_element(By.CLASS_NAME, 'order_table').get_attribute('innerHTML')
        except:
            return

        rows = BeautifulSoup(str(table_innerhtml), 'html.parser').find_all('td')
        self.orders = []
        i = 5
        while i < len(rows):
            self.orders.append(rows[i])
            i += 3

        self.handle_orders()

    def handle_orders(self):
        for order in self.orders:
            script = order.find_all('a')[0].get_attribute_list('onclick')[0]
            self.driver.execute_script(script)

            sleep(2)
            obj = self.driver.find_element(By.TAG_NAME, 'object')
            pdf_url = str(obj.get_attribute('data'))

            while True:
                filename = f"pdf/{uuid.uuid4().hex}.pdf"
                if not os.path.exists(filename):
                    break
            self.current_view['pdfs'].append(filename)
            cookies = "; ".join([f"{c['name']}={c['value']}" for c in self.driver.get_cookies()])
            r = request.Request(pdf_url)
            r.add_header("Cookie", cookies)

            try:
                with request.urlopen(r) as response, open(filename, "wb") as file:
                    file.write(response.read())
            except:
                print(f'UNABLE TO FETCH PDF: {pdf_url}')

            self.driver.find_element(By.ID, 'modalOders').find_element(By.CLASS_NAME, 'btn-close').click()
