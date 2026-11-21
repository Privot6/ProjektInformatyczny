# Plan i wyniki testów

## 1. Zakres oraz wersja kodu i danych

Lab 7 jest realizowane z testami manualnymi na wyraźne polecenie użytkownika.
Nie dodajemy ani nie uruchamiamy testów automatycznych, CI, asercji ani mutacji
w głównej wersji kodu. Istniejące testy wcześniejszych laboratoriów pozostają
w repozytorium. Operator uruchamia pojedyncze przypadki i osobiście porównuje
wynik z oczekiwaniem. Skrypt pomiarowy zbiera wyłącznie czasy.

Wersja bazowa: `bd22946619a49ec0738e123c7222c40f6fc5305e`, gałąź `lab7`.
Wyniki poprawek dotyczą tej bazy z roboczym diffem Lab 7; dokładne hashe plików
zapisujemy przy dowodach. Nie utworzono nowego commita w imieniu zespołu.
Próbki: kopie `data/raw/sample.json` i `data/test/forecast-duplicate.json`;
`data/raw/lab6/gios.json` i `data/processed/lab4_scoring_scenarios.csv`
odczytywano wyłącznie do analizy i treningu, bez zapisu w tych plikach.
Nie zmieniamy źródeł w `data/raw/` ani bazy użytkownika.

Środowisko: Windows 11 build 26200, AMD64 Family 25 Model 117 Stepping 2,
Python 3.12.16, SQLite 3.53.1, scikit-learn 1.7.2, NumPy 2.5.5, SciPy 1.18.1,
FastAPI 0.165.0, httpx 0.28.1, Uvicorn 0.54.0, tzdata 2026.6.
[Pełny lock zależności](../requirements-lab7-lock.txt).
Pierwotne środowisko miało Python 3.15 i niekompletne zależności; utworzono
wydzielone `.venv-lab7` z Pythonem 3.12. Nie używano starego środowiska do oceny.
Wersję danych i plików kodu identyfikuje [manifest](../results/lab7/manifest.json).
Hashe dotyczą bajtów aktualnego checkoutu; historyczne raporty mogą mieć inny
hash CSV po zmianie końców linii. Wiersze i liczby porównano na tej samej próbce.

## 2. Plan przypadków testowych i dziennik uruchomień

Poniższe oczekiwania zapisano przed wykonaniem. Podstawą są wymagania Lab 2,
reguły Lab 6 i niezależny rachunek; nie dopasowujemy oczekiwań do programu.

| ID | Wymaganie / wejście | Oczekiwany wynik i podstawa |
|---|---|---|
| M01 | R1/R2: CLI Lab 3, kopia próbki | 8 dat, 168 godzin, 3 PM10; 12.11: PM10=31,59 i 24 godziny; jednostki z processing.md |
| M02 | R2: 11.11.2026 23:00 UTC | 12.11 00:00+01:00, z reguły Europe/Warsaw |
| M03 | R3: kopia z powtórzoną godziną, istniejący wynik kontrolny | Kod 1, komunikat o duplikacie, stary wynik bez zmian; walidacja przed zapisem |
| M04 | R3: pusty JSON oraz ujemne PM10 | Odrzucenie przed utworzeniem wyniku; schemat i zakres PM10≥0 |
| M05 | R5: PM10 oszacowane=20, temperatura=0, wiatr=5, opad=0 | 81 pkt: round(28,7778+12,5+25+15); niezależny rachunek S04 |
| M06 | R5: klasy dla 39,40,69,70; PM10 dobowe=112,5 albo opad=4 | ZOSTAŃ W DOMU, OGRANICZ, OGRANICZ, TRENUJ; weto daje ≤39, implementation.md |
| M07 | R2: 29.03 i 25.10.2026 | Odpowiednio 23 i 25 godzin lokalnej doby |
| M08 | R1/R2/R5: pełna operacja check dla 12.11, zapisane odpowiedzi HTTP | 24 godziny, PM10=31,59, score i best, 24 rekordy SQLite, brak ostrzeżeń |
| M09 | R3: awaria obu źródeł po M08, potem dzień bez cache | Dla 12.11 cache i ostrzeżenia; dla nowej daty HTTPException 503 |
| M10 | R3: 14.11 bez PM10, następnie null temperatury 12.11 | Brak best/score dla brakujących danych; brak nie może stawać się zerem |
| M11 | R3: błąd INSERT w osobnej bazie po M08 | Ostrzeżenie zapisu, świeży wynik w pamięci, poprzedni zapis zachowany w całości |
| M12 | R1/R3: HTTP rzeczywistego FastAPI, niedozwolona nazwa dnia | HTTP 422; dozwolone są tylko today i tomorrow |
| M13 | R5: porównanie aktualnej punktacji na 24 scenariuszach Lab 4 | MAE aplikacji=47/24=1,958333 pkt; baza=165/24=6,875 pkt; wrażliwość=161/24=6,708333 pkt |
| M14 | R1/R3/R5: Android, wybór dni, rozwijanie, brak połączenia | Właściwy dzień, jednostki, czytelny błąd, brak starego wyniku po nowym błędzie |
| M15 | Dokumentacja: osoba inna niż autor, nowy katalog i środowisko | Instalacja według README, poprawny przypadek oraz błąd bez ustnych podpowiedzi |
| M16 | R5: pochodzenie ocen i wnioski skryptu Lab 4 | Opis zgodny z synthetic_assumption; brak twierdzenia o potwierdzonej skuteczności u użytkowników |




| Data i czas Europe/Warsaw | Wersja / środowisko | ID | Wynik | Czas [s] | Dowód i odczyt |
|---|---|---|---|---|---|
| 21.11.2026 18:44 | baza / środowisko powyżej | M01 | PASS | nie mierzono | [prepared.json](../results/lab7/prepared.json): 8 dat, 168 godzin, 3 PM10; właściwe jednostki |
| 21.11.2026 18:44 | baza / j.w. | M02 | PASS | nie mierzono | prepared.json: 12.11 00:00+01:00 odpowiada 11.11 23:00 UTC |
| 21.11.2026 18:44 | baza / j.w. | M03 | PASS | nie mierzono | [log](../results/lab7/manual-log.txt), [zachowany plik](../results/lab7/protected-result.txt): kod 1, duplikat, stara treść |
| 21.11.2026 18:44 i 18:48 | baza / j.w. | M04 | PASS | nie mierzono | log: pusty obiekt, puste tablice i PM10=−1 dają kod 1 bez zapisu |
| 21.11.2026 18:44 | baza / j.w. | M05 | PASS | nie mierzono | log: S04=81, zgodnie z rachunkiem |
| 21.11.2026 18:44 | baza / j.w. | M06 | PASS | nie mierzono | log: klasy 39/40/69/70 i weto 39 |
| 21.11.2026 18:44 | baza / j.w. | M07 | PASS | nie mierzono | log: 23 i 25 godzin |
| 21.11.2026 18:44:18 | baza / j.w. | M08 | PASS | nie mierzono | [M08](../results/lab7/M08.json): 24 godziny, 31,59 µg/m³, best 22:00 / 97; odczyt SQLite 24 rekordy |
| 21.11.2026 18:44:39 | baza / j.w. | M09 | PASS | nie mierzono | [cache](../results/lab7/M09-cache.json): dwa źródła cache; bez zapisu 503, w logu |
| 21.11.2026 18:44:39 | baza / j.w. | M10 | PASS | nie mierzono | [brak PM10](../results/lab7/M10-missing.json), [null](../results/lab7/M10-null.json); score null, opad 0 zachowany |
| 21.11.2026 18:44:39 | baza / j.w. | M11 | PASS | nie mierzono | [odpowiedź](../results/lab7/M11.json), [rekordy przed/po](../results/lab7/M11-storage.json): zachowane 24 wiersze i czasy źródeł |
| 21.11.2026 18:46:56 | baza / j.w. | M12 | PASS | nie mierzono | [HTTP 422](../results/lab7/M12-http-422.json), rzeczywisty Uvicorn; kod odpowiedzi zapisany w logu |
| 21.11.2026 18:45 | baza / j.w. | M13 | PASS | nie mierzono | [MAE](../results/lab7/scoring/comparison.csv), [wrażliwość](../results/lab7/scoring/sensitivity/comparison.csv) |
| — | — | M14 | NOT RUN | — | Brak działającego Androida/adb na stanowisku; procedura przygotowana |
| — | — | M15 | NOT RUN | — | Brak rzeczywistego odbioru przez inną osobę zespołu |
| 21.11.2026 18:45, przed poprawką | baza / j.w. | M16 | FAIL | nie mierzono | [stary run.json](../results/lab7/scoring-before/run.json) błędnie przypisuje syntetyczne oceny ekspertom |
| 21.11.2026 18:45, po poprawce | baza + roboczy diff Lab 7 / j.w. | M16 | PASS | nie mierzono | [nowy run.json](../results/lab7/scoring/run.json) i komunikat zgodne z CSV; MAE bez zmian |



## 3. Pomiar niefunkcjonalny

Kryterium ustalone przed pomiarem: mediana czasu lokalnego `check` dla 24
godzin <2 s na tym stanowisku. Próg projektowy uzasadnia interakcyjne porównanie
godzin bez odczuwalnego oczekiwania na samo przetwarzanie. Jedna rozgrzewka,
pięć powtórzeń na identycznych danych. Zakres: odczyt cache, dwie odtworzone
odpowiedzi HTTP, walidacja, predykcja, punktacja i zapis SQLite; bez internetu,
startu procesu, treningu modelu i renderowania Androida. To dodatkowe kryterium
Lab 7; Lab 4 nie określało limitu czasu.

Wykonanie: 21.11.2026 18:45, środowisko z sekcji 1, zwykła sesja desktopowa,
bez celowo generowanego obciążenia. Nie mierzono zajętości CPU ani pamięci
innych procesów; nie jest to stanowisko dedykowane ani test obciążeniowy API.
Wynik dotyczy ciepłego cache i tej jednej maszyny.

| Powtórzenie | Czas [s] |
|---|---:|
| 1 | 0,01027160 |
| 2 | 0,01004060 |
| 3 | 0,01092320 |
| 4 | 0,00953540 |
| 5 | 0,01042190 |

Mediana **0,01027160 s**, minimum **0,00953540 s**, maksimum **0,01092320 s**.
Kryterium lokalnego przetwarzania <2 s jest spełnione. Nie wynika z niego,
że telefon otrzyma dane w 2 s przy wolnym internecie. [Surowy CSV](../results/lab7/timing.csv),
[warunki i podsumowanie](../results/lab7/timing-summary.json).
Odtworzenie: `python scripts/measure_lab7.py`; operator sam ocenia próg.

## 4. Ocena danych, wyników i kodu

**Dane.** Ręcznie wywołano istniejące przetwarzanie i walidację Lab 3 na kopii
próbki (M01–M04): format, jednostki, liczebności, zakresy, daty, unikalność
i zachowanie braków. Wynik: 168 godzin, 8 dat, 3 dobowe PM10; brak wejściowych
null, pięć dat wyniku bez PM10. Niepełne krańcowe doby mają 23 i 1 godzinę,
12–13.11 po 24. Duplikat, ujemne PM10 i puste dane odrzucono. Te kontrole
walidacyjne są częścią aplikacji, nie dodanymi testami automatycznymi.
Model przy starcie zweryfikował SHA-256 pomiarów Lab 6 zgodnie z manifestem
źródła. Poprawna struktura trzech dat nie świadczy o reprezentatywności sezonu.

**Wyniki — porównanie punktacji z Lab 4.** Ten sam aktualny
`backend.model.training_score`, te same 24 scenariusze i syntetyczne wzorce,
bez Ridge i bez sieci: MAE=1,958333 pkt, baza=6,875000 pkt, wrażliwość
bazy=6,708333 pkt. Sumy błędów to 47, 165, 161; podzielenie przez 24 niezależnie
potwierdza miarę. Przewaga wynosi 4,916667 i 4,750000 pkt, czyli przekracza
przyjęte w Lab 4 minimum 2 pkt w obu wariantach. Wynik obecnej punktacji jest
zgodny z Lab 4, różnica MAE aplikacji=0. Ręczny S04 daje 81 pkt, błąd 1 pkt;
baza daje 94 pkt, błąd 14 pkt. [Obserwacje](../results/lab7/scoring/observations.csv).
To ocena zgodności z założonymi wzorcami, bez potwierdzenia trafności treningowej.

**Wyniki — cały przepływ po integracji.** Na odtworzonych odpowiedziach źródeł
wykonano `check` dla 13.11 i zapis SQLite oraz score dla 24 godzin. Model uczony
na 28 godzinach daje MAE godzinowego PM10 w t+1 h **6,809397 µg/m³**, wobec
**22,786667 µg/m³** dla samej prognozy dobowej. Miara zgadza się z Lab 6 (6,81).
Pierwszy przypadek: estymacja 17,388587, pomiar 7,9, błąd 9,488587 µg/m³,
wynik końcowy 95 pkt. [Pełne obserwacje](../results/lab7/quality-observations.csv),
[raport](../results/lab7/quality-summary.json), [odpowiedź aplikacji](../results/lab7/quality-day.json).
MAE dotyczy składowej PM10 całego przepływu; brak etykiet eksperckich dla
wynikowych score uniemożliwia ocenę ich skuteczności w praktyce.

Ponowiono również historyczny eksperyment **dobowy** Lab 4 na tych samych
28/19 dniach i identycznych parametrach: Ridge=10,077318, drzewo=13,134539 µg/m³
w obu wariantach głębokości. [Porównanie](../results/lab7/pm10-daily/comparison.csv).
Potwierdza to wcześniejszy wybór Ridge; drzewo nadal nie spełnia kryterium
obniżenia MAE o 1 µg/m³. Nie wolno traktować 6,81 wobec 10,08 jako dowodu
poprawy po integracji: Lab 6–7 mają godzinowy cel t+1, inny okres i dodatkową
cechę PM10, a Lab 4 średnią dobową. Różnice wynikają z konstrukcji eksperymentu.



**Kod.** Przejrzano `read_cases/evaluate/run` i zmienione opisy w
`compare_scoring_methods.py`: podział odpowiedzialności, nazwy miar, błędy,
import wzoru aplikacji i pochodzenie ocen. Poprawiono rzeczywisty problem
LAB7-01; M16 zachowuje wynik przed/po. [Lokalny przegląd](issues/lab7-review.md)
nie zastępuje recenzji innej osoby w PR; rzeczywisty URL PR pozostaje do dodania.

## 5. Statusy wymagań

Wymagania zachowano z Lab 2, bez zmiany ich kryteriów dla uzyskania PASS.

| Wymaganie | Status | Dowód i granica oceny |
|---|---|---|
| R1 — PM10 i trzy pola pogody z jednostkami w jednym miejscu | niesprawdzone | Dane i backend spełniają kryterium próbki (M01, M08); odbiór widoku telefonu M14 nie został wykonany |
| R2 — wspólna data lokalna | spełnione | M02, M07, M08: północ i doby 23/25 godzin; ocena obejmuje sprawdzone przypadki |
| R3 — komunikat o brakach i błędach | niespełnione | Backend obsługuje braki, cache i 503 (M04, M09–M12), ale ekran nie renderuje warnings/pm10_notice/czasu cache; LAB7-02 |
| R4 — historyczna siła i kierunek zależności | spełnione | Protokół experiment.md, run.json z Lab 4 i odtworzenie 28/19 dni; korelacje +0,399/−0,132/−0,391 i parametry Ridge są dostępne w dokumentacji; brak widoku analitycznego w Androidzie |
| R5 — rekomendacja i porównanie godzin | niesprawdzone | Reguły i miara syntetyczna potwierdzone M05, M06, M08, M13; porównanie kart w Androidzie i użyteczność rzeczywista nie zostały odebrane |

Pomiar <2 s jest dodatkowym kryterium Lab 7, spełnionym wyłącznie dla lokalnego
przepływu. Nie zastępuje żadnego wymagania Lab 2.

## 6. Sprawdzenie dokumentacji

Sprawdzono technicznie lokalne uruchomienie konsoli, poprawne i błędne CLI,
instalację zależności w nowym `.venv-lab7`, start rzeczywistego Uvicorna i HTTP
422. To weryfikacja agenta na tym stanowisku, nie niezależny odbiór M15.
Nie pobrano projektu do nowego katalogu przez drugą osobę.

Pierwszy brak: domyślny Python 3.15 nie spełniał opisu Lab 6. README wskazuje
teraz jawnie 3.12, wybór interpretera, wydzielone środowisko i lock zależności.
Po przygotowaniu 3.12 uruchomiono ponownie poprawne i błędne CLI. Dodatkowo
pierwszy odczyt jednostek w konsoli Windows ujawnił UnicodeEncodeError;
po ustawieniu `PYTHONUTF8=1` ponowny odczyt się powiódł. Dodano to do instrukcji.
Uzupełniono instrukcję użytkownika o przepływ, jednostki, interpretację i błędy,
a architekturę o aktualne położenie FastAPI i SQLite.



## 7. Znane błędy i ograniczenia

| Problem | Status / wpływ / obejście |
|---|---|
| [LAB7-01: pochodzenie ocen](issues/lab7-reference-provenance.md) | Skrypt poprawiony lokalnie; stary FAIL zachowano. Protokół experiment_scoring.md na polecenie użytkownika pozostaje bez zmian; jego rozbieżność i błędne historyczne metadane są jawne, nowe wyniki są w Lab 7 |
| [LAB7-02: Android i metadane źródeł](issues/lab7-review.md) | Otwarty: brak czasu cache i ostrzeżeń na ekranie, M14 NOT RUN; techniczne obejście przez Swagger |
| [LAB7-03: drugi wykonawca i PR](issues/lab7-review.md) | Otwarty: M15 i niezależny przegląd; gotowa procedura, brak prawdziwego URL Issue/PR; nie publikowano lokalnych notatek w GitHub |
| [LAB7-04: użyteczność](issues/lab7-review.md) | Otwarty: brak niezależnych ocen i kilku sezonów danych; wyniki ograniczone do zapisanej próbki |


