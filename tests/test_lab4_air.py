import unittest
from scripts.lab4_air import check_pm, summarize_pm
from scripts.lab4_controls import high_pm_cases

class AirQuality(unittest.TestCase):
    def test_bad_measurements_rejected(self):
        for value in ('', None, '-1', 'nan', 'inf', '-inf'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                check_pm({'pm25': value, 'pm10': 20})

    def test_flag_does_not_delete_measurement(self):
        report = summarize_pm([{'pm25': 25, 'pm10': 20}, {'pm25': 5, 'pm10': 10}])
        self.assertEqual(report['n'], 2)
        self.assertEqual(report['pm25_above_pm10_review_count'], 1)

    def test_zero_and_fractional_measurements(self):
        self.assertEqual(check_pm({'pm25': '0', 'pm10': '12.5'}), {'pm25': 0., 'pm10': 12.5})

    def test_empty_sample_rejected(self):
        with self.assertRaises(ValueError):
            summarize_pm([])

    def test_sentinels_cover_each_pollutant_separately(self):
        cases = dict(high_pm_cases({'pm25_scale': 25, 'pm10_scale': 50}))
        self.assertEqual(cases['high_pm25']['pm25'], 50)
        self.assertEqual(cases['high_pm25']['pm10'], 0)
        self.assertEqual(cases['high_pm10']['pm10'], 100)
        self.assertEqual(cases['high_pm10']['pm25'], 0)

    def test_saved_results_independent_check(self):
        from pathlib import Path
        from scripts.verify_pm_results import verify
        root = Path(__file__).resolve().parents[1]
        result = verify(root/'data/processed/aerorun_dane.csv', root/'results/lab4')
        self.assertEqual([row['observations_checked'] for row in result], [144, 144])
