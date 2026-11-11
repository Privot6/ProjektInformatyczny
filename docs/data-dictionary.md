# Słownik danych

## Surowa próbka prognoz

Plik [data/raw/sample.json](../data/raw/sample.json).

| Pole | Znaczenie | Typ | Jednostka / format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| `metadata.city` | Miasto, którego dotyczy próbka | tekst | — | Rzeszów | nie |
| `metadata.teryt` | Identyfikator miasta w zapytaniu o PM10 | tekst | 4 cyfry | `1863` | nie |
| `ios_pib_pm10` | Mapa dat i średnich dobowych PM10. Klucze zawierają datę bez strefy czasowej. | obiekt: tekst → liczba | klucz `YYYYMMDD`, wartość w µg/m³ | `"20261112": 31.59` | wartość może być `null`, data może być nieobecna |
| `open_meteo.timezone` | Strefa znaczników czasu w odpowiedzi | tekst | GMT lub UTC | `GMT` | nie |
| `open_meteo.utc_offset_seconds` | Przesunięcie czasu źródłowego względem UTC | liczba całkowita | sekundy | `0` | nie |
| `open_meteo.hourly_units` | Format dat i jednostki godzinowych wartości | obiekt | ISO 8601, °C, mm, km/h | `"wind_speed_10m": "km/h"` | nie |
| `open_meteo.hourly.time` | Pełne godziny prognozy w GMT/UTC | tablica tekstów | `YYYY-MM-DDTHH:mm` | `2026-11-11T00:00` | nie |
| `open_meteo.hourly.temperature_2m` | Temperatura powietrza na wysokości 2 m dla danej godziny | tablica liczb | °C | `5.2` | element może być `null` |
| `open_meteo.hourly.precipitation` | Suma opadów z godziny poprzedzającej znacznik czasu | tablica liczb | mm | `0.0` | element może być `null` |
| `open_meteo.hourly.wind_speed_10m` | Prędkość wiatru na wysokości 10 m dla danej godziny | tablica liczb | km/h | `17.3` | element może być `null` |

Cztery tablice godzinowe mają ten sam indeks. Metadane `metadata.sources` opisują pochodzenie próbki. `publisher` i `content_type` to tekst, `url` to pełny adres GET, `retrieved_at_utc` to czas pobrania w ISO 8601 UTC, a `http_status` to liczbowy kod odpowiedzi.

## Wynik Lab 3

Plik [data/processed/sample-clean.json](../data/processed/sample-clean.json).

| Pole | Znaczenie | Typ | Jednostka / format | Przykładowa wartość | Czy może być puste? |
|---|---|---|---|---|---|
| `city` | Miasto z metadanych źródłowych | tekst | — | Rzeszów | nie |
| `teryt` | Identyfikator miasta z metadanych źródłowych | tekst | 4 cyfry | `1863` | nie |
| `timezone` | Strefa dat i godzin wyniku | tekst | nazwa IANA | `Europe/Warsaw` | nie |
| `units` | Jednostki czterech wielkości | obiekt | µg/m³, °C, mm, km/h | `"pm10_daily_mean": "µg/m³"` | nie |
| `days` | Daty lokalne obecne w co najmniej jednym źródle, rosnąco | tablica obiektów | — | rekord z datą `2026-11-12` | nie |
| `days[].date` | Lokalna data grupowania | tekst | ISO 8601, `YYYY-MM-DD` | `2026-11-12` | nie |
| `days[].pm10_daily_mean` | Średnia dobowa PM10 dla Rzeszowa | liczba lub `null` | µg/m³ | `31.59` | tak, gdy brakuje prognozy dla daty |
| `days[].missing_weather_hours` | Liczba godzin lokalnej doby pomniejszona o liczbę godzin z kompletem trzech pól pogodowych. Uwzględnia zmianę czasu. | liczba całkowita | godziny | `1` | nie |
| `days[].weather` | Godziny pogody w kolejności czasu, dla wskazanej daty | tablica obiektów | — | 24 rekordy dla `2026-11-12` | może być pusta |
| `days[].weather[].timestamp` | Pełna godzina po konwersji z GMT/UTC do czasu Rzeszowa | tekst | ISO 8601 z offsetem | `2026-11-11T01:00+01:00` | nie |
| `days[].weather[].temperature_2m` | Temperatura na 2 m przejęta z prognozy | liczba lub `null` | °C | `5.2` | tak, jeśli brakuje wartości w źródle |
| `days[].weather[].precipitation` | Suma opadów za poprzednią godzinę przejęta z prognozy | liczba lub `null` | mm | `0.0` | tak, jeśli brakuje wartości w źródle |
| `days[].weather[].wind_speed_10m` | Prędkość wiatru na 10 m przejęta z prognozy | liczba lub `null` | km/h | `17.3` | tak, jeśli brakuje wartości w źródle |

## Dane historyczne do eksperymentu Lab 4

Dotyczy: `data/raw/open_meteo_pogoda.csv`, `data/raw/gios_pomiary.csv` i `data/processed/aerorun_dane.csv`.

| Pole | Znaczenie | Typ | Jednostka / format | Przykład | Czy może być puste? |
|---|---|---|---|---|---|
| timestamp | Godzina pomiaru GIOŚ lub reanalizy pogody, klucz integracji | datetime / tekst CSV | ISO 8601 z offsetem; wynik Europe/Warsaw | 2026-10-20T00:00:00+02:00 | nie |
| pm25 | Stężenie pyłu PM2.5 (wejście GIOŚ) | FLOAT | µg/m³ | 9.2 | tak w surowych, nie w wyniku |
| pm10 | Stężenie pyłu PM10 (wejście GIOŚ) | FLOAT | µg/m³ | 11.9 | tak w surowych, nie w wyniku |
| temperature_2m | Temperatura powietrza na wysokości 2 m | FLOAT | °C | 8.0 | tak w surowych, nie w wyniku |
| wind_speed_10m | Prędkość wiatru na wysokości 10 m | FLOAT | km/h (domyślne API) | 8.0 | tak w surowych, nie w wyniku |
| precipitation | Opad godzinowy | FLOAT | mm | 0.0 | tak w surowych, nie w wyniku |

W wyniku zachowano nazwy i jednostki pól wejściowych; `timestamp` jest ujednolicony do strefy `Europe/Warsaw`, a braki w krótkich odcinkach są interpolowane. Nie tworzono wskaźników pochodnych — należą do innej części projektu. Surowa odpowiedź API zawiera dodatkowe metadane i jednostki w `hourly_units`, które należy zweryfikować dla danego żądania.
