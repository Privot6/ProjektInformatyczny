"""Zbierz czasy lokalnego przepływu; bez asercji, testów i automatycznej oceny."""
import csv
from datetime import date
import json
from pathlib import Path
import platform
from statistics import median
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import manual_lab7 as session

day = date(2026, 11, 12)
session.check(day, session.state)  # Jedna rozgrzewka, poza pomiarem.
rows = []
for repeat in range(1, 6):
    start = perf_counter()
    result = session.check(day, session.state)
    elapsed = perf_counter() - start
    rows.append({"repeat": repeat, "hours": len(result["hours"]), "seconds": elapsed})

out = session.ROOT / "results/lab7"
out.mkdir(parents=True, exist_ok=True)
with (out / "timing.csv").open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
times = [r["seconds"] for r in rows]
summary = {"python": platform.python_version(), "system": platform.system(),
           "machine": platform.machine(), "processor": platform.processor(),
           "warmup": 1, "repeats": 5, "hours": 24,
           "scope": "check: replay HTTP, read, validation, predict, score, SQLite write; no real network or model training",
           "criterion_seconds_median_below": 2,
           "median_seconds": median(times), "min_seconds": min(times), "max_seconds": max(times)}
(out / "timing-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
session.client.close()
session.temporary.cleanup()
