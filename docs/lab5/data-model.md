# Model danych AeroRun

Model dotyczy plików, bez relacyjnej bazy danych. Podstawą jest próbka Lab 3–4:
72 godziny z 20–22 października 2026, stacja GIOŚ 10125 PkRzeszPilsu w Rzeszowie.
PM2.5: stanowisko 20277; PM10: 16344. Pogoda: Open-Meteo ERA5 dla współrzędnych
50.040675 N, 22.004656 E; zwrócona komórka modelu 50.0 N, 22.0 E.
Odpowiedzi pobrano 7 listopada 2026. Pogoda jest reanalizą, nie pomiarem punktowym.

## Model logiczny

| Obiekt | Jeden rekord i identyfikator | Powiązanie |
|---|---|---|
| SourceSnapshot | Zestaw odpowiedzi i metadanych; planowany source_version = SHA-256 pliku provenance.json | Jedna wersja źródła może służyć wielu integracjom |
| InputSnapshot | Jeden niezmienny CSV; input_sha256 = SHA-256 dokładnych bajtów | Zawiera godziny; może być użyty w wielu uruchomieniach |
| HourMeasurement | Jedna godzina z jednej stacji; klucz timestamp po przeliczeniu na UTC, w obrębie InputSnapshot | Te same pomiary są wejściem obu metod |
| ConfigSnapshot | Jeden JSON parametrów; config_sha256 = SHA-256 dokładnych bajtów | Używany przez jedno lub wiele uruchomień |
| AnalysisRun | Jedno pełne porównanie, planowany run_id UUID | Wskazuje dokładnie jedno wejście, konfigurację i wersję źródła |
| Observation | Wynik jednej metody dla jednej godziny; klucz run_id, scenario, timestamp, wariant | Wskazuje godzinę wejściową; wynik perturbacji jest w tym samym wierszu |
| Comparison | Agregacja metody w scenariuszu; klucz run_id, scenario, wariant | Powstaje z obserwacji jednego uruchomienia |

Obecnie scenariusz wynika z katalogu, a run_id jeszcze nie istnieje.
Nie są to kolumny observations.csv.
W planowanym zapisie run_id jest nazwą katalogu i polem manifestu, a scenario
wynika z katalogu głównego albo sensitivity/. Nie trzeba zmieniać kolumn Lab 4.

## Istniejący zapis fizyczny

| Ścieżka | Format i zawartość |
|---|---|
| data/raw/gios_pm25.json, gios_pm10.json | Niezmienione odpowiedzi GIOŚ; lista wyników zawiera Kod stanowiska, Data i Wartość |
| data/raw/gios_stacje.json, gios_stanowiska.json | Niezmienione metadane stacji i stanowisk |
| data/raw/open_meteo_archiwum.json | Niezmieniona odpowiedź: hourly.time, temperature_2m, wind_speed_10m, precipitation i hourly_units |
| data/raw/provenance.json | station, sensor_ids, source_kind, współrzędne, selected_start, selected_end, n, time_conversion, sources z URL i SHA-256, normalized_csv_sha256 i attribution |
| data/raw/gios_pomiary.csv | timestamp, pm25, pm10 |
| data/raw/open_meteo_pogoda.csv | timestamp, temperature_2m, wind_speed_10m, precipitation |
| data/processed/aerorun_dane.csv | Sześć pól wspólnego wejścia; schemat niżej |
| data/processed/aerorun_dane.json | Ten sam zestaw pól; format pomocniczy, nie wejście load_data |
| config/lab4.json | version, skale PM, temperature_center, anchors, caps, labels, perturbation_pm25, sensitivity_pm25_scale, practical_relative_reduction, note |
| results/lab4/observations.csv | Szczegółowe wyniki, po dwa wiersze na godzinę |
| results/lab4/comparison.csv | Dwa wiersze: bazowy i rozmyty |
| results/lab4/control_checks.csv | Kontrolne przypadki wysokiego PM; nie są pomiarami ze stacji |
| results/lab4/run.json | input_sha256, pełny config, relative_reduction, practical_criterion_met, metric_meaning, data_kind, randomness |
| results/lab4/sensitivity/ | Te same cztery pliki dla zmienionej skali PM2.5 |

Raporty input_audit.json, input_pm_audit.json, pm_results_check.json oraz
reproducibility.json opisują kontrolę jakości i odtworzenie. Nie są danymi
uczącymi ani niezależnymi etykietami poprawności rekomendacji.

## Schemat wejścia

CSV jest kodowany w UTF-8, dopuszczalny BOM, separator przecinek, kropka dziesiętna.

| Pole | Typ logiczny | Jednostka i warunek |
|---|---|---|
| timestamp | tekst ISO 8601 z offsetem | Pełna godzina; unikatowa i uporządkowana, odstęp 3600 s w UTC |
| pm25 | float64 | µg/m³, skończone >= 0 |
| pm10 | float64 | µg/m³, skończone >= 0 |
| temperature_2m | float64 | °C, skończone, od -90 do 60 w istniejącej kontroli |
| wind_speed_10m | float64 | km/h, skończone >= 0 |
| precipitation | float64 | mm sumy godzinowej, skończone >= 0 |

Po przetworzeniu żadne z tych pól nie może być puste. PM2.5 > PM10 jest flagą
do przeglądu, nie automatycznym powodem usunięcia rekordu. Archiwum GIOŚ używa
stałego CET (UTC+01:00); ERA5 pobrano w UTC. CSV po normalizacji używa
Europe/Warsaw. Przy zmianie czasu dwie lokalne godziny z różnym offsetem są
różnymi obserwacjami. Dane aktualnej próbki są kompletne i nie były interpolowane.

## Schemat wyników

observations.csv zawiera wszystkie sześć pól wejściowych oraz:

| Pole | Typ | Znaczenie |
|---|---|---|
| wariant | enum tekstowy | bazowy lub rozmyty |
| score | float64 | Indeks w punktach 0–100 dla oryginalnego wejścia |
| label | enum tekstowy | TRENUJ, OGRANICZ WYSIŁEK lub ZOSTAŃ W DOMU |
| pm25_perturbed | float64 | µg/m³; pm25 + perturbation_pm25 |
| score_perturbed | float64 | Indeks po perturbacji, punkty 0–100 |
| label_perturbed | enum tekstowy | Etykieta po perturbacji |
| absolute_score_change | float64 | abs(score_perturbed - score), punkty |
| label_changed | integer | 0 albo 1 |
| r_bad, r_middle, r_good | float64 lub puste | Aktywacje 0–1 dla modelu rozmytego; puste wyłącznie dla bazowego |

Puste aktywacje w bazowym nie oznaczają braku danych pomiarowych. W próbce są
144 wiersze na scenariusz, 72 na metodę. Nie są to 144 niezależne pomiary.

comparison.csv: wariant jako enum; n jako dodatnia liczba całkowita;
mean_abs_score_change_points, min_change_points, max_change_points jako skończone
float64 w punktach; label_changes oraz no_train_failures jako nieujemne liczby
całkowite. n dotyczy godzin metody, nie liczby przypadków kontrolnych.
relative_reduction w run.json jest liczbą lub null, jeżeli średnia baseline=0.

## Planowany zapis uruchomień

| Ścieżka | Stan i przeznaczenie |
|---|---|
| data/raw/snapshots/<source_version>/ | Planowane niezmienne odpowiedzi źródeł oraz provenance.json |
| results/runs/.partial/<run_id>/ | Planowany katalog roboczy, niewidoczny dla dashboardu |
| results/runs/<run_id>/input.csv | Kopia dokładnych bajtów ocenianego wejścia |
| results/runs/<run_id>/config.json | Kopia dokładnych bajtów konfiguracji podstawowej |
| results/runs/<run_id>/provenance.json | Kopia metadanych wskazująca niezmienny snapshot źródła |
| results/runs/<run_id>/observations.csv, comparison.csv, control_checks.csv, run.json | Istniejące schematy Lab 4 dla scenariusza podstawowego |
| results/runs/<run_id>/sensitivity/ | Istniejące schematy dla próby wrażliwości |
| results/runs/<run_id>/manifest.json | Planowane metadane kompletnego uruchomienia |

Planowany manifest.json:

| Pole | Typ i ograniczenie |
|---|---|
| schema_version | integer, początkowo 1 |
| run_id | tekst UUID, zgodny z nazwą katalogu |
| status | enum, tylko complete w opublikowanym katalogu |
| created_at_utc | ISO 8601 UTC, chwila zakończenia obliczeń i przygotowania zapisu |
| input_sha256, config_sha256, source_version | tekst, 64 cyfry szesnastkowe |
| source_path | względna ścieżka do data/raw/snapshots/<source_version>/ |
| code_version | identyfikator commitu i flaga dirty; bez pozorowania czystej wersji |
| input_start, input_end | ISO 8601 z offsetem, zakres ocenianych pomiarów |
| station_id | integer, jedna stacja na uruchomienie |
| n | dodatni integer, liczba godzin wejścia |
| scenarios | lista tekstów: podstawowy, sensitivity |
| files | mapa względna ścieżka pliku -> SHA-256; bez samego manifestu |

Przed publikacją hashe input.csv, config.json i provenance.json muszą być zgodne
z manifestem. Hashe wyników obejmują oba scenariusze. Odtworzenie używa kopii
wejścia i parametrów, a nie ponownego pobrania API. Czasy pobrania źródeł są
w provenance.json; created_at_utc nie jest datą pomiaru ani gwarancją świeżości.

Właściciele potrzebnych zmian: Dawid Jopek — snapshoty źródeł i pochodzenie;
Kacper Dąbek — spójność wejścia, wersjonowany zapis i walidacja odczytu.
