# AeroRun – Analityczny asystent wyboru okna treningowego na podstawie danych smogowych (GIOŚ) i meteorologicznych (Open-Meteo)

**Specjalność:** Analiza Danych Społeczno-gospodarczych

**Zespół:** Dawid Jopek, Kornel Łazowski, Maksym Łazowski, Kacper Dąbek 

**Data opracowania:** 18.10.2026 r.

---

## Opis problemu

Osoby trenujące na zewnątrz w Rzeszowie muszą sprawdzać prognozę jakości powietrza i prognozę pogody w osobnych serwisach. Utrudnia to wybór dnia i godziny treningu z uwzględnieniem stężenia PM10, temperatury, opadów i wiatru.

## Cel i wartość rozwiązania

**AeroRun** ma pomóc wybrać godzinę treningu i ocenić warunki przed wyjściem. Lab 2 sprawdza dane wejściowe dla Rzeszowa: średnią dobową prognozę PM10 opracowaną przez IOŚ-PIB i publikowaną także przez GIOŚ oraz godzinową temperaturę, opady i prędkość wiatru z Open-Meteo. Rekomendacja treningowa wymaga ustalenia reguł oceny, a analiza zależności pogody od PM10 wymaga dodatkowych danych historycznych.

## Odbiorcy rozwiązania

* Osoby aktywne fizycznie na świeżym powietrzu w miastach (biegacze, rowerzyści, spacerowicze).
* Trenerzy grup biegowych.
* Rodzice planujący wyjścia z dziećmi w okresach grzewczych.

---


## Struktura repozytorium i dokumentacja

* 📄 [Analiza problemu i wymagania (`docs/problem.md`)](./docs/problem.md)
* 📊 [Analiza źródeł danych i pomysł realizacji (`docs/data.md`)](./docs/data.md)
* 📁 [Rzeczywista próbka prognoz PM10 i pogody dla Rzeszowa (`data/raw/sample.json`)](./data/raw/sample.json)


```text
projekt-zespolu/
├── data/
│   └── raw/
│       └── sample.json
├── docs/
│   ├── problem.md
│   └── data.md
└── README.md
```


# AeroRun — Laboratorium 3

Lab 3 przetwarza zapisaną w Lab 2 próbkę prognoz dla Rzeszowa. Wynik zawiera jedną dobową średnią PM10 i listę godzin pogody dla każdej daty lokalnej.

## Uruchomienie w Pythonie 3.10+

W katalogu głównym projektu uruchom poniższe polecenia. Zależność `tzdata` dostarcza reguły czasu dla `Europe/Warsaw` na systemach bez bazy IANA, m.in. Windows. Właściwe przetwarzanie używa zapisanej próbki i działa bez połączenia z API.

```bash
python -m pip install -r requirements.txt
python scripts/prepare_forecast.py
```

Wejściem jest [data/raw/sample.json](./data/raw/sample.json), a wynikiem [data/processed/sample-clean.json](./data/processed/sample-clean.json). Skrypt uruchamia kontrole przed zapisem. Próbę z celowo powtórzoną godziną można wykonać poniższym poleceniem. Oczekiwany jest komunikat o duplikacie, kod wyjścia 1 i brak nowego pliku.

```bash
python scripts/prepare_forecast.py --source data/test/forecast-duplicate.json --output data/test/forecast-rejected.json
```

[Plan pozyskania](./docs/data.md#plan-pozyskania-danych-w-lab-3), [słownik danych](./docs/data-dictionary.md) i [kontrole oraz odtworzenie wyniku](./docs/processing.md).

Historyczne zestawienie pomiarów GIOŚ z reanalizą ERA5 można nadal odtworzyć poleceniem `python scripts/prepare_data.py --output results/history_reproduced`.

# AeroRun — Laboratorium 4

Porównujemy dwie metody uczenia maszynowego dla R4. Ridge i drzewo regresyjne estymują dobową średnią PM10 na podstawie temperatury, wiatru i opadów. Uczenie i ocena używają archiwalnych pomiarów GIOŚ i danych Open-Meteo z Rzeszowa. Na [próbce Lab 3](./data/processed/sample-clean.json) skrypt wykonuje też próbę zastosowania do dwóch kompletnych dób z prognozą IOŚ-PIB.

## Środowisko

Polecenia uruchamiaj w PowerShellu z katalogu głównego projektu. Jeśli nie masz jeszcze `.venv`, utwórz je za pomocą zainstalowanego Pythona 3.12.

```powershell
py -3.12 -m venv .venv
```

Jeśli środowisko projektu wymaga instalacji zależności, uruchom:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-lab4.txt
```

Jeżeli w `.venv` brakuje pip, najpierw uruchom `.\.venv\Scripts\python.exe -m ensurepip`. Dokładne wersje użyte na Windows z Pythonem 3.12.14 są w `requirements-lab4-lock.txt`.

## Uruchomienie i kontrola

Polecenia używają interpretera projektu i działają bez aktywowania `.venv`.

```powershell
.\.venv\Scripts\python.exe scripts/compare_methods.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_lab4.py" -v
.\.venv\Scripts\python.exe scripts/reproduce_lab4.py
```

Możesz też uruchomić `scripts/compare_methods.py` przyciskiem **Run** w PyCharmie. Domyślne ścieżki danych i wyników są liczone od katalogu projektu, niezależnie od ustawienia **Working directory**.

Źródła, adresy zapytań i sumy kontrolne są w [data/raw/lab4](./data/raw/lab4/sources.json). Skrypt działa na zapisanych plikach. Dopasowuje modele na dniach sprzed 12.10.2026, a oblicza MAE na kompletnych dniach od tej daty do 31.10.2026. W wariancie głównym drzewo ma limit głębokości 3. W próbie wrażliwości limit wynosi 4.

Wyniki obejmują [porównanie MAE](./results/lab4/comparison.csv), [19 ocenianych dni](./results/lab4/observations.csv), [próbę zastosowania na Lab 3](./results/lab4/lab3_application.csv) oraz [parametry i dane pominięte](./results/lab4/run.json). Próba wrażliwości jest w [osobnym katalogu](./results/lab4/sensitivity/comparison.csv). Polecenie odtworzenia porównuje osiem plików bajtowo w tym samym środowisku. Aby zapisać nowe wykonanie obok wyników wzorcowych, użyj `.\.venv\Scripts\python.exe scripts/compare_methods.py --output results/lab4_reproduced`.

[Protokół, literatura, kontrola ręczna i wnioski](./docs/experiment.md).

## AeroRun — Laboratorium 5

[Projekt techniczny](./docs/architecture.md) opisuje aplikację mobilną w React Native. Po naciśnięciu **Sprawdź** aplikacja pobiera dane z publicznych API, sprawdza je i wyświetla warunki dla wskazanego dnia. Lokalna baza SQLite zachowuje ostatni poprawnie pobrany zestaw. [Zadania implementacyjne](./docs/issues/lab5-implementation.md) określają zakres prac i kryteria odbioru.
