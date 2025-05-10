import requests

import os

from .encryption import Encryption

BASE_URL = "https://app.ecourts.gov.in/ecourt_mobile_DC"
RETRY_ATTEMPTS = 10
TIMEOUT = 5

class Interface:
    def __init__(self):
        self.token = self.fetch_token()

    def fetch_token(self):
        uid = os.urandom(8).hex() + ':in.gov.ecourts.eCourtsServices'
        payload = Encryption.encrypt({"version": "3.0", "uid": uid})
        r1 = requests.get(f"{BASE_URL}/appReleaseWebService.php", params={'params': payload})
        token = Encryption.decrypt(r1.text)['token']
        token = Encryption.encrypt(token)
        if not token:
            raise Exception

        return token

    def get(self, endpoint, data):
        for _ in range(RETRY_ATTEMPTS):
            try:
                resp = requests.get(
                    f"{BASE_URL}/{endpoint}",
                    params={'params': data},
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=TIMEOUT
                )

                return Encryption.decrypt(resp.text)
            except:
                continue

        raise Exception

    def get_states(self):
        try:
            data = Encryption.encrypt({'action_code': 'fillState'})
            states_list = self.get('stateWebService.php', data)['states']
            return list(map(lambda x: (x['state_code'], x['state_name']), states_list))
        except RuntimeError:
            raise Exception("Failed to scrape states")

    def get_districts(self, state_code):
        try:
            data = Encryption.encrypt({"state_code": str(state_code)})
            districts_list = self.get('districtWebService.php', data)['districts']
            return list(map(lambda x: (x['dist_code'], x['dist_name']), districts_list))
        except RuntimeError:
            raise Exception("Failed to scrape districts")

    def get_complexes(self, state_code, dist_code):
        try:
            data = Encryption.encrypt({
                "action_code": "fillCourtComplex",
                "state_code": str(state_code),
                "dist_code": str(dist_code)
            })
            complexes_list = self.get('courtEstWebService.php', data)['courtComplex']
            if complexes_list is None:
                return []
            return list(map(lambda x: (x['njdg_est_code'], x['court_complex_name']), complexes_list))
        except RuntimeError:
            raise Exception("Failed to scrape court complexes")

    def get_acts(self, state_code, dist_code, complex_code):
        try:
            data = Encryption.encrypt({
                "state_code": str(state_code),
                "dist_code": str(dist_code),
                "court_code": str(complex_code),
                "searchText": "",
                "language_flag": "english",
                "bilingual_flag": "0"
            })
            acts_list = self.get('actWebService.php', data)['actsList'][0]['acts'].split('#')
            return list(map(lambda x: (x.split('~')[0], x.split('~')[1]) if '~' in x else (x, None), acts_list))
        except RuntimeError:
            raise Exception("Failed to scrape acts")

    def search_by_act(self, state_code, dist_code, complex_code, act_number, section=""):
        try:
            data = Encryption.encrypt({
                "state_code": str(state_code),
                "dist_code": str(dist_code),
                "court_code_arr": str(complex_code),
                "language_flag": "english",
                "bilingual_flag": "0",
                "selectActTypeText": str(act_number),
                "underSectionText": section,
                "pendingDisposed": "Disposed"
            })
            cases_list = self.get('searchByActWebService.php', data)
            return cases_list['0']['caseNos']
        except RuntimeError:
            raise Exception("Failed to scrape cases by act")

    def case_history(self, state_code, dist_code, complex_code, case_no):
        try:
            data = Encryption.encrypt({
                "state_code": str(state_code),
                "dist_code": str(dist_code),
                "court_code": str(complex_code),
                "language_flag": "english",
                "bilingual_flag": "0",
                "case_no": case_no
            })
            return self.get('caseHistoryWebService.php', data)['history']
        except RuntimeError:
            raise Exception("Failed to scrape case history")
