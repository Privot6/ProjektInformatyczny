import argparse, copy, csv, hashlib, json, sys
from pathlib import Path
from statistics import mean
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lab4_data import load_data
from scripts.fuzzy_model import FuzzyModel, baseline, load_config
from scripts.lab4_controls import high_pm_cases

def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def run(rows, cfg, output, input_hash):
    model = FuzzyModel(cfg)
    output.mkdir(parents=True, exist_ok=True)
    records, comparison = [], []
    for row in rows:
        perturbed = {**row, 'pm25': row['pm25'] + cfg['perturbation_pm25']}
        for name, evaluate in [('bazowy', lambda r: baseline(r, cfg)), ('rozmyty', model.evaluate)]:
            before, after = evaluate(row), evaluate(perturbed)
            records.append({**row, 'wariant': name, 'score': before['score'], 'label': before['label'],
                            'pm25_perturbed': perturbed['pm25'], 'score_perturbed': after['score'],
                            'label_perturbed': after['label'],
                            'absolute_score_change': abs(after['score'] - before['score']),
                            'label_changed': int(after['label'] != before['label']),
                            'r_bad': before.get('r_bad', ''), 'r_middle': before.get('r_middle', ''),
                            'r_good': before.get('r_good', '')})


    checks = []
    for case, row in high_pm_cases(cfg):
        for name, evaluate in [('bazowy', lambda r: baseline(r, cfg)), ('rozmyty', model.evaluate)]:
            result = evaluate(row)
            checks.append({'case': case, 'wariant': name, **row, **result,
                           'pass_no_train': int(result['label'] != 'TRENUJ')})

    keys = list(dict.fromkeys(k for row in checks for k in row))
    checks = [{key: row.get(key, '') for key in keys} for row in checks]
    for variant in ('bazowy', 'rozmyty'):
        selected = [r for r in records if r['wariant'] == variant]
        changes = [r['absolute_score_change'] for r in selected]
        comparison.append({'wariant': variant, 'n': len(selected),
                           'mean_abs_score_change_points': mean(changes),
                           'min_change_points': min(changes), 'max_change_points': max(changes),
                           'label_changes': sum(r['label_changed'] for r in selected),
                           'no_train_failures': sum(not r['pass_no_train'] for r in checks if r['wariant'] == variant)})
    b, f = comparison
    reduction = 1-f['mean_abs_score_change_points']/b['mean_abs_score_change_points'] if b['mean_abs_score_change_points'] > 0 else None
    decision = {
        'input_sha256': input_hash, 'config': cfg,
        'relative_reduction': reduction,
        'practical_criterion_met': reduction is not None and reduction >= cfg['practical_relative_reduction'] and f['no_train_failures'] == 0,
        'metric_meaning': 'stability only, not recommendation accuracy or health safety',
        'data_kind': 'GIOS measurements and Open-Meteo ERA5 reanalysis', 'randomness': 'none',
    }
    write_csv(output/'observations.csv', records)
    write_csv(output/'comparison.csv', comparison)
    write_csv(output/'control_checks.csv', checks)
    (output/'run.json').write_text(json.dumps(decision, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(output.as_posix(), json.dumps(comparison, ensure_ascii=False))
    return comparison

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=Path('data/processed/aerorun_dane.csv'))
    parser.add_argument('--config', type=Path, default=Path('config/lab4.json'))
    parser.add_argument('--output', type=Path, default=Path('results/lab4'))
    args = parser.parse_args()
    rows = load_data(args.input)
    cfg = load_config(args.config)
    sha = hashlib.sha256(args.input.read_bytes()).hexdigest()
    run(rows, cfg, args.output, sha)
    sensitivity = copy.deepcopy(cfg)
    sensitivity['pm25_scale'] = cfg['sensitivity_pm25_scale']
    run(rows, sensitivity, args.output/'sensitivity', sha)

if __name__ == '__main__':
    main()
