import json
import urllib.request

# 1. Pobranie danych z Open-Meteo (ostatnie 2 dni + 1 dzień prognozy = 72 rekordy godzinowe)
meteo_url = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude=50.0811&longitude=19.8953"
    "&hourly=temperature_2m,wind_speed_10m,precipitation"
    "&past_days=2&forecast_days=1&timezone=Europe%2FWarsaw"
)
with urllib.request.urlopen(meteo_url) as resp:
    meteo_data = json.loads(resp.read().decode("utf-8"))

# 2. Pobranie danych z GIOŚ dla przykładowego czujnika (np. sensorId=2750)
gios_url = "https://api.gios.gov.pl/pjp-api/rest/data/getData/2750"
with urllib.request.urlopen(gios_url) as resp:
    gios_data = json.loads(resp.read().decode("utf-8"))

# 3. Zapisanie połączonej próbki do data/sample.json
with open("data/sample.json", "w", encoding="utf-8") as f:
    json.dump({"gios": gios_data, "open_meteo": meteo_data}, f, ensure_ascii=False, indent=2)

print("Pobrano i zapisano próbkę do data/sample.json")
