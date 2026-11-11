import csv
import json
import unittest
from datetime import date
from pathlib import Path
from statistics import mean
from zoneinfo import ZoneInfo

from scripts.compare_methods import load_data, sha256


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/lab4"


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


class Lab4(unittest.TestCase):
    def test_temporal_split_and_metric(self):
        main = RESULTS
        sensitivity = main / "sensitivity"
        scenarios = [json.loads((folder / "run.json").read_bytes()) for folder in (main, sensitivity)]
        self.assertEqual(scenarios[0]["training_dates"], scenarios[1]["training_dates"])
        self.assertEqual(scenarios[0]["test_dates"], scenarios[1]["test_dates"])
        self.assertLess(max(scenarios[0]["training_dates"]), min(scenarios[0]["test_dates"]))
        self.assertEqual([run["tree"]["max_depth"] for run in scenarios], [3, 4])
        for folder, run in zip((main, sensitivity), scenarios):
            rows = read_csv(folder / "observations.csv")
            scores = {row["method"]: row for row in read_csv(folder / "comparison.csv")}
            self.assertEqual([row["date"] for row in rows], run["test_dates"])
            self.assertEqual(len({row["date"] for row in rows}), len(rows))
            for method, score in scores.items():
                errors = [
                    abs(float(row["observed_pm10_ug_m3"]) - float(row[f"{method}_pm10_ug_m3"]))
                    for row in rows
                ]
                for error, row in zip(errors, rows):
                    self.assertAlmostEqual(error, float(row[f"{method}_absolute_error_ug_m3"]))
                self.assertEqual(int(score["n_test"]), len(rows))
                self.assertAlmostEqual(mean(errors), float(score["mae_ug_m3"]))
            self.assertLess(float(scores["ridge"]["mae_ug_m3"]), float(scores["tree"]["mae_ug_m3"]))

    def test_source_coverage_and_lab3_application(self):
        raw = ROOT / "data/raw/lab4"
        rows, excluded, sources = load_data(raw, ZoneInfo("Europe/Warsaw"))
        self.assertEqual((len(rows), len(excluded)), (47, 14))
        self.assertIn(date(2026, 10, 25), {day for day, _, _ in rows})
        self.assertEqual(excluded["2026-10-26"]["missing_pm10_hours"], 1)
        for filename, metadata in sources.items():
            self.assertEqual(sha256(raw / filename), metadata["sha256"])
        applied = read_csv(RESULTS / "lab3_application.csv")
        self.assertEqual([row["date"] for row in applied], ["2026-11-12", "2026-11-13"])
        self.assertEqual([float(row["ios_pib_forecast_ug_m3"]) for row in applied], [31.59, 37.07])
        self.assertNotIn("observed_pm10_ug_m3", applied[0])


if __name__ == "__main__":
    unittest.main()
