"""Osobny eksperyment Lab 4: punktacja aplikacji a reguły progowe.

Domyślne oceny wzorcowe są ocenami ekspertów.
"""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.model import training_score

NUMERIC_FIELDS = (
    "pm10_daily_mean", "predicted_pm10", "temperature_2m",
    "wind_speed_10m", "precipitation", "reference_score",
)
REQUIRED_FIELDS = ("case_id", "description", *NUMERIC_FIELDS, "reference_source")
PRACTICAL_THRESHOLD = 2.0


def read_cases(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(REQUIRED_FIELDS).issubset(reader.fieldnames or []):
            raise ValueError(f"Wymagane kolumny CSV: {', '.join(REQUIRED_FIELDS)}")
        cases, ids = [], set()
        for row in reader:
            if any(not row.get(key, "") for key in REQUIRED_FIELDS):
                raise ValueError(f"Brak wartości w wierszu {reader.line_num}")
            if row["case_id"] in ids:
                raise ValueError(f"Powtórzone case_id: {row['case_id']}")
            ids.add(row["case_id"])
            for key in NUMERIC_FIELDS:
                row[key] = float(row[key])
                if not math.isfinite(row[key]):
                    raise ValueError(f"Nieskończona lub brakująca liczba: {key}")
            if not 0 <= row["reference_score"] <= 100:
                raise ValueError("Ocena wzorcowa musi być w zakresie 0–100")
            if any(row[key] < 0 for key in (
                "pm10_daily_mean", "predicted_pm10", "wind_speed_10m", "precipitation",
            )):
                raise ValueError("PM10, wiatr i opad nie mogą być ujemne")
            cases.append(row)
    if not cases:
        raise ValueError("CSV nie zawiera przypadków oceny")
    return cases


def threshold_score(row, wind_limit=20):
    """Prosta baza: pogoda 0/100, pozostałe elementy wspólne z aplikacją."""
    air = max(0, 100 - 40 * row["predicted_pm10"] / 45)
    points = (
        0.35 * air
        + 25 * (0 <= row["temperature_2m"] <= 30)
        + 25 * (row["wind_speed_10m"] <= wind_limit)
        + 15 * (row["precipitation"] < 2)
    )
    if row["pm10_daily_mean"] >= 112.5 or row["precipitation"] >= 4:
        points = min(points, 39)
    return round(points)


def evaluate(cases, wind_limit):
    observations = []
    for row in cases:
        scores = {
            "threshold": threshold_score(row, wind_limit),
            "application": training_score(row, row["predicted_pm10"]),
        }
        result = dict(row)
        for method, score in scores.items():
            result[f"{method}_score"] = score
            result[f"{method}_absolute_error_points"] = abs(score - row["reference_score"])
        observations.append(result)
    comparison = [
        {
            "method": method, "n_cases": len(cases),
            "mae_points": mean(row[f"{method}_absolute_error_points"] for row in observations),
        }
        for method in ("threshold", "application")
    ]
    return observations, comparison


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(input_path, output):
    cases = read_cases(input_path)
    improvements = []
    for name, wind_limit, destination in (
        ("main", 20, output), ("sensitivity", 15, output / "sensitivity"),
    ):
        observations, comparison = evaluate(cases, wind_limit)
        baseline, application = (row["mae_points"] for row in comparison)
        improvement = baseline - application
        improvements.append(improvement)
        metadata = {
            "scenario": name,
            "data_sha256": digest(input_path),
            "application_model_sha256": digest(ROOT / "backend/model.py"),
            "script_sha256": digest(Path(__file__)),
            "reference_sources": sorted({row["reference_source"] for row in cases}),
            "reference_note": "Pochodzenie deklarowane w CSV; domyślna próbka jest oceną ekspertów.",
            "scope": "Tylko punktacja; wspólne założone PM10, bez treningu i oceny Ridge.",
            "baseline": {"temperature_range_c": [0, 30], "wind_max_kmh": wind_limit,
                         "rain_below_mm": 2, "weights": [0.35, 0.25, 0.25, 0.15]},
            "application": "backend.model.training_score (bez zmian)",
            "metric": "MAE w punktach oceny 0–100",
            "application_improvement_points": improvement,
            "practical_threshold_points": PRACTICAL_THRESHOLD,
            "lower_mae": "application" if improvement > 0 else "threshold" if improvement < 0 else "tie",
        }
        destination.mkdir(parents=True, exist_ok=True)
        write_csv(destination / "observations.csv", observations)
        write_csv(destination / "comparison.csv", comparison)
        (destination / "run.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8", newline="\n",
        )
        print(f"{name}: n={len(cases)}, MAE baza={baseline:.4f}, aplikacja={application:.4f} pkt")
    meets = all(value >= PRACTICAL_THRESHOLD for value in improvements)
    print("Kryterium przewagi aplikacji w obu próbach: " + ("spełnione" if meets else "niespełnione"))
    print("Domyślne oceny są opinią ekspertów. Wynik dowodzi przewagę w rzeczywistym użyciu.")
    return meets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/processed/lab4_scoring_scenarios.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "results/lab4/scoring")
    args = parser.parse_args()
    try:
        run(args.input, args.output)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Błąd porównania: {error}\n")


if __name__ == "__main__":
    main()
