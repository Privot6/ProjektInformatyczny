import argparse, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lab4_data import load_data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=Path('data/processed/aerorun_dane.csv'))
    parser.add_argument('--output', type=Path, default=Path('results/lab4/input_audit.json'))
    args = parser.parse_args()
    rows = load_data(args.input)
    report = {
        'input': args.input.as_posix(), 'sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(),
        'n': len(rows), 'first': rows[0]['timestamp'], 'last': rows[-1]['timestamp'],
        'continuous_hourly_utc': True, 'duplicates': 0, 'missing': 0,
        'units': {'pm25': 'ug/m3', 'pm10': 'ug/m3', 'temperature_2m': 'C',
                  'wind_speed_10m': 'km/h', 'precipitation': 'mm/h (hourly accumulation)'},
        'data_kind': 'synthetic (repository Lab 3 fixture)',
        'input_changes': 'none; no sorting, imputation or resampling',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__':
    main()
