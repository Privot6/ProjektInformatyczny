# Kontrakt analizy i rekomendacji

Wymaganie: R5. Granica istniejąca: walidacja danych i konfiguracji przekazuje
poprawne pomiary do scripts/fuzzy_model.py. Komunikacja jest wywołaniem funkcji
w jednym procesie Python, bez HTTP i bez osobnego serwera analitycznego.

## Istniejący interfejs

FuzzyModel(cfg: dict).evaluate(row: dict[str, float | str]) -> dict[str, float | str].
Przed wywołaniem load_config odczytuje config/lab4.json, a load_data zwraca
chronologiczną listę godzin. row może zawierać timestamp; model go nie używa.
Wejściem evaluate są pola pm25, pm10, temperature_2m, wind_speed_10m, precipitation.
Jednostki: µg/m³, µg/m³, °C, km/h i mm sumy godzinowej. Warunki pól i czasu
określa [model danych](data-model.md).

check_pm i check_weather przekształcają wartości do float. Obecna implementacja
akceptuje również napisy liczbowe możliwe do przeliczenia. Kontrakt między modułami
po load_data używa już liczb float. Model ponownie sprawdza pola pomiarowe;
nie sprawdza dat, liczebności próbki ani pochodzenia. Te warunki należą do warstwy
danych, nie mogą być domniemywane na podstawie wyniku evaluate.

| Wynik | Typ i znaczenie |
|---|---|
| score | Skończony float, punkty skali 0–100 |
| label | TRENUJ, OGRANICZ WYSIŁEK albo ZOSTAŃ W DOMU |
| r_bad, r_middle, r_good | Skończone float 0–1, aktywacje reguł |

baseline(row, cfg) -> dict zwraca tylko score i label. Brak aktywacji w bazowym
jest zapisywany jako puste pola CSV. Model nie zapisuje plików ani nie pobiera API.
Obiekt FuzzyModel utrzymuje stan symulacji i cache biblioteki; przetwarzanie jest
sekwencyjne w jednym procesie, bez współdzielenia tego obiektu między wątkami.

| Sytuacja | Istniejący sygnał | Reakcja planowanego koordynatora |
|---|---|---|
| Brak pola, NaN, nieskończoność, ujemny PM/wiatr/opad lub temperatura poza zakresem | ValueError w walidatorze | Koniec obliczeń, brak publikacji nowego uruchomienia |
| Brak aktywnej reguły | ValueError | Koniec obliczeń, brak zastępczego indeksu |
| Błędna konfiguracja | ValueError lub błąd odczytu JSON; brak klucza może dać KeyError | Komunikat o konfiguracji, bez publikacji |
| Nieoczekiwany błąd biblioteki | Wyjątek obliczeń | Komunikat o nieudanym obliczeniu, bez wyniku udającego sukces |

Indeks 0 jest poprawną wartością dziedziny, dlatego nie jest kodem błędu.
Nie stosuje się etykiety TRENUJ jako domyślnej przy brakującym wyniku.

## Reguły istniejące i parametry

Wnioskowanie Mamdaniego z scikit-fuzzy: AND=min, OR=max, trzy reguły, centroid.
Wejścia pochodne: max(pm25/pm25_scale, pm10/pm10_scale), odległość temperatury
od temperature_center, wiatr i opad. Najgorsze warunki nie są kompensowane samą
dobrą pogodą. Parametry i mapowanie indeksu na etykiety pozostają z config/lab4.json:
score < 35 — ZOSTAŃ W DOMU; 35 <= score < 65 — OGRANICZ WYSIŁEK; score >= 65 — TRENUJ.
Parametry są założeniami projektu; nie są godzinowymi normami WHO/GIOŚ.

Lab 4 porównuje stabilność indeksu po +1 µg/m³ PM2.5. Zmiana skali z 25 na 30
w próbie wrażliwości jest osobnym scenariuszem; nie zmienia konfiguracji bazowej.
Nie jest to prognoza PM ani potwierdzenie bezpieczeństwa zdrowotnego.

## Planowane połączenie obliczeń i zapisu

prepare_run(input_path: Path, config_path: Path, output_root: Path) -> RunRef
jest planowaną operacją koordynującą CLI. Wykorzystuje istniejące load_data,
load_config, baseline, FuzzyModel.evaluate i reguły agregacji compare_methods.run.
Nie jest funkcją już dostępną w Lab 4. Oblicza oba warianty i oba scenariusze na
tych samych godzinach, przed udostępnieniem katalogu dashboardowi.

RunRef zawiera run_id i run_dir. Zwracany jest dopiero po opublikowaniu kompletu
plików przez planowany RunStore. Błąd danych lub konfiguracji jest ValueError;
błąd odczytu lub zapisu jest OSError; kolizja docelowego run_id jest FileExistsError.
Niepowodzenie nie zmienia wcześniej opublikowanego przebiegu.

load_run(run_dir: Path) -> RunView jest planowaną granicą magazyn–dashboard.
RunView zawiera manifest, config oraz obserwacje i porównania obu scenariuszy.
Walidacja obejmuje komplet plików, schema_version, hashe, klucze rekordów,
zgodność zakresu i n. Brak pliku daje OSError; naruszenie schematu lub haszy
daje ValueError. Błędu nie przekazuje się pustą tabelą udającą prawidłowy wynik.

## Odbiór UC-01

| Przypadek | Oczekiwane zachowanie |
|---|---|
| Wersja próbki Lab 4, scenariusz podstawowy | 72 godziny, po 72 wyniki metod; średnie zmiany 0.555555556 i 0.422230450 pkt z tolerancją 1e-6 |
| Próba wrażliwości | Te same godziny, średnie 0 i 0.040723361 pkt z tolerancją 1e-6 |
| PM2.5=19.2, PM10=31.6, T=16.4, wiatr=15.3, opad=0 | Baseline 90; rozmyty około 64.572043; po +1 PM2.5 baseline 50, rozmyty około 61.972103 |
| Brak godziny albo niepoprawny pomiar | Brak nowego opublikowanego uruchomienia i komunikat o danych |
| Awaria zapisu podczas drugiego scenariusza | Brak RunRef i niewidoczny niekompletny katalog; poprzedni przebieg działa |
| Nieistniejący dzień lub brak etykiety TRENUJ | Komunikat o braku dnia albo kwalifikujących się godzin; bez podstawiania innego dnia |
| Ten sam indeks dwóch godzin | Najpierw wcześniejszy timestamp; ranking deterministyczny |

Ranking używa oryginalnego score i label dla wariantu rozmytego, nie wyniku
perturbacji. Pokazuje do trzech godzin z etykietą TRENUJ z wybranego lokalnego dnia,
sortując score malejąco, timestamp rosnąco. Nie łączy godzin w ciągłe okno.
Właściciel adaptacji koordynatora i kontroli wyników: Maksym Łazowski.
