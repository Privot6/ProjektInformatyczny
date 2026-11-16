"""Godzinowy model ekspozycji AeroRun. Trening raz przy starcie procesu."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from scripts.compare_methods import ROOT, gios_days, read_json, sha256
from scripts.prepare_forecast import LOCAL_TIMEZONE, read_pm10, read_weather

ZONE = ZoneInfo(LOCAL_TIMEZONE)
FIELDS = ("pm10_daily_mean", "temperature_2m", "wind_speed_10m", "precipitation")


def features(row):
    return [row[key] for key in FIELDS]


def train():
    directory = ROOT / "data/raw/lab6"
    manifest = read_json(directory / "sources.json")
    observations = directory / "gios.json"
    if sha256(observations) != manifest["gios.json"]["sha256"]:
        raise ValueError("Niezgodna suma SHA-256 pomiarów LAB6")
    days = gios_days(read_json(observations), ZONE)
    pm = {int(t.timestamp()): v for hours in days.values() for t, v in hours.items()}
    sample = read_json(ROOT / "data/raw/sample.json")
    daily = read_pm10(sample["ios_pib_pm10"])
    weather = read_weather(sample["open_meteo"], ZONE)
    issued = max(datetime.fromisoformat(s["retrieved_at_utc"]) for s in sample["metadata"]["sources"].values())
    test_start = date(2026, 11, 13)
    training, testing = [], []
    for rows in weather.values():
        for row in rows:
            stamp = datetime.fromisoformat(row["timestamp"])
            if stamp < issued:
                continue
            t = int(stamp.timestamp())
            x = features({**row, "pm10_daily_mean": daily.get(stamp.date())})
            y = pm.get(t + 3600)
            if None in x or y is None:
                continue
            if stamp.date() < test_start:
                if datetime.fromtimestamp(t + 3600, ZONE).date() < test_start:
                    training.append((x, y))
            else:
                testing.append((x, y))
    x, y = zip(*training)
    model = make_pipeline(StandardScaler(), Ridge(alpha=1, solver="svd")).fit(x, y)
    xt, yt = zip(*testing)
    report = {"train_hours": len(y), "test_hours": len(yt),
              "mae_ug_m3": mean_absolute_error(yt, np.maximum(0, model.predict(xt))),
              "daily_forecast_mae": mean_absolute_error(yt, [v[0] for v in xt])}
    return model, report


def classify(score):
    if score >= 70:
        return "TRENUJ"
    return "OGRANICZ" if score >= 40 else "ZOSTAŃ W DOMU"


def membership(value):
    return min(1.0, max(0.0, value))


def training_score(row, predicted_pm10):
    temperature = row["temperature_2m"]
    wind = row["wind_speed_10m"]
    rain = row["precipitation"]
    # Pary reguł Sugeno: korzystne -> 100 pkt, niekorzystne -> 0 pkt.
    # Stopnie aktywacji każdej pary sumują się do 1.
    good_temperature = membership(min((temperature + 5) / 10, (35 - temperature) / 10))
    light_wind = membership((30 - wind) / 20)
    dry = membership(1 - rain / 4)
    rules = ((0.25, good_temperature), (0.25, light_wind), (0.15, dry))
    air_points = max(0, 100 - 40 * max(0, predicted_pm10) / 45)
    points = 0.35 * air_points
    for weight, favorable in rules:
        points += weight * favorable * 100
    if row["pm10_daily_mean"] >= 112.5 or rain >= 4:
        points = min(points, 39)
    return round(points)


def evaluate(rows, model):
    valid = [row for row in rows if None not in features(row)]
    if not valid:
        return None
    for row, predicted in zip(valid, model.predict([features(row) for row in valid])):
        score = training_score(row, predicted)
        row.update(score=score, message=classify(score))
    return max(valid, key=lambda row: row["score"])
