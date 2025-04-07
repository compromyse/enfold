from time import sleep
import os
import uuid

from urllib import request

from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import cv2
import pytesseract
import tempfile

from .scraper import Scraper

class ScraperCaseStatus(Scraper):
    def __init__(self):
        Scraper.__init__(self, 'https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index', headless=False)

    def select_act(self, act):
        try:
            self.select('actcode', act)
        except Exception as e:
            print('EXCEPTION HANDLED:')
            print(e)
        sleep(1)

        # Disposed only
        self.driver.find_element(By.ID, 'radDAct').click()
        self.submit_search()

    def goto_acts(self):
        while True:
            try:
                self.close_modal()
                element = self.driver.find_element(By.ID, 'act-tabMenu')
                element.click()
                break
            except:
                pass

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

    def handle_table(self, db):
        try:
            table_innerhtml = self.driver.find_element(By.ID, 'dispTable').get_attribute('innerHTML')
        except:
            return

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

            db.insert(self.current_view)
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

            sleep(1)
            obj = self.driver.find_element(By.TAG_NAME, 'object')
            if self.driver.find_element(By.ID, 'validateError').is_displayed():
                self.close_modal()
                return

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

            sleep(1)
            while True:
                try:
                    self.driver.find_element(By.ID, 'modalOders').find_element(By.CLASS_NAME, 'btn-close').click()
                    break
                except:
                    pass
