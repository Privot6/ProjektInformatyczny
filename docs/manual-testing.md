# Manualne wykonanie Lab 7

To instrukcja dla operatora, bez automatycznych asercji i zbiorczego runnera.
Oczekiwania są w [planie](tests.md). Każdy wynik trzeba przeczytać i zapisać
w dzienniku; samo wykonanie polecenia nie oznacza PASS. Do powtórnego wykonania
wybierz nowe nazwy raportów, aby zachować historię. Skrypty `measure_lab7.py`
i `quality_lab7.py` zbierają pomiary, nie oceniają przypadków testowych.

## Przygotowanie

Zainstaluj środowisko według sekcji LAB7 w README. Uruchamiaj polecenia
z katalogu głównego projektu. Ustaw `$env:PYTHONUTF8="1"`.
Nie używaj produkcyjnej bazy i nie zmieniaj `data/raw/`.

## M01–M04: dane, CLI i ochrona wyniku

```powershell
New-Item -ItemType Directory -Force results/lab7/repeat | Out-Null
Copy-Item data/raw/sample.json results/lab7/repeat/sample.json
.\.venv-lab7\Scripts\python.exe scripts/prepare_forecast.py --source results/lab7/repeat/sample.json --output results/lab7/repeat/prepared.json
Get-Content -Encoding utf8 results/lab7/repeat/prepared.json
Set-Content -Encoding utf8 results/lab7/repeat/protected.txt 'WYNIK KONTROLNY'
.\.venv-lab7\Scripts\python.exe scripts/prepare_forecast.py --source results/lab7/inputs/duplicate.json --output results/lab7/repeat/protected.txt
$LASTEXITCODE
Get-Content results/lab7/repeat/protected.txt
.\.venv-lab7\Scripts\python.exe scripts/prepare_forecast.py --source results/lab7/inputs/empty.json --output results/lab7/repeat/empty-result.json
$LASTEXITCODE
Test-Path results/lab7/repeat/empty-result.json
.\.venv-lab7\Scripts\python.exe scripts/prepare_forecast.py --source results/lab7/inputs/no-data.json --output results/lab7/repeat/no-data-result.json
$LASTEXITCODE
.\.venv-lab7\Scripts\python.exe scripts/prepare_forecast.py --source results/lab7/inputs/negative.json --output results/lab7/repeat/negative-result.json
$LASTEXITCODE
```

Sprawdź liczebności, jednostki, pierwszy lokalny znacznik 12.11 i PM10=31,59.
Każdy błędny plik powinien dać kod 1. Istniejący plik kontrolny po duplikacie
powinien nadal zawierać WYNIK KONTROLNY. Pliki wynikowe błędnych wejść nie
powinny powstać. Fixtures: `empty.json` to `{}`, `no-data.json` ma prawidłowe
metadane i puste tablice/PM10, `negative.json` ma PM10=−1 dla 12.11.

## M05–M11: pojedyncze operacje w konsoli

Uruchom `python -i scripts/manual_lab7.py` interpreterem `.venv-lab7`.
Konsola kopiuje próbkę do katalogu tymczasowego i tworzy osobną bazę.
`network` w zapisywanych JSON oznacza tu odpowiedzi odtworzone przez
`httpx.MockTransport`, a nie prawdziwe zapytania do dostawców. Kod aplikacji
`check`, walidacja, Ridge i SQLite są rzeczywiste.

Wpisuj kolejno, po każdym przypadku odczytując wynik:

```python
row = dict(pm10_daily_mean=20, temperature_2m=0, wind_speed_10m=5, precipitation=0)
training_score(row, 20)                         # M05: 81
classify(39), classify(40), classify(69), classify(70)  # M06
training_score(dict(row, pm10_daily_mean=112.5), 0)    # 39
training_score(dict(row, precipitation=4), 0)         # 39
len(timestamps(date(2026, 3, 29))), len(timestamps(date(2026, 10, 25)))  # M07: 23,25
result = show('2026-11-12', 'repeat-M08')
len(storage.read(state.db, '2026-11-12')[0])    # M08: 24
result['hours'][0]
mode = 'offline'
cached = show('2026-11-12', 'repeat-M09-cache')
```

Sprawdź w JSON pola, score, najkorzystniejszą godzinę oraz pochodzenie cache.
Następnie wykonaj M09 bez cache:

```python
from fastapi import HTTPException
try:
    show('2026-10-26', 'repeat-M09-no-cache')
except HTTPException as error:
    print(error.status_code, error.detail)

mode = 'archive'
missing = show('2026-11-14', 'repeat-M10-missing')
sample['open_meteo']['hourly']['temperature_2m'][23] = None
null_result = show('2026-11-12', 'repeat-M10-null')
null_result['hours'][0]
```

Brak PM10 wyklucza cały dzień z oceny, null jednej temperatury wyklucza tylko
tę godzinę. Opad 0 pozostaje zerem. Przed M11 odtwórz próbkę w pamięci,
ale pozostaw poprzedni niepełny zapis w bazie, aby wykazać rollback:

```python
sample = json.loads((work / 'sample.json').read_text(encoding='utf-8'))
import sqlite3
before, captures_before = storage.read(state.db, '2026-11-12')
db = sqlite3.connect(state.db)
db.execute("CREATE TRIGGER reject_hour BEFORE INSERT ON forecast_hour BEGIN SELECT RAISE(ABORT,'manual-write-failure'); END")
db.close()
rollback = show('2026-11-12', 'repeat-M11')
after, captures_after = storage.read(state.db, '2026-11-12')
print(list(before.values()))
print(list(after.values()))
print(captures_before, captures_after)
```

Porównaj ręcznie wszystkie rekordy i czasy źródeł: powinny być zachowane,
łącznie z null pierwszej temperatury; świeży wynik ma temperaturę 4,5°C
i ostrzeżenie zapisu. Wykonany dowód jest w `M11-storage.json`.
Na końcu konsoli wpisz `client.close()`, `temporary.cleanup()` i `exit()`.

## M12: prawdziwy HTTP

W osobnym terminalu wskaż nową bazę:

```powershell
$env:AERORUN_DB=Join-Path $env:TEMP 'aerorun-manual-http.sqlite3'
.\.venv-lab7\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8768
```

Otwórz `http://127.0.0.1:8768/docs` i wykonaj GET `/forecast/invalid` lub
wyślij to żądanie z terminala/Postmana. Oczekuj HTTP 422 oraz wskazania
dozwolonych `today`/`tomorrow`. Ten przypadek nie wysyła żądań do dostawców.
Zatrzymaj serwer Ctrl+C po kontroli. Podczas wykonania Lab 7 ograniczenia
sandboxa wymagały uruchomienia serwera i klienta z dostępem do lokalnych gniazd.

## M13, M16 oraz pomiary

```powershell
.\.venv-lab7\Scripts\python.exe scripts/compare_scoring_methods.py --output results/lab7/repeat/scoring
.\.venv-lab7\Scripts\python.exe scripts/compare_methods.py --output results/lab7/repeat/pm10-daily
.\.venv-lab7\Scripts\python.exe scripts/quality_lab7.py
.\.venv-lab7\Scripts\python.exe scripts/measure_lab7.py
```

Dwa ostatnie skrypty zapisują bieżący pomiar w stałych nazwach w `results/lab7`;
przed powtórzeniem skopiuj poprzednie wyniki do osobnego katalogu.
Porównaj MAE i opisy pochodzenia ocen z planem. Oblicz medianę pięciu czasów
i odnieś ją do 2 s; skrypt pomiarowy nie nadaje statusu PASS/FAIL.
Przeliczenie MAE jest pomiarem analitycznym, a nie uruchomieniem testów.

## M14–M15: odbiór przez zespół

Inna osoba pobiera projekt do nowego katalogu, przygotowuje Pythona 3.12
i środowisko według README, wykonuje kroki użytkownika offline: poprawny
przypadek M01 i błąd M03. Następnie uruchamia Androida, zmienia DZISIAJ/JUTRO,
rozwija karty i sprawdza jednostki, wyłącza backend, naciska SPRAWDŹ i ocenia
komunikat oraz brak poprzedniego wyniku. Zapisuje imię, datę, commit, urządzenie,
kroki, pierwszy brak instrukcji, wynik oraz wynik powtórzenia po poprawce.
Recenzję zmienionego fragmentu należy opublikować w rzeczywistym PR i podać URL.
