# Model danych i zapis przebiegu

## Pliki w repozytorium

| Plik | Zawartość |
|---|---|
| `data/raw/sample.json` | Odpowiedzi prognoz dla Rzeszowa i ich metadane. |
| `data/processed/sample-clean.json` | Lokalne daty, jedna prognoza PM10 na dobę, godziny pogody. [Słownik](../data-dictionary.md). |
| `data/raw/lab4/gios.json`, `weather.json`, `sources.json` | Pomiary PM10, archiwalna pogoda oraz dokładne adresy i SHA-256. |
| `results/lab4/observations.csv` | Jeden wiersz na datę testową. Trzy dobowe cechy, pomiar PM10, estymaty i błędy bezwzględne obu metod. |
| `results/lab4/comparison.csv` | Jeden wiersz na metodę z liczebnością treningu i testu oraz MAE w µg/m³. |
| `results/lab4/lab3_application.csv` | Jedna kompletna doba Lab 3 na wiersz. Cechy, prognoza IOŚ-PIB i dwie estymaty. |
| `results/lab4/run.json` | Źródła, hashe, daty uczenia, testu i pominięć, parametry i diagnostyka. |
| `results/lab4/sensitivity/` | Ten sam schemat z limitem głębokości drzewa 4. |

Data w CSV ma format ISO 8601 `YYYY-MM-DD` w strefie `Europe/Warsaw`. Temperatura jest w °C, wiatr w km/h, suma opadów w mm, a pomiar, estymaty i MAE w µg/m³. Kluczem obserwacji jest data w scenariuszu. Kluczem agregacji jest metoda w scenariuszu.

## Planowana historia przebiegów

Każdy katalog `results/runs/<run_id>/` ma zawierać wersję wejścia Lab 3, manifest źródeł, parametry oraz komplety plików obu scenariuszy. Manifest ma zapisać `run_id`, `schema_version`, `created_at_utc`, `status`, wersję kodu i hashe plików. Publikacja obejmuje cały katalog po kontroli spójności. Starszy przebieg pozostaje dostępny. [ADR-001](../decisions/001-storage.md) · [Kontrakt](contracts.md)
