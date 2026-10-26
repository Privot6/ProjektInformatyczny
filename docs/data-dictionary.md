# Słownik danych

Dotyczy: `data/raw/open_meteo_syntetyczne.csv`, `data/raw/gios_syntetyczne.csv` i `data/processed/aerorun_dane.csv`.

| Pole | Znaczenie | Typ | Jednostka / format | Przykład | Czy może być puste? |
|---|---|---|---|---|---|
| timestamp | Godzina pomiaru/prognozy, klucz integracji | datetime / tekst CSV | ISO 8601 z offsetem; wynik Europe/Warsaw | 2026-10-20T00:00:00+02:00 | nie |
| pm25 | Stężenie pyłu PM2.5 (wejście GIOŚ) | FLOAT | µg/m³ | 15.0 | tak w surowych, nie w wyniku |
| pm10 | Stężenie pyłu PM10 (wejście GIOŚ) | FLOAT | µg/m³ | 32.0 | tak w surowych, nie w wyniku |
| temperature_2m | Temperatura powietrza na wysokości 2 m | FLOAT | °C | 7.0 | tak w surowych, nie w wyniku |
| wind_speed_10m | Prędkość wiatru na wysokości 10 m | FLOAT | km/h (domyślne API) | 13.0 | tak w surowych, nie w wyniku |
| precipitation | Opad godzinowy | FLOAT | mm | 0.4 | tak w surowych, nie w wyniku |

W wyniku zachowano nazwy i jednostki pól wejściowych; `timestamp` jest ujednolicony do strefy `Europe/Warsaw`, a braki w krótkich odcinkach są interpolowane. Nie tworzono wskaźników pochodnych — należą do innej części projektu. Surowa odpowiedź API zawiera dodatkowe metadane i jednostki w `hourly_units`, które należy zweryfikować dla danego żądania.
