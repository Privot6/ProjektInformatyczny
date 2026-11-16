"""Odczyt i atomowa wymiana godzin wybranego dnia."""
from contextlib import closing
import sqlite3

from scripts.compare_methods import ROOT
from scripts.prepare_forecast import WEATHER_UNITS


def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def initialize(path):
    with closing(connect(path)) as db, db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='forecast_day'").fetchone():
            db.executescript("BEGIN;\n" + (ROOT / "docs/lab5/schema.sql").read_text(encoding="utf-8"))
        else:
            db.execute("BEGIN IMMEDIATE")
        if "pm10" not in {r["name"] for r in db.execute("PRAGMA table_info(forecast_hour)")}:
            db.execute("ALTER TABLE forecast_hour ADD COLUMN pm10 REAL CHECK(pm10 >= 0)")
        db.execute("""CREATE TABLE IF NOT EXISTS day_capture(
            local_date TEXT REFERENCES forecast_day(local_date), source TEXT NOT NULL,
            retrieved_at_utc TEXT NOT NULL, PRIMARY KEY(local_date, source)) STRICT""")


def read(path, day):
    with closing(connect(path)) as db, db:
        db.execute("BEGIN")
        captures = dict(db.execute("SELECT source,retrieved_at_utc FROM day_capture WHERE local_date=? AND source IN ('ios_pib_pm10','open_meteo')", (day,)))
        rows = {r["timestamp_utc"]: dict(r) for r in db.execute(
            "SELECT h.*, d.pm10_daily_mean FROM forecast_hour h JOIN forecast_day d USING(local_date) WHERE local_date=? ORDER BY timestamp_utc", (day,))}
    return rows, captures


def save(path, day, rows, captures):
    missing = sum(any(r[k] is None for k in WEATHER_UNITS) for r in rows)
    with closing(connect(path)) as db, db:
        db.execute("""INSERT INTO forecast_day(local_date, missing_weather_hours, pm10_daily_mean) VALUES (?,?,?)
            ON CONFLICT(local_date) DO UPDATE SET missing_weather_hours=excluded.missing_weather_hours, pm10_daily_mean=excluded.pm10_daily_mean""",
                   (day, missing, rows[0]["pm10_daily_mean"]))
        db.execute("DELETE FROM forecast_hour WHERE local_date=?", (day,))
        db.executemany("""INSERT INTO forecast_hour
            (timestamp_utc, local_date, temperature_2m, precipitation, wind_speed_10m)
            VALUES (?,?,?,?,?)""", [(r["timestamp_utc"], day, *(r[k] for k in WEATHER_UNITS)) for r in rows])
        db.executemany("INSERT OR REPLACE INTO day_capture VALUES (?,?,?)",
                       [(day, source, stamp) for source, stamp in captures.items()])
        db.executemany("INSERT OR REPLACE INTO source_capture VALUES (?,?)", captures.items())
