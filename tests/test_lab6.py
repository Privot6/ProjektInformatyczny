from contextlib import closing
from datetime import date
from pathlib import Path
import json
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest

import httpx
from fastapi import HTTPException

from backend import storage
from backend.main import check
from backend.model import classify, evaluate, train, training_score
from backend.sources import timestamps
from scripts.compare_methods import ROOT


class Lab6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.metrics = train()

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "aerorun.sqlite3"
        # Otwórz istniejącą bazę LAB5, tak jak przy aktualizacji.
        with closing(sqlite3.connect(self.path)) as db:
            db.executescript((ROOT / "docs/lab5/schema.sql").read_text(encoding="utf-8"))
        storage.initialize(self.path)
        storage.initialize(self.path)
        self.requests = []

        def replay(request):
            self.requests.append(request)
            sample = json.loads((ROOT / "data/raw/sample.json").read_bytes())
            key = "ios_pib_pm10" if request.url.host == "api.prognozy.ios.edu.pl" else "open_meteo"
            return httpx.Response(200, json=sample[key])

        self.state = SimpleNamespace(model=self.model, db=self.path, backoff={},
                                     client=httpx.Client(transport=httpx.MockTransport(replay)))
        self.addCleanup(self.state.client.close)

    def test_archive_day_batch_and_cache(self):
        day = date(2026, 11, 12)
        result = check(day, self.state)
        self.assertEqual(len(self.requests), 2)
        self.assertEqual(len(result["hours"]), 24)
        self.assertEqual(len({r["timestamp"] for r in result["hours"]}), 24)
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["best"]["score"], max(r["score"] for r in result["hours"]))
        self.assertEqual(result["pm10_daily_mean"], 31.59)
        self.assertTrue(all(r["pm10_daily_mean"] == 31.59 for r in result["hours"]))
        for r in result["hours"]:
            single = dict(r, score=None, message=None)
            evaluate([single], self.model)
            self.assertEqual(single, r)
        self.assertEqual(len(storage.read(self.path, day.isoformat())[0]), 24)
        def unavailable(request):
            return httpx.Response(503)
        with httpx.Client(transport=httpx.MockTransport(unavailable)) as client:
            self.state.client = client
            cached = check(day, self.state)
            self.assertEqual(cached["origin"], {"ios_pib_pm10": "cache", "open_meteo": "cache"})
            self.assertEqual(cached["hours"], result["hours"])
            with self.assertRaises(HTTPException) as error:
                check(date(2026, 10, 26), self.state)
            self.assertEqual(error.exception.status_code, 503)

    def test_missing_and_invalid(self):
        when = date(2026, 10, 15)
        tomorrow = check(when, self.state)
        self.assertEqual(len(self.requests), 2)
        self.assertIsNone(tomorrow["best"])
        self.assertTrue(all(r["pm10_daily_mean"] is None and r["score"] is None for r in tomorrow["hours"]))
        with httpx.Client(transport=httpx.MockTransport(lambda req: httpx.Response(200, json=[]))) as client:
            self.state.client = client
            invalid = check(when, self.state)
            self.assertEqual(len(invalid["warnings"]), 2)
            self.assertIsNone(invalid["best"])

    def test_daily_mean_missing_only_for_requested_date(self):
        # Próbka LAB2 zawiera pogodę na 14 listopada, ale PM10 tylko do 13.
        result = check(date(2026, 11, 14), self.state)
        self.assertIsNone(result["pm10_daily_mean"])
        self.assertIsNone(result["best"])
        self.assertTrue(all(r["temperature_2m"] is not None and r["score"] is None for r in result["hours"]))

    def test_write_failure_and_rollback(self):
        when = date(2026, 10, 15)
        result = check(when, self.state)
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("""CREATE TRIGGER reject_hour BEFORE INSERT ON forecast_hour
                BEGIN SELECT RAISE(ABORT,'test'); END""")
        refreshed = check(when, self.state)
        self.assertTrue(refreshed["warnings"])
        self.assertEqual(result["best"], refreshed["best"])
        self.assertEqual(len(storage.read(self.path, when.isoformat())[0]), 24)

    def test_boundaries(self):
        self.assertEqual(len(timestamps(date(2026, 10, 25))), 25)
        self.assertEqual(len(timestamps(date(2026, 3, 29))), 23)
        self.assertEqual([classify(i) for i in (39, 40, 69, 70)],
                         ["ZOSTAŃ W DOMU", "OGRANICZ", "OGRANICZ", "TRENUJ"])
        self.assertEqual(self.model.n_features_in_, 4)

    def test_fuzzy_weather_and_air_contributions(self):
        row = dict(pm10_daily_mean=20, temperature_2m=15, wind_speed_10m=5, precipitation=0)
        self.assertEqual(training_score(row, 0), 100)
        for field, value, expected in [
            ("temperature_2m", -5, 75), ("temperature_2m", 35, 75),
            ("wind_speed_10m", 30, 75), ("precipitation", 2, 92),
            ("precipitation", 4, 39), ("pm10_daily_mean", 112.5, 39),
        ]:
            with self.subTest(field=field, value=value):
                self.assertEqual(training_score({**row, field: value}, 0), expected)
        self.assertEqual(training_score(row, 45), 86)

    def test_retry_after(self):
        calls = []
        def limited(request):
            calls.append(request)
            return httpx.Response(429, headers={"Retry-After": "60"})
        with httpx.Client(transport=httpx.MockTransport(limited)) as client:
            self.state.client = client
            for _ in range(2):
                with self.assertRaises(HTTPException):
                    check(date(2026, 10, 15), self.state)
        self.assertEqual(len(calls), 2)
