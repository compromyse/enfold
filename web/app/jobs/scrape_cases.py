from app.modules.interface import Interface
from tinydb import TinyDB
from bs4 import BeautifulSoup
import time
import csv

def scrape_cases(name, acts, section, state_code):
    db = TinyDB(f'app/outputs/{name}.json')
    interface = Interface()

    try:
        districts = interface.get_districts(state_code)
    except Exception as e:
        print(f"[ERROR] Failed to scrape districts: {e}")
        districts = []

    for dist_code, dist_name in districts:
        print(f'DISTRICT: {dist_name}')

        try:
            complexes = interface.get_complexes(state_code, dist_code)
        except Exception as e:
            print(f"[ERROR] Failed to scrape complexes for {dist_name}: {e}")
            continue

        for complex_code, complex_name in complexes:
            print(f'COMPLEX: {complex_name}')

            court_establishments = str(complex_code).split(',')
            for i, court_establishment in enumerate(court_establishments, 1):
                print(f'ESTABLISHMENT: {i}/{len(court_establishments)}')

                for act in acts:
                    try:
                        cases = interface.search_by_act(state_code, dist_code, court_establishment, act, section)
                    except Exception as e:
                        print(f"[ERROR] Failed to scrape cases in complex {complex_name}: {e}")
                        continue

                    for j, case in enumerate(cases, 1):
                        print(f'CASE: {j}/{len(cases)}')

                        try:
                            case_no = case['case_no']
                            case_history = interface.case_history(state_code, dist_code, court_establishment, case_no)
                        except Exception as e:
                            print(f"[ERROR] Failed to get history for case {case.get('case_no', 'UNKNOWN')}: {e}")
                            continue

                        try:
                            case_history['case_no'] = case_no
                            case_history['complex_name'] = complex_name
                            db.insert(case_history)

                        except Exception as e:
                            print(f"[ERROR] Failed to parse orders for case {case_no}: {e}")
    
    entries = db.all()

    key_mapping = {
        'case_no': 'Case Number',
        'cino': 'CNR Number',
        'type_name': 'Case Type',

        'reg_no': 'Registration Number',
        'reg_year': 'Registration Year',

        'district_name': 'District',
        'complex_name': 'Complex Name',
        'court_name': 'Court Name',

        'dt_regis': 'Registration Date',
        'date_of_filing': 'Date of Filing',
        'date_of_decision': 'Date of Decision',
        'disp_name': 'Disposition',

        'acts': 'Acts',

        'pet_name': 'Petitioner',
        'pet_adv': 'Petitioner Advocate',
        'petparty_name': 'Petitioner Party Name',

        'res_name': 'Respondent',
        'res_adv': 'Respondent Advocate',
        'resparty_name': 'Respondent Party Name'
    }

    all_acts = []

    for entry in entries:
        soup = BeautifulSoup(entry.get('finalOrder') or '', features="html.parser")
        final_orders = []
        for row in soup.select('table.tbl-result tbody tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                order_date = cells[1].get_text(strip=True)
                link_tag = cells[2].find('a', href=True) if len(cells) > 2 else None
                if link_tag:
                    final_orders.append({'date': order_date, 'link': link_tag['href']})

        soup = BeautifulSoup(entry.get('interimOrder') or '', features="html.parser")
        interim_orders = []
        for row in soup.select('table.tbl-result tbody tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                order_date = cells[1].get_text(strip=True)
                link_tag = cells[2].find('a', href=True) if len(cells) > 2 else None
                if link_tag:
                    interim_orders.append({'date': order_date, 'link': link_tag['href']})

        act_html = entry.get('act', '')
        soup = BeautifulSoup(act_html, 'html.parser')

        acts = []
        for row in soup.select('tbody tr'):
            cells = row.find_all('td')
            if len(cells) == 2:
                act = cells[0].get_text(strip=True)
                section = cells[1].get_text(strip=True)
                if act not in all_acts:
                    all_acts.append(act)

                acts.append(f"{act}: {section}")

        entry['acts'] = '\n'.join(acts)
        entry['final_orders'] = final_orders
        entry['interim_orders'] = interim_orders

    max_final = max(len(entry.get('final_orders', [])) for entry in entries)
    max_interim = max(len(entry.get('interim_orders', [])) for entry in entries)

    with open(f'app/outputs/{name}.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        headers = list(key_mapping.values())

        headers += [f'Final Order {i+1}' for i in range(max_final)]
        headers += [f'Interim Order {i+1}' for i in range(max_interim)]
        writer.writerow(headers)

        for entry in entries:
            row = []
            for key in key_mapping:
                row.append(entry.get(key, ''))

            final_orders = entry.get('final_orders', [])
            for order in final_orders:
                hyperlink = f'=HYPERLINK("{order["link"]}", "{order["date"]}")'
                row.append(hyperlink)
            row += [''] * (max_final - len(final_orders))

            interim_orders = entry.get('interim_orders', [])
            for order in interim_orders:
                hyperlink = f'=HYPERLINK("{order["link"]}", "{order["date"]}")'
                row.append(hyperlink)
            row += [''] * (max_interim - len(interim_orders))

            writer.writerow(row)
