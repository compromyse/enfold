from time import sleep
import os
import uuid

from urllib import request

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from bs4 import BeautifulSoup

import cv2
import pytesseract
import tempfile

Karnataka = '3'
Bengaluru = '20'
CMM_Court_Complex = '1030134@2,5,10,11,12,13,14@Y'
Chief_Metropolitan = '10'

ACT = '23'

class Scraper:
    def __init__(self, db):
        self.db = db

        self.driver = Firefox()
        self.driver.get('https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index')

        self.current_view = {}

    def run(self):
        self.close_modal()
        self.goto_acts()
        self.select_act()
        self.parse_table()

    def close_modal(self):
        sleep(2)
        self.driver.execute_script('closeModel({modal_id:"validateError"})')
        sleep(1)

    def select(self, i_d, value):
        element = self.driver.find_element(By.ID, i_d)
        select = Select(element)
        select.select_by_value(value)
        sleep(1)

    def select_act(self):
        self.select('actcode', ACT)
        sleep(1)

        # Disposed only
        self.driver.find_element(By.ID, 'radDAct').click()
        self.submit_search()

    def goto_acts(self):
        self.select('sess_state_code', Karnataka)
        self.select('sess_dist_code', Bengaluru)
        self.select('court_complex_code', CMM_Court_Complex)

        sleep(1)
        self.select('court_est_code', Chief_Metropolitan )
        sleep(1)
        element = self.driver.find_element(By.ID, 'act-tabMenu')
        element.click()
        sleep(1)

    def submit_search(self):
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


    def parse_table(self):
        table_innerhtml = self.driver.find_element(By.ID, 'dispTable').get_attribute('innerHTML')
        rows = BeautifulSoup(str(table_innerhtml), 'html.parser').find_all('td')
        self.views = []
        i = 5
        while i < len(rows):
            self.views.append(rows[i])
            self.current_view = {
                'case_info': rows[i-2].get_text(strip=True),
                'petitioner_respondent': ' Vs '.join(rows[i-1].get_text(strip=True).split('Vs')),
                'htmlfile': '',
                'pdfs': []
            }

            i += 4

    def handle_views(self):
        i = 0
        for view in self.views:
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
            self.driver.find_element(By.ID, 'main_back_act').click()

            i += 1
            if i == 10:
                break


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

            with request.urlopen(r) as response, open(filename, "wb") as file:
                file.write(response.read())

            self.driver.find_element(By.ID, 'modalOders').find_element(By.CLASS_NAME, 'btn-close').click()
