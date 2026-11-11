"""Przygotuj dobowe PM10 i godzinową prognozę pogody z próbki Lab 2."""

import argparse
import json
import math
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


WEATHER_UNITS = {
    "temperature_2m": "°C",
    "precipitation": "mm",
    "wind_speed_10m": "km/h",
}
LOCAL_TIMEZONE = "Europe/Warsaw"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Powtórzony klucz JSON: {key}")
        result[key] = value
    return result


def check_number(value, field, minimum, maximum=math.inf):
    if value is None:
        return
    if type(value) not in (int, float) or not minimum <= value <= maximum or not math.isfinite(value):
        raise ValueError(f"Niepoprawna wartość pola {field}: {value!r}")


def read_pm10(values):
    if not isinstance(values, dict):
        raise ValueError("Oczekiwano obiektu z prognozą dobową PM10")
    daily = {}
    for key, value in values.items():
        day = datetime.strptime(key, "%Y%m%d").date()
        if day.strftime("%Y%m%d") != key:
            raise ValueError(f"Niepoprawny format daty PM10: {key!r}")
        check_number(value, "pm10_daily_mean", 0)
        daily[day] = value
    return daily


def read_weather(payload, local_zone):
    if payload["utc_offset_seconds"] != 0 or payload["timezone"] not in ("GMT", "UTC"):
        raise ValueError("Oczekiwano prognozy Open-Meteo w GMT lub UTC")
    expected_units = {"time": "iso8601", **WEATHER_UNITS}
    units = payload["hourly_units"]
    if not isinstance(units, dict) or any(units.get(field) != unit for field, unit in expected_units.items()):
        raise ValueError("Niezgodne jednostki lub format czasu Open-Meteo")

    hourly = payload["hourly"]
    series = [hourly[field] for field in expected_units]
    if any(not isinstance(values, list) for values in series):
        raise ValueError("Pola godzinowe Open-Meteo muszą być tablicami")
    if len({len(values) for values in series}) != 1:
        raise ValueError("Tablice godzinowe Open-Meteo mają różne długości")

    weather = defaultdict(list)
    for stamp, temperature, precipitation, wind in zip(*series):
        parsed = datetime.strptime(stamp, "%Y-%m-%dT%H:%M")
        if parsed.isoformat(timespec="minutes") != stamp or parsed.minute != 0:
            raise ValueError(f"Oczekiwano pełnej godziny w formacie ISO 8601: {stamp!r}")
        check_number(temperature, "temperature_2m", -90, 60)
        check_number(precipitation, "precipitation", 0)
        check_number(wind, "wind_speed_10m", 0)
        local = parsed.replace(tzinfo=timezone.utc).astimezone(local_zone)
        weather[local.date()].append({
            "timestamp": local.isoformat(timespec="minutes"),
            "temperature_2m": temperature,
            "precipitation": precipitation,
            "wind_speed_10m": wind,
        })
    return weather


def missing_weather_hours(day, hours, local_zone):
    start = datetime.combine(day, time.min, local_zone).astimezone(timezone.utc)
    end = datetime.combine(day + timedelta(days=1), time.min, local_zone).astimezone(timezone.utc)
    expected = (end - start) // timedelta(hours=1)
    complete = sum(all(row[field] is not None for field in WEATHER_UNITS) for row in hours)
    return expected - complete


def prepare(source, output):
    if source.resolve() == output.resolve():
        raise ValueError("Próbka źródłowa i plik wyniku muszą mieć różne ścieżki")
    sample = json.loads(source.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    metadata = sample["metadata"]
    if (metadata["city"], metadata["teryt"]) != ("Rzeszów", "1863"):
        raise ValueError("Oczekiwano danych dla Rzeszowa (TERYT 1863)")

    local_zone = ZoneInfo(LOCAL_TIMEZONE)
    pm10 = read_pm10(sample["ios_pib_pm10"])
    weather = read_weather(sample["open_meteo"], local_zone)
    if not pm10.keys() & weather.keys():
        raise ValueError("Brak wspólnej daty PM10 i prognozy pogody")

    days = []
    for day in sorted(pm10.keys() | weather.keys()):
        hours = sorted(weather.get(day, []), key=lambda row: datetime.fromisoformat(
            row["timestamp"]
        ).astimezone(timezone.utc))
        days.append({
            "date": day.isoformat(),
            "pm10_daily_mean": pm10.get(day),
            "missing_weather_hours": missing_weather_hours(day, hours, local_zone),
            "weather": hours,
        })

    # Sprawdź zachowanie liczby rekordów i zgodność kluczy po transformacji.
    result_hours = sum(len(day["weather"]) for day in days)
    result_pm10 = sum(day["pm10_daily_mean"] is not None for day in days)
    if result_hours != len(sample["open_meteo"]["hourly"]["time"]):
        raise ValueError("Zmieniła się liczba godzin pogody po integracji")
    if result_pm10 != sum(value is not None for value in pm10.values()):
        raise ValueError("Zmieniła się liczba dostępnych prognoz PM10 po integracji")
    for day in days:
        local_date = date.fromisoformat(day["date"])
        seen = set()
        for row in day["weather"]:
            stamp = row["timestamp"]
            if stamp in seen:
                raise ValueError(f"Powtórzony timestamp Open-Meteo po konwersji: {stamp}")
            seen.add(stamp)
            if datetime.fromisoformat(stamp).date() != local_date:
                raise ValueError(f"Godzina pogody przypisana do niewłaściwej daty: {stamp}")
        if day["missing_weather_hours"] < 0:
            raise ValueError(f"Nadmiar godzin pogody dla {day['date']}")

    result = {
        "city": metadata["city"],
        "teryt": metadata["teryt"],
        "timezone": LOCAL_TIMEZONE,
        "units": {"pm10_daily_mean": "µg/m³", **WEATHER_UNITS},
        "days": days,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=output.parent,
                                delete=False) as file:
            temporary = Path(file.name)
            json.dump(result, file, ensure_ascii=False, indent=2, allow_nan=False)
            file.write("\n")
        temporary.replace(output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return len(days), result_pm10, result_hours


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("data/raw/sample.json"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/sample-clean.json"))
    args = parser.parse_args()
    try:
        days, pm10, hours = prepare(args.source, args.output)
    except ZoneInfoNotFoundError:
        parser.exit(1, "Błąd: brak danych stref czasowych. Zainstaluj pakiet tzdata.\n")
    except (OSError, KeyError, TypeError, ValueError) as error:
        parser.exit(1, f"Błąd danych Lab 3: {error}\n")
    print(f"Zapisano {args.output} | dni: {days}, wartości PM10: {pm10}, godziny pogody: {hours}")


if __name__ == "__main__":
    main()
