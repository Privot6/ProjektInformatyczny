"""Porównanie Ridge i drzewa regresyjnego na dobowych danych z Rzeszowa."""

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import StatisticsError, correlation, mean
from zoneinfo import ZoneInfo

import numpy as np
import sklearn
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.prepare_forecast import (
    LOCAL_TIMEZONE, WEATHER_UNITS, check_number, missing_weather_hours, read_weather,
)

START = date(2026, 9, 1)
TEST_START = date(2026, 10, 12)
END = date(2026, 10, 31)
FEATURES = ("temperature_mean_c", "wind_mean_kmh", "precipitation_sum_mm")
IMPROVEMENT_REQUIRED = 1.0
TREE_PARAMS = {"criterion": "squared_error", "min_samples_leaf": 5, "random_state": 42}


def read_json(path):
    return json.loads(path.read_bytes())


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gios_days(payload, zone):
    if payload["totalPages"] != 1:
        raise ValueError("Archiwum GIOŚ musi zawierać wszystkie strony zapytania")
    cet = timezone(timedelta(hours=1))
    days = defaultdict(dict)
    for row in payload["Lista archiwalnych wyników pomiarów"]:
        if row["Kod stanowiska"] != "PkRzeszPilsu-PM10-1g":
            raise ValueError("Oczekiwano godzinowych pomiarów PM10 z Rzeszowa")
        stamp = datetime.fromisoformat(row["Data"])
        if stamp.tzinfo or stamp.minute or stamp.second or stamp.microsecond:
            raise ValueError("Oczekiwano pełnej godziny GIOŚ w stałym CET")
        utc = stamp.replace(tzinfo=cet).astimezone(timezone.utc)
        day = utc.astimezone(zone).date()
        if utc in days[day]:
            raise ValueError(f"Powtórzona godzina GIOŚ: {utc.isoformat()}")
        value = row["Wartość"]
        check_number(value, "PM10 GIOŚ", 0)
        days[day][utc] = value
    return days


def weather_features(day, hours, zone):
    stamps = [datetime.fromisoformat(row["timestamp"]) for row in hours]
    if (len({stamp.astimezone(timezone.utc) for stamp in stamps}) != len(stamps)
            or any(stamp.tzinfo is None or stamp.astimezone(zone).date() != day
                   or stamp.minute or stamp.second or stamp.microsecond for stamp in stamps)):
        raise ValueError(f"Niespójne godziny pogody: {day}")
    if missing_weather_hours(day, hours, zone):
        return None
    return (
        mean(row["temperature_2m"] for row in hours),
        mean(row["wind_speed_10m"] for row in hours),
        sum(row["precipitation"] for row in hours),
    )


def load_data(raw_dir, zone):
    sources = read_json(raw_dir / "sources.json")
    paths = {key: raw_dir / key for key in ("gios.json", "weather.json")}
    for key, path in paths.items():
        if sha256(path) != sources[key]["sha256"]:
            raise ValueError(f"Zmieniona próbka źródłowa: {path}")
    pm10 = gios_days(read_json(paths["gios.json"]), zone)
    weather = read_weather(read_json(paths["weather.json"]), zone)
    rows, excluded = [], {}
    for offset in range((END - START).days + 1):
        day = START + timedelta(days=offset)
        values = pm10.get(day, {})
        expected_hours = missing_weather_hours(day, [], zone)
        complete_pm10 = sum(value is not None for value in values.values())
        features = weather_features(day, weather.get(day, []), zone)
        if features is None or complete_pm10 != expected_hours:
            excluded[day.isoformat()] = {
                "missing_pm10_hours": expected_hours - complete_pm10,
                "missing_weather_hours": missing_weather_hours(day, weather.get(day, []), zone),
            }
            continue
        rows.append((day, features, mean(values.values())))
    return rows, excluded, sources


def load_lab3(path, zone):
    sample = read_json(path)
    expected_units = {"pm10_daily_mean": "µg/m³", **WEATHER_UNITS}
    if (sample["teryt"], sample["timezone"], sample["units"]) != ("1863", LOCAL_TIMEZONE, expected_units):
        raise ValueError("Niezgodny zakres, strefa lub jednostki próbki Lab 3")
    for day in sample["days"]:
        features = weather_features(date.fromisoformat(day["date"]), day["weather"], zone)
        if features is not None and day["pm10_daily_mean"] is not None:
            yield day["date"], features, day["pm10_daily_mean"]


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pearson(feature, target):
    try:
        return correlation(feature, target)
    except StatisticsError:
        return None


def evaluate(train, test, lab3, depth):
    x_train = np.array([features for _, features, _ in train])
    y_train = np.array([target for _, _, target in train])
    x_test = np.array([features for _, features, _ in test])
    y_test = np.array([target for _, _, target in test])
    ridge = make_pipeline(StandardScaler(), Ridge(alpha=1.0, solver="svd"))
    tree = DecisionTreeRegressor(max_depth=depth, **TREE_PARAMS)
    models = {"ridge": ridge, "tree": tree}
    for model in models.values():
        model.fit(x_train, y_train)

    predictions = {key: model.predict(x_test).clip(min=0) for key, model in models.items()}
    if not all(np.isfinite(values).all() for values in predictions.values()):
        raise ValueError("Model zwrócił niepoprawną wartość PM10")
    scores = {key: float(mean_absolute_error(y_test, values)) for key, values in predictions.items()}
    observations = []
    for index, (day, features, target) in enumerate(test):
        row = {"date": day.isoformat(), **dict(zip(FEATURES, features)), "observed_pm10_ug_m3": target}
        for key, values in predictions.items():
            row[f"{key}_pm10_ug_m3"] = float(values[index])
            row[f"{key}_absolute_error_ug_m3"] = float(abs(target - values[index]))
        observations.append(row)

    application = []
    for day, features, published in lab3:
        application.append({
            "date": day, **dict(zip(FEATURES, features)), "ios_pib_forecast_ug_m3": published,
            **{f"{key}_estimate_ug_m3": float(model.predict([features]).clip(min=0)[0])
               for key, model in models.items()},
        })

    scaler, estimator = ridge["standardscaler"], ridge["ridge"]
    raw_coef = estimator.coef_ / scaler.scale_
    tree_leaf = tree.apply(x_test[:1])[0]
    diagnostic = {
        "tree_fitted_depth": tree.get_depth(),
        "ridge_intercept_original_units": float(estimator.intercept_ - raw_coef @ scaler.mean_),
        "ridge_coefficients_original_units": dict(zip(FEATURES, map(float, raw_coef))),
        "pearson_training": {name: pearson(x_train[:, i], y_train) for i, name in enumerate(FEATURES)},
        "first_test_tree_leaf_training_values": y_train[tree.apply(x_train) == tree_leaf].tolist(),
        "first_test_date": test[0][0].isoformat(),
    }
    return scores, observations, application, diagnostic


def run(raw_dir, lab3_path, output):
    zone = ZoneInfo(LOCAL_TIMEZONE)
    rows, excluded, sources = load_data(raw_dir, zone)
    train = [row for row in rows if row[0] < TEST_START]
    test = [row for row in rows if row[0] >= TEST_START]
    if len(train) < 10 or not test:
        raise ValueError("Za mało kompletnych dób w części uczącej lub testowej")
    lab3 = list(load_lab3(lab3_path, zone))
    if not lab3:
        raise ValueError("Brak kompletnych dni w próbce Lab 3")
    source_info = {
        "lab3_sha256_utf8_lf": hashlib.sha256(
            lab3_path.read_text(encoding="utf-8").encode("utf-8")
        ).hexdigest(),
        "sources": sources,
        "training_dates": [day.isoformat() for day, _, _ in train],
        "test_dates": [day.isoformat() for day, _, _ in test],
        "excluded_dates": excluded,
        "python": sys.version.split()[0],
        "scikit_learn": sklearn.__version__,
    }
    improvements = []
    for depth, destination in ((3, output), (4, output / "sensitivity")):
        scores, observations, application, diagnostic = evaluate(train, test, lab3, depth)
        improvement = scores["ridge"] - scores["tree"]
        improvements.append(improvement)
        comparison = [
            {"method": key, "n_train": len(train), "n_test": len(test), "mae_ug_m3": value}
            for key, value in scores.items()
        ]
        destination.mkdir(parents=True, exist_ok=True)
        write_csv(destination / "observations.csv", observations)
        write_csv(destination / "comparison.csv", comparison)
        write_csv(destination / "lab3_application.csv", application)
        metadata = {
            **source_info, **diagnostic,
            "ridge": {"alpha": 1.0, "solver": "svd", "scaling": "training only"},
            "tree": {"max_depth": depth, **TREE_PARAMS},
            "tree_improvement_ug_m3": improvement,
            "practical_threshold_ug_m3": IMPROVEMENT_REQUIRED,
            "lower_mae": "ridge" if scores["ridge"] < scores["tree"] else
                         "tree" if scores["tree"] < scores["ridge"] else "tie",
        }
        (destination / "run.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8", newline="\n",
        )
        print(f"Limit drzewa {depth} | uczenie {len(train)}, test {len(test)} | "
              f"MAE Ridge {scores['ridge']:.4f}, drzewo {scores['tree']:.4f} ug/m3")
    selected = "tree" if all(x >= IMPROVEMENT_REQUIRED for x in improvements) else "ridge"
    print(f"Model do dalszej oceny: {selected}")
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw/lab4")
    parser.add_argument("--lab3", type=Path, default=ROOT / "data/processed/sample-clean.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/lab4")
    args = parser.parse_args()
    try:
        run(args.raw_dir, args.lab3, args.output)
    except FileNotFoundError as error:
        parser.exit(1, f"Brak pliku Lab 4: {Path(error.filename).resolve()}\n")


if __name__ == "__main__":
    main()
