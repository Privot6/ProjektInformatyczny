import argparse, csv, hashlib, json
from pathlib import Path
from lab4_air import summarize_pm

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=Path('data/processed/aerorun_dane.csv'))
    parser.add_argument('--output', type=Path, default=Path('results/lab4/input_pm_audit.json'))
    args = parser.parse_args()
    with args.input.open(encoding='utf-8-sig', newline='') as stream:
        report = summarize_pm(list(csv.DictReader(stream)))
    report.update(input=args.input.as_posix(), sha256=hashlib.sha256(args.input.read_bytes()).hexdigest())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__':
    main()
