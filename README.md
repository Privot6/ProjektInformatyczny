# AeroRun – Analityczny asystent wyboru okna treningowego na podstawie danych smogowych (GIOŚ) i meteorologicznych (Open-Meteo)

**Specjalność:** Analiza Danych Społeczno-gospodarczych

**Zespół:** Dawid Jopek, Kornel Łazowski, Maksym Łazowski, Kacper Dąbek 

**Data opracowania:** 18.10.2026 r.

---

## Opis problemu

Osoby trenujące na zewnątrz (biegacze, rowerzyści) w polskich miastach w sezonie jesienno-zimowym są narażone na wysokie stężenia pyłów zawieszonych PM2.5 i PM10 oraz dynamiczne zmiany pogody. Obecnie dane o jakości powietrza i prognozy pogody znajdują się w osobnych aplikacjach i mają postać surowych wykresów bez analizy zależności między wiatrem, temperaturą a stężeniem zanieczyszczeń. W efekcie użytkownik podejmuje decyzję o wyjściu na trening intuicyjnie, narażając układ oddechowy na smog lub rezygnując z aktywności mimo sprzyjającego okna pogodowego.

## Cel i wartość rozwiązania

**AeroRun** zastępuje ręczne przeglądanie kilku źródeł jednym narzędziem wspierającym decyzję w modelu *Rekomendacja zamiast automatycznego sterowania*. Użytkownik otrzymuje:
* wyliczoną statystyczną zależność (współczynnik korelacji Pearsona oraz model regresji liniowej) pokazującą, jak prędkość wiatru i temperatura wpływają na przewiewanie smogu w jego lokalizacji,
* jednoznaczną rekomendację decyzyjną (`TRENUJ` / `OGRANICZ WYSIŁEK` / `ZOSTAŃ W DOMU`) wraz ze wskazaniem najkorzystniejszych godzin treningowych w ciągu doby na podstawie progów norm WHO/GIOŚ.

## Odbiorcy rozwiązania

* Osoby aktywne fizycznie na świeżym powietrzu w miastach (biegacze, rowerzyści, spacerowicze).
* Trenerzy grup biegowych.
* Rodzice planujący wyjścia z dziećmi w okresach grzewczych.

---


## Struktura repozytorium i dokumentacja

* 📄 [Analiza problemu i wymagania (`docs/problem.md`)](./docs/problem.md)
* 📊 [Analiza źródeł danych i pomysł realizacji (`docs/data.md`)](./docs/data.md)
* 📁 [Próbka danych z API GIOŚ i Open-Meteo (`data/sample.json`)](./data/sample.json)
  

```text
projekt-zespolu/
├── data/
│   └── sample.json
├── docs/
│   ├── problem.md
│   └── data.md
└── README.md
```


# AeroRun — Laboratorium 3

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
