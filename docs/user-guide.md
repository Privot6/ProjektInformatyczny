# Instrukcja użytkownika

## 1. Wymagane dane wejściowe

AeroRun dotyczy Rzeszowa. Na telefonie wybierz DZISIAJ albo JUTRO; aplikacja
sama pobiera prognozę. Backend musi działać według [README](../README.md).
Telefon/emulator potrzebuje połączenia z backendem, a backend z dostawcami
prognoz lub wcześniejszego zapisu wybranego dnia.

Prognoza PM10 ma jedną średnią dobową w µg/m³, nieujemną. Pogoda obejmuje
temperaturę od −90 do 60°C, nieujemne opady w mm i wiatr w km/h, co godzinę.
Zero opadów oznacza brak opadu; brak danych nie oznacza zera. Czas jest lokalny,
Europe/Warsaw. Doby zmiany czasu mają 23 albo 25 godzin.

Wariant offline do ćwiczenia bez telefonu używa kopii publicznej próbki JSON:
metadane Rzeszów/1863, `ios_pib_pm10` z datami `YYYYMMDD`, `open_meteo`
z jednostkami i równoległymi tablicami czasu UTC oraz trzech pól pogody.
Nie wprowadzaj własnych danych do `data/raw/`; pracuj w katalogu wynikowym.

## 2. Wykonanie operacji krok po kroku

1. Uruchom backend i aplikację Android zgodnie z README.
2. Wybierz DZISIAJ lub JUTRO i naciśnij SPRAWDŹ. W czasie pobierania przycisk
   oraz zmiana dnia są nieaktywne.
3. Odczytaj wynik 0–100 i etykietę przy wybranej godzinie.
4. Dotknij karty godziny, aby rozwinąć PM10, temperaturę, wiatr i opady.
   Ponowne dotknięcie zwija szczegóły. Porównaj kilka godzin.
5. Po zmianie dnia naciśnij ponownie SPRAWDŹ; poprzedni wynik jest usuwany.

Bez telefonu możesz przećwiczyć przygotowanie danych z katalogu projektu:

```powershell
$env:PYTHONUTF8="1"
New-Item -ItemType Directory -Force results/lab7/user-run | Out-Null
Copy-Item data/raw/sample.json results/lab7/user-run/sample.json
.\.venv-lab7\Scripts\python.exe scripts/prepare_forecast.py --source results/lab7/user-run/sample.json --output results/lab7/user-run/prepared.json
Get-Content -Encoding utf8 results/lab7/user-run/prepared.json
```

Oczekuj 8 dat, 168 godzin pogody i 3 wartości PM10. W dniu 12.11.2026 są
24 godziny i PM10=31,59 µg/m³. Ten wariant pokazuje integrację danych,
ale nie pokazuje kart telefonu. Punktację offline można odczytać poleceniem
`result = show('2026-11-12', 'user-result')` w [konsoli manualnej](manual-testing.md).
To archiwalna data, nie prognoza na bieżący dzień.

## 3. Interpretacja wyniku

70–100 pkt oznacza TRENUJ, 40–69 OGRANICZ, 0–39 NIE TRENUJ na telefonie
(`ZOSTAŃ W DOMU` w API). Szare BRAK DANYCH oznacza niewystarczające dane do
oceny danej godziny. Etykieta OGRANICZ odpowiada ograniczeniu wysiłku z R5.

Score łączy oszacowanie godzinowego PM10 przez Ridge (35%) z oceną temperatury
(25%), wiatru (25%) i opadów (15%). Średnia dobowa PM10 pokazywana w szczegółach
jest wspólna dla godzin tego dnia. Nie jest pomiarem stężenia w konkretnej
godzinie ani na Twojej trasie. Większy score oznacza korzystniejszą ocenę
według reguł projektu. Najwyższy wynik może dotyczyć godziny, która już minęła.


## 4. Komunikaty błędów i sposób postępowania

| Komunikat / sytuacja | Co zrobić |
|---|---|
| BRAK DANYCH, kreska zamiast score | Nie traktuj wyniku jako 0; spróbuj innej godziny/dnia lub ponów później. |
| Brak połączenia z FastAPI | Sprawdź uruchomienie backendu, adres i przekierowanie USB z README; ponów SPRAWDŹ. |
| Źródła są niedostępne. Brak zapisu dla tego dnia. | Oba źródła zawiodły, a cache nie ma tego dnia; ponów później. API zwraca 503. |
| Dane zapisane wcześniej | Backend użył cache. Ekran nie pokazuje jeszcze czasu źródeł; sprawdź `retrieved_at_utc` w Swaggerze lub poczekaj na poprawne odświeżenie. |
| HTTP 422 w Swaggerze | Użyj dokładnie `/forecast/today` lub `/forecast/tomorrow`; dowolna data w URL nie jest obsługiwana. |
| Powtórzony timestamp / niepoprawna wartość / brak wspólnej daty w CLI | Popraw kopię wejścia; wynik nie jest zapisywany po błędzie walidacji. |
| `'metadata'` w komunikacie CLI | Plik jest pusty lub nie ma wymaganego schematu; użyj kopii sample.json. |
| Błąd kodowania konsoli Windows | Ustaw `$env:PYTHONUTF8="1"` i ponów polecenie. |

API zwraca również `warnings` o nieudanym pobraniu/zapisie i `pm10_notice`.
Obecny ekran telefonu ich nie wyświetla; to [otwarte zadanie](issues/lab7-review.md).
Przy błędzie zapisu backend nadal może zwrócić świeży wynik, ale nie gwarantuje
jego późniejszej dostępności offline.
