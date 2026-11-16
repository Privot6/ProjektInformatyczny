from datetime import datetime, time, timedelta, timezone
from email.utils import parsedate_to_datetime

from backend.model import ZONE
from scripts.prepare_forecast import WEATHER_UNITS, read_pm10, read_weather

PM10_URL = "https://api.prognozy.ios.edu.pl/v1/PM10/1863/"
WEATHER = "https://api.open-meteo.com/v1/forecast"


def retry_at(response, now):
    value = response.headers.get("Retry-After", "")
    if value.isascii() and value.isdigit():
        return now + timedelta(seconds=min(int(value[:10]), 2147483647))
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return now
    return parsed if parsed.tzinfo else now


def timestamps(day):
    def midnight(d):
        return int(datetime.combine(d, time.min, ZONE).timestamp())
    return range(midnight(day), midnight(day + timedelta(days=1)), 3600)


def fetch(client, source, day):
    hours = timestamps(day)
    if source == "ios_pib_pm10":
        response = client.get(PM10_URL)
        response.raise_for_status()
        daily_mean = read_pm10(response.json()).get(day)
        return {t: {"pm10_daily_mean": daily_mean} for t in hours}
    dates = [datetime.fromtimestamp(t, timezone.utc).date().isoformat() for t in (hours[0], hours[-1])]
    response = client.get(WEATHER, params={"latitude": 50.0413, "longitude": 21.999,
                          "start_date": dates[0], "end_date": dates[1], "timezone": "GMT",
                          "hourly": ",".join(WEATHER_UNITS)})
    response.raise_for_status()
    rows = read_weather(response.json(), ZONE).get(day, [])
    result = {int(datetime.fromisoformat(r["timestamp"]).timestamp()): {f: r[f] for f in WEATHER_UNITS}
              for r in rows}
    if len(result) != len(rows):
        raise ValueError("Powtórzona godzina pogody")
    return result
