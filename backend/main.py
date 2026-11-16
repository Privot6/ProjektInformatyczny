from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
import logging
import os
import sqlite3
from threading import Lock
from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException

from backend import storage
from backend.model import FIELDS, ZONE, evaluate, train
from backend.sources import PM10_URL, fetch, retry_at, timestamps
from scripts.compare_methods import ROOT
from scripts.prepare_forecast import WEATHER_UNITS

logger = logging.getLogger("uvicorn.error")
refresh = Lock()


@asynccontextmanager
async def lifespan(app):
    app.state.model, app.state.metrics = train()
    app.state.backoff = {}
    app.state.db = os.getenv("AERORUN_DB", str(ROOT / "aerorun.sqlite3"))
    try:
        storage.initialize(app.state.db)
    except sqlite3.Error:
        logger.exception("Nie udało się otworzyć bazy SQLite")
    mounts = {}
    if os.getenv("AERORUN_PM10_UNVERIFIED_TLS") == "1":
        origin = httpx.URL(PM10_URL)
        mounts[f"https://{origin.host}:443"] = httpx.HTTPTransport(verify=False)
    with httpx.Client(timeout=15, mounts=mounts) as client:
        app.state.client = client
        yield


app = FastAPI(title="AeroRun", lifespan=lifespan)


def check(day, state):
    warnings = []
    key = day.isoformat()
    try:
        cache, captures = storage.read(state.db, key)
    except sqlite3.Error:
        cache, captures = {}, {}
        warnings.append("Nie udało się odczytać SQLite.")
    source_names = ["ios_pib_pm10", "open_meteo"]
    values, origins = {}, {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        now = datetime.now(timezone.utc)
        jobs = {s: pool.submit(fetch, state.client, s, day) for s in source_names
                if state.backoff.get(s, now) <= now}
        for source in source_names:
            try:
                if source not in jobs:
                    raise ValueError("Retry-After")
                values[source] = jobs[source].result()
                captures[source] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                origins[source] = "network"
            except (httpx.HTTPError, ValueError, TypeError, KeyError, AttributeError) as exc:
                if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429:
                    state.backoff[source] = retry_at(exc.response, datetime.now(timezone.utc))
                logger.warning("Błąd źródła %s: %s", source, type(exc).__name__)
                fields = ("pm10_daily_mean",) if source == "ios_pib_pm10" else WEATHER_UNITS
                label = "prognozy dobowej PM10 (IOŚ-PIB)" if source == "ios_pib_pm10" else "pogody (Open-Meteo)"
                message = f"Nie udało się pobrać {label}."
                if isinstance(exc, httpx.ConnectError) and "CERTIFICATE_VERIFY_FAILED" in str(exc):
                    message += " Nie udało się potwierdzić certyfikatu serwera."
                warnings.append(message)
                if source in captures:
                    values[source] = {t: {k: r[k] for k in fields} for t, r in cache.items()}
                    origins[source] = "cache"
    if not values:
        raise HTTPException(503, "Źródła są niedostępne. Brak zapisu dla tego dnia.")
    rows = []
    for stamp in timestamps(day):
        row = dict.fromkeys(FIELDS)
        for data in values.values():
            row.update(data.get(stamp, {}))
        row.update(timestamp_utc=stamp, timestamp=datetime.fromtimestamp(stamp, ZONE).isoformat(timespec="minutes"),
                   score=None, message=None)
        rows.append(row)
    if "network" in origins.values():
        try:
            storage.save(state.db, key, rows, captures)
        except sqlite3.Error:
            warnings.append("Nie udało się zapisać wyniku w SQLite.")
    best = evaluate(rows, state.model)
    return {"date": key, "pm10_daily_mean": rows[0]["pm10_daily_mean"], "hours": rows, "best": best, "origin": origins,
            "retrieved_at_utc": captures, "warnings": warnings,
            "pm10_notice": "Brak prognozy dobowej PM10 dla wybranego dnia." if rows[0]["pm10_daily_mean"] is None else None}


@app.get("/forecast/{day}")
def forecast(day: Literal["today", "tomorrow"]):
    with refresh:
        today = datetime.now(ZONE).date()
        tomorrow = day == "tomorrow"
        return check(today + timedelta(days=int(tomorrow)), app.state)
