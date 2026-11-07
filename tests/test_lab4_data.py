import unittest, tempfile, csv
from pathlib import Path
from scripts.lab4_data import load_data, check_weather, FIELDS

class DataContract(unittest.TestCase):
    def load(self, stamps):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'test.csv'
            with path.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(FIELDS)
                for stamp in stamps:
                    writer.writerow([stamp, 10, 20, 12, 7, 0])
            return load_data(path)

    def test_clock_change_keeps_two_local_hours(self):
        rows = self.load(['2026-10-25T02:00:00+02:00', '2026-10-25T02:00:00+01:00'])
        self.assertEqual(len(rows), 2)

    def test_duplicates_gaps_and_naive_times(self):
        for stamps in (["2026-10-20T00:00:00"],
                       ["2026-10-20T00:00:00+02:00"] * 2,
                       ["2026-10-20T00:00:00+02:00", "2026-10-20T02:00:00+02:00"]):
            with self.subTest(stamps=stamps), self.assertRaises(ValueError):
                self.load(stamps)

    def test_bad_weather(self):
        row = dict(temperature_2m=10, wind_speed_10m=5, precipitation=0)
        for key, value in [('temperature_2m', 100), ('wind_speed_10m', -1), ('precipitation', 'nan')]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                check_weather({**row, key: value})

    def test_original_sample(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(len(load_data(root / 'data/processed/aerorun_dane.csv')), 72)
