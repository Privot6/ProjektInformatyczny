"""Wspólny kontrakt danych eksperymentu; walidacja bez zmiany wejścia."""
import csv, math
from datetime import datetime, timezone
from pathlib import Path
from scripts.lab4_air import check_pm

FIELDS = ('timestamp', 'pm25', 'pm10', 'temperature_2m', 'wind_speed_10m', 'precipitation')

def check_weather(row):
    out = {}
    for key in FIELDS[3:]:
        try:
            value = float(row[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f'Brak lub błędne {key}') from exc
        if not math.isfinite(value):
            raise ValueError(f'{key}: wartość musi być skończona')
        if key == 'temperature_2m' and not -90 <= value <= 60:
            raise ValueError('Temperatura poza kontrolnym zakresem -90..60 C')
        if key != 'temperature_2m' and value < 0:
            raise ValueError(f'{key}: wartość ujemna')
        out[key] = value
    return out

def load_data(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if not set(FIELDS).issubset(reader.fieldnames or []):
            raise ValueError('Brak wymaganych kolumn wejścia')
        raw = list(reader)
    if not raw:
        raise ValueError('Pusta próbka')
    rows, seen = [], set()
    previous = None
    for i, row in enumerate(raw, 2):
        try:
            stamp = datetime.fromisoformat(row['timestamp'])
            if stamp.tzinfo is None or stamp.utcoffset() is None:
                raise ValueError('Czas musi zawierać offset strefy')
            utc = stamp.astimezone(timezone.utc)
            if utc in seen:
                raise ValueError('Powtórzona godzina')
            if any((stamp.minute, stamp.second, stamp.microsecond)):
                raise ValueError('Wymagana pełna godzina')
            if previous is not None and (utc - previous).total_seconds() != 3600:
                raise ValueError('Niesortowany czas lub luka w szeregu godzinowym')
            seen.add(utc)
            previous = utc
            rows.append({'timestamp': stamp.isoformat(), **check_pm(row), **check_weather(row)})
        except (ValueError, TypeError) as exc:
            raise ValueError(f'Wiersz {i}: {exc}') from exc
    return rows
