"""Kontrola miary i niezależności wyboru zwycięzcy od założonej metody."""
import csv
from pathlib import Path
import tempfile
import unittest

from scripts.compare_scoring_methods import evaluate, read_cases


class ScoringComparison(unittest.TestCase):
    def setUp(self):
        self.case = dict(case_id="cold", description="Chłód", pm10_daily_mean=20,
                         predicted_pm10=20, temperature_2m=0, wind_speed_10m=5,
                         precipitation=0, reference_score=80,
                         reference_source="synthetic_assumption")

    def test_hand_calculated_scores_and_mae(self):
        # PM10: 28.7778 pkt; pogoda: aplikacja 12.5+25+15, baza 25+25+15.
        # Po zaokrągleniu 81 i 94. Drugi przypadek ma błąd 0 dla obu metod.
        comfortable = dict(self.case, case_id="comfortable", temperature_2m=15,
                           reference_score=94)
        rows, comparison = evaluate([self.case, comfortable], 20)
        self.assertEqual(rows[0]["application_score"], 81)
        self.assertEqual(rows[0]["threshold_score"], 94)
        self.assertEqual([r["mae_points"] for r in comparison], [7, 0.5])

    def test_baseline_can_win_and_ties_are_possible(self):
        _, comparison = evaluate([dict(self.case, reference_score=94)], 20)
        self.assertEqual([r["mae_points"] for r in comparison], [0, 13])
        _, comparison = evaluate([dict(self.case, temperature_2m=15, reference_score=94)], 20)
        self.assertEqual([r["mae_points"] for r in comparison], [0, 0])

    def test_invalid_references_and_duplicate_cases_rejected(self):
        for updates, duplicate in (({"reference_score": "nan"}, False),
                                   ({"reference_score": 101}, False),
                                   ({"reference_source": ""}, False), ({}, True)):
            with self.subTest(updates=updates, duplicate=duplicate):
                row = dict(self.case, **updates)
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "input.csv"
                    with path.open("w", newline="", encoding="utf-8") as stream:
                        writer = csv.DictWriter(stream, fieldnames=list(row))
                        writer.writeheader()
                        writer.writerows([row, row] if duplicate else [row])
                    with self.assertRaises(ValueError):
                        read_cases(path)


if __name__ == "__main__":
    unittest.main()
