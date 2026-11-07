import unittest
from scripts.fuzzy_model import FuzzyModel, load_config, baseline, memberships

class FuzzyInference(unittest.TestCase):
    def setUp(self):
        self.cfg = load_config()
        self.model = FuzzyModel(self.cfg)
        self.good = dict(pm25=5, pm10=10, temperature_2m=15, wind_speed_10m=5, precipitation=0)

    def test_manual_triangle_centroid(self):
        result = self.model.evaluate(self.good)
        self.assertAlmostEqual(result['score'], 90., places=7)
        self.assertEqual(result['r_good'], 1)
        self.assertEqual(result['label'], 'TRENUJ')
        bad = self.model.evaluate({**self.good, 'pm25': 100})
        self.assertAlmostEqual(bad['score'], 10., places=7)

    def test_worst_pm_not_cancelled_by_weather(self):
        for field in ('pm25', 'pm10'):
            row = {**self.good, field: 1000}
            self.assertEqual(self.model.evaluate(row)['label'], 'ZOSTAŃ W DOMU')
            self.assertEqual(baseline(row, self.cfg)['label'], 'ZOSTAŃ W DOMU')

    def test_coverage_and_bounds(self):
        for name, anchors in self.cfg['anchors'].items():
            for value in (0, *anchors, self.cfg['caps'][name], self.cfg['caps'][name]*2):
                mu = memberships(value, anchors, self.cfg['caps'][name])
                self.assertGreater(max(mu), 0)
        for value in (0, 15, 20, 25, 30, 35, 1000):
            score = self.model.evaluate({**self.good, 'pm25': value})['score']
            self.assertTrue(0 <= score <= 100)

    def test_bad_input_is_not_silently_clipped(self):
        for value in (-1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                self.model.evaluate({**self.good, 'pm25': value})

    def test_hard_threshold_and_fuzzy_continuity(self):
        before = {**self.good, 'pm25': 20.0}
        after = {**before, 'pm25': 20.00001}
        self.assertEqual(baseline(before, self.cfg)['score'], 90)
        self.assertEqual(baseline(after, self.cfg)['score'], 50)
        self.assertLess(abs(self.model.evaluate(after)['score']-self.model.evaluate(before)['score']), .001)
