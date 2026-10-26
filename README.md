# AeroRun — Laboratorium 3, część Kacpra Dąbka

**Zakres:** Open-Meteo, synchronizacja godzin, czyszczenie, integracja z przygotowaną tabelą GIOŚ i kontrola jakości. Nie obejmuje regresji ani dashboardu.

## Uruchomienie (Python 3.10+)
Z katalogu głównego projektu:
```bash
python -m pip install -r requirements.txt
python scripts/prepare_data.py
python -m unittest discover -s tests -v
```
Wynik: `data/processed/aerorun_dane.csv` i `.json`.

**Tryb offline:** dołączone próbki GIOŚ i Open-Meteo są **syntetyczne** i mają wyłącznie pokazać powtarzalność procedury. Nie wolno przedstawiać ich jako rzeczywistych pomiarów. `data/raw/` pozostaje nietknięte przez procedurę.

**Tryb rzeczywisty (wymaga internetu):**
```bash
python scripts/pobierz_open_meteo.py --lat 50.0413 --lon 21.9990
```
Zapisuje niezmienioną odpowiedź HTTP w JSON i tabelę CSV. Skrypt żąda danych w UTC i zapisuje CSV z jednoznacznym offsetem Europe/Warsaw, również przy zmianie czasu. Do integracji z rzeczywistymi PM wymagany jest plik CSV Dawida (`timestamp,pm25,pm10`), zgodny czasowo i przestrzennie. Skrypt integracyjny `integracja.py` może też sam pobrać pogodę dla danych GIOŚ: `python integracja.py --gios sciezka_do_gios.csv`.

**Test błędnych danych:** `python scripts/prepare_data.py --weather data/test/open_meteo_bledne.csv --output data/test/wynik_bledny` powinien zakończyć się błędem i nie zapisać wyniku.

Dokumentacja: `docs/data.md`, `docs/data-dictionary.md`, `docs/processing.md`.
