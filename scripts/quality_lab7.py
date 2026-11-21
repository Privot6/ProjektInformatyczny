"""Pomiar jakości całego lokalnego przepływu na archiwalnej dobie.

Nie jest to zestaw testów: zapisuje obserwacje i MAE do oceny przez operatora.
"""
import csv
from datetime import datetime
import json
from pathlib import Path
from statistics import mean
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import manual_lab7 as session
from backend.model import ZONE, features
from scripts.compare_methods import gios_days, read_json

result = session.show("2026-11-13", "quality-day")
days = gios_days(read_json(session.ROOT / "data/raw/lab6/gios.json"), ZONE)
measurements = {int(t.timestamp()): v for hours in days.values() for t, v in hours.items()}
rows = []
for hour in result["hours"]:
    target_stamp = hour["timestamp_utc"] + 3600
    target = measurements.get(target_stamp)
    if target is None or None in features(hour):
        continue
    predicted = max(0.0, float(session.model.predict([features(hour)])[0]))
    rows.append({"timestamp": hour["timestamp"],
                 "target_timestamp": datetime.fromtimestamp(target_stamp, ZONE).isoformat(),
                 "observed_pm10_ug_m3": target, "predicted_pm10_ug_m3": predicted,
                 "daily_forecast_pm10_ug_m3": hour["pm10_daily_mean"],
                 "absolute_error_ug_m3": abs(predicted - target),
                 "daily_absolute_error_ug_m3": abs(hour["pm10_daily_mean"] - target),
                 "score": hour["score"], "message": hour["message"]})
out = session.ROOT / "results/lab7"
with (out / "quality-observations.csv").open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
summary = {"date": result["date"], "n": len(rows),
           "mae_ug_m3": mean(r["absolute_error_ug_m3"] for r in rows),
           "daily_forecast_mae_ug_m3": mean(r["daily_absolute_error_ug_m3"] for r in rows),
           "target": "station 16344 PM10 at t+1h",
           "training": session.metrics,
           "limitation": "Single archived forecast; no independent labels of training suitability. Daily Lab4 MAE has a different target and period."}
(out / "quality-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
session.client.close()
session.temporary.cleanup()
