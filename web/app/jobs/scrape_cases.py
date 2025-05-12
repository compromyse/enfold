from app.modules.interface import Interface
from bs4 import BeautifulSoup
import csv

from tinydb import TinyDB

db = TinyDB('app/jobs.json')

def get_districts(interface, state_code):
    try:
        return interface.get_districts(state_code)
    except Exception as e:
        print(f"[ERROR] Failed to scrape districts: {e}")
        return []

def get_complexes(interface, state_code, dist_code, dist_name):
    try:
        return interface.get_complexes(state_code, dist_code)
    except Exception as e:
        print(f"[ERROR] Failed to scrape complexes for {dist_name}: {e}")
        return []

def fetch_cases(interface, state_code, dist_code, court_establishment, act, section, complex_name):
    try:
        return interface.search_by_act(state_code, dist_code, court_establishment, act, section)
    except Exception as e:
        print(f"[ERROR] Failed to scrape cases in complex {complex_name}: {e}")
        return []

def fetch_case_history(interface, state_code, dist_code, court_establishment, case_no):
    try:
        return interface.case_history(state_code, dist_code, court_establishment, case_no)
    except Exception as e:
        print(f"[ERROR] Failed to get history for case {case_no}: {e}")
        return None

def parse_orders(order_html):
    soup = BeautifulSoup(order_html or '', features="html.parser")
    orders = []
    for row in soup.select('table.tbl-result tbody tr'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            order_date = cells[1].get_text(strip=True)
            link_tag = cells[2].find('a', href=True) if len(cells) > 2 else None
            if link_tag:
                orders.append({'date': order_date, 'link': link_tag['href']})
    return orders

def parse_acts(entry, all_acts):
    soup = BeautifulSoup(entry.get('act', ''), 'html.parser')
    acts = []
    for row in soup.select('tbody tr'):
        cells = row.find_all('td')
        if len(cells) == 2:
            act = cells[0].get_text(strip=True)
            section = cells[1].get_text(strip=True)
            if act not in all_acts:
                all_acts.append(act)
            acts.append(f"{act}: {section}")
    return '\n'.join(acts)

def write_to_csv(entries, key_mapping, name):
    max_final = max(len(entry.get('final_orders', [])) for entry in entries)
    max_interim = max(len(entry.get('interim_orders', [])) for entry in entries)

    with open(f'app/outputs/{name}.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        headers = list(key_mapping.values()) + \
                  [f'Final Order {i+1}' for i in range(max_final)] + \
                  [f'Interim Order {i+1}' for i in range(max_interim)]
        writer.writerow(headers)

        for entry in entries:
            row = [entry.get(key, '') for key in key_mapping]

            for order in entry.get('final_orders', []):
                row.append(f'=HYPERLINK("{order["link"]}", "{order["date"]}")')
            row += [''] * (max_final - len(entry.get('final_orders', [])))

            for order in entry.get('interim_orders', []):
                row.append(f'=HYPERLINK("{order["link"]}", "{order["date"]}")')
            row += [''] * (max_interim - len(entry.get('interim_orders', [])))

            writer.writerow(row)

def scrape_cases(name, acts, sections, state_code):
    acts = set(acts)
    entries = []
    interface = Interface()

    districts = get_districts(interface, state_code)
    for dist_code, dist_name in districts:
        print(f'DISTRICT: {dist_name}')
        complexes = get_complexes(interface, state_code, dist_code, dist_name)

        for complex_code, complex_name in complexes:
            print(f'COMPLEX: {complex_name}')
            court_establishments = str(complex_code).split(',')

            for i, court_establishment in enumerate(court_establishments, 1):
                print(f'ESTABLISHMENT: {i}/{len(court_establishments)}')

                for act in acts:
                    for section in sections:
                        cases = fetch_cases(interface, state_code, dist_code, court_establishment, act, section, complex_name)

                        for j, case in enumerate(cases, 1):
                            print(f'CASE: {j}/{len(cases)}')
                            case_no = case.get('case_no')
                            if not case_no:
                                continue

                            case_history = fetch_case_history(interface, state_code, dist_code, court_establishment, case_no)
                            if not case_history:
                                continue

                            case_history['case_no'] = case_no
                            case_history['complex_name'] = complex_name
                            entries.append(case_history)

    key_mapping = {
        'case_no': 'Case Number', 'cino': 'CNR Number', 'type_name': 'Case Type',
        'reg_no': 'Registration Number', 'reg_year': 'Registration Year',
        'district_name': 'District', 'complex_name': 'Complex Name', 'court_name': 'Court Name',
        'dt_regis': 'Registration Date', 'date_of_filing': 'Date of Filing', 'date_of_decision': 'Date of Decision',
        'disp_name': 'Disposition', 'acts': 'Acts',
        'pet_name': 'Petitioner', 'pet_adv': 'Petitioner Advocate', 'petparty_name': 'Petitioner Party Name',
        'res_name': 'Respondent', 'res_adv': 'Respondent Advocate', 'resparty_name': 'Respondent Party Name'
    }

    all_acts = []
    for entry in entries:
        entry['final_orders'] = parse_orders(entry.get('finalOrder'))
        entry['interim_orders'] = parse_orders(entry.get('interimOrder'))
        entry['acts'] = parse_acts(entry, all_acts)

    write_to_csv(entries, key_mapping, name)

    db.insert({
        "name": name
    })
