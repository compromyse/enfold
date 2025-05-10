from modules.interface import Interface
from tinydb import TinyDB
import time

def scrape_cases(act, section, state_code, name=time.time_ns()):
    db = TinyDB(f'{name}.json')
    interface = Interface()

    def get_act_number(acts):
        for act_code, act_name in acts:
            if act_name == act:
                return act_code
        return None
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

                try:
                    acts = interface.get_acts(state_code, dist_code, court_establishment)
                    act_number = get_act_number(acts)
                except Exception as e:
                    print(f"[ERROR] Failed to scrape acts for complex {complex_name}: {e}")
                    continue

                if not act_number:
                    continue

                try:
                    cases = interface.search_by_act(state_code, dist_code, court_establishment, act_number, section)
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
