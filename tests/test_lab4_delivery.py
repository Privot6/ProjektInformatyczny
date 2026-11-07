import csv, hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class EndToEnd(unittest.TestCase):
    def test_reproducibility_and_unchanged_input(self):
        source = ROOT/'data/processed/aerorun_dane.csv'
        original = source.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            destinations = [Path(tmp)/'first', Path(tmp)/'second']
            for dest in destinations:
                subprocess.run([sys.executable, str(ROOT/'scripts/compare_methods.py'),
                                '--input', str(source), '--output', str(dest)], check=True, capture_output=True)
                with (dest/'observations.csv').open(encoding='utf-8') as stream:
                    rows = list(csv.DictReader(stream))
                self.assertEqual(len(rows), 144)
                for variant in ('bazowy', 'rozmyty'):
                    self.assertEqual(sum(r['wariant'] == variant for r in rows), 72)
                main = json.loads((dest/'run.json').read_text(encoding='utf-8'))
                sensitive = json.loads((dest/'sensitivity/run.json').read_text(encoding='utf-8'))
                self.assertEqual(main['input_sha256'], hashlib.sha256(original).hexdigest())
                self.assertEqual(main['config']['pm25_scale'], 25)
                self.assertEqual(sensitive['config']['pm25_scale'], 30)
                a, b = dict(main['config']), dict(sensitive['config'])
                a.pop('pm25_scale'); b.pop('pm25_scale')
                self.assertEqual(a, b)
            for rel in ('comparison.csv', 'observations.csv', 'run.json', 'control_checks.csv',
                        'sensitivity/comparison.csv', 'sensitivity/observations.csv', 'sensitivity/run.json'):
                self.assertEqual((destinations[0]/rel).read_bytes(), (destinations[1]/rel).read_bytes())
        self.assertEqual(source.read_bytes(), original)

    def test_dashboard_both_scenarios(self):
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file(str(ROOT/'app_lab4.py')).run(timeout=30)
        self.assertFalse(at.exception)
        self.assertEqual(len(at.metric), 3)
        self.assertTrue(at.warning)
        at.radio[0].set_value('Próba wrażliwości').run(timeout=30)
        self.assertFalse(at.exception)
        self.assertEqual(len(at.metric), 3)
