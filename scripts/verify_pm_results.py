import argparse, csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lab4_data import load_data
from scripts.lab4_controls import high_pm_cases

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def verify(input_path, folder):
    source = {row['timestamp']: row for row in load_data(input_path)}
    report = []
    for scenario in (folder, folder/'sensitivity'):
        run = json.loads((scenario/'run.json').read_text(encoding='utf-8'))
        cfg = run['config']
        observations = read_csv(scenario/'observations.csv')
        keys = {(r['timestamp'], r['wariant']) for r in observations}
        expected = {(stamp, variant) for stamp in source for variant in ('bazowy', 'rozmyty')}
        if len(observations) != len(expected) or keys != expected:
            raise ValueError('Niepełne lub powtórzone przypadki oceny')
        for row in observations:
            original = source[row['timestamp']]
            for key in ('pm25', 'pm10'):
                if float(row[key]) != original[key]:
                    raise ValueError(f'Zmienione wejście {key}')
            if abs(float(row['pm25_perturbed'])-original['pm25']-cfg['perturbation_pm25']) > 1e-10:
                raise ValueError('Niewłaściwa perturbacja PM2.5')
        cases = dict(high_pm_cases(cfg))
        controls = read_csv(scenario/'control_checks.csv')
        if {(r['case'], r['wariant']) for r in controls} != {
            (case, variant) for case in cases for variant in ('bazowy', 'rozmyty')
        } or len(controls) != 4:
            raise ValueError('Niepełne kontrole wysokiego PM')
        for row in controls:
            for key, value in cases[row['case']].items():
                if float(row[key]) != value:
                    raise ValueError('Niezgodne wejścia kontroli')
            if row['label'] == 'TRENUJ' or row['pass_no_train'] != '1':
                raise ValueError('Kontrola wysokiego PM nieprzechodząca')
        report.append({'scenario': scenario.name, 'observations_checked': len(observations),
                       'control_checks': len(controls), 'result': 'PASS'})
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=Path('data/processed/aerorun_dane.csv'))
    parser.add_argument('--results', type=Path, default=Path('results/lab4'))
    args = parser.parse_args()
    report = verify(args.input, args.results)
    (args.results/'pm_results_check.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report))

if __name__ == '__main__':
    main()
