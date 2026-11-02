"""Odtworzenie Lab 3 i dwukrotne porównanie Lab 4 w katalogu tymczasowym."""
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lab4_data import load_data
from scripts.prepare_data import prepare

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source = ROOT/'data/processed/aerorun_dane.csv'
    before = sha(source)
    rows = load_data(source)
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        prepare(ROOT/'data/raw/gios_syntetyczne.csv',
                ROOT/'data/raw/open_meteo_syntetyczne.csv', scratch/'lab3')
        regenerated = load_data(scratch/'lab3/aerorun_dane.csv')
        if regenerated != rows:
            raise ValueError('Odtworzenie Lab 3 różni się od istniejącej próbki')
        locations = [scratch/'first', scratch/'second']
        for location in locations:
            subprocess.run([sys.executable, str(ROOT/'scripts/compare_methods.py'),
                            '--input', str(source), '--config', str(ROOT/'config/lab4.json'),
                            '--output', str(location)], cwd=ROOT, check=True, capture_output=True)
        hashes = {}
        for first in sorted(locations[0].rglob('*')):
            if first.is_file():
                relative = first.relative_to(locations[0])
                second = locations[1]/relative
                if first.read_bytes() != second.read_bytes():
                    raise ValueError(f'Niepowtarzalny wynik {relative}')
                hashes[relative.as_posix()] = sha(first)
    if before != sha(source):
        raise ValueError('Plik Lab 3 został zmieniony')
    report = {
        'input_sha256': before, 'lab3_rows_reproduced': len(rows),
        'lab3_semantically_identical': True, 'lab4_byte_identical_runs': 2,
        'output_sha256': hashes, 'input_unchanged': True,
        'raw_sha256': {name: sha(ROOT/'data/raw'/name)
                       for name in ('gios_syntetyczne.csv', 'open_meteo_syntetyczne.csv')},
    }
    target = ROOT/'results/lab4/reproducibility.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('PASS: Lab 3 odtworzony, wyniki Lab 4 identyczne bajtowo, wejście bez zmian.')

if __name__ == '__main__':
    main()
