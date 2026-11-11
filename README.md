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

Historyczne zestawienie godzinowych pomiarów GIOŚ z reanalizą ERA5 przygotowuje `scripts/prepare_data.py`. Jego wynik `data/processed/aerorun_dane.csv` jest wejściem do eksperymentu Lab 4.


# AeroRun — Laboratorium 4

Porównanie reguł progowych z wnioskowaniem rozmytym Mamdaniego na historycznym
zestawie pomiarów i reanalizy. Dotyczy R5 i stabilności indeksu, bez oceny skuteczności zdrowotnej.

## Środowisko

Python 3.10+; polecenia z katalogu głównego projektu, Windows PowerShell.
Utworzenie .venv jest potrzebne tylko wtedy, gdy środowisko jeszcze nie istnieje:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable)"
python -m pip install -r requirements-lab4.txt
```

Jeśli polityka PowerShell blokuje aktywację, wywoływać bezpośrednio
`.\.venv\Scripts\python.exe` zamiast `python`. Nie instalować systemowo.
`requirements-lab4-lock.txt` zapisuje dokładne wersje sprawdzonego środowiska
Windows/Python 3.13; na tej platformie można zamiast zakresów zainstalować ten plik.
Na innych platformach użyć requirements-lab4.txt i zapisać własne wersje.
Środowiska `.venv/` nie dodawać do Git.

## Odtworzenie eksperymentu

Wejście to `data/processed/aerorun_dane.csv`, 72 godziny pomiarów GIOŚ i reanalizy ERA5.
Przygotowanie historycznego zbioru można odtworzyć do osobnego
katalogu: `python scripts/prepare_data.py --output results/lab3_reproduced`.

```powershell
python scripts/audit_pm_lab4.py
python scripts/audit_inputs_lab4.py
python examples/lab4/fuzzy_demo.py
python scripts/compare_methods.py
python scripts/verify_pm_results.py
python scripts/reproduce_lab4.py
python -m unittest discover -s tests -v
python -m streamlit run app_lab4.py
```

Konfiguracja: `config/lab4.json`. Oba warianty oceniają te same godziny i ten sam
przyrost +1 µg/m³ PM2.5. Próba wrażliwości zmienia wyłącznie pm25_scale z 25 na 30
u obu metod. Skrypt generuje oba scenariusze jednym poleceniem. Nie ma losowania.
Progi są założeniami demonstracyjnymi, bez przypisywania ich normom WHO/GIOŚ.

Wyniki: `results/lab4/comparison.csv`, `observations.csv`, `control_checks.csv`,
`run.json`, audyty oraz osobny podkatalog `sensitivity/`. Miara podstawowa to średnia
bezwzględna zmiana indeksu w punktach; nie jest to MAE prognozy ani trafność etykiet.
Tryb jawny: `python scripts/compare_methods.py --input data/processed/aerorun_dane.csv --config config/lab4.json --output results/lab4`.

Dokumentacja: `docs/experiment.md`, `docs/lab4_model.md`, `docs/lab4_air.md`
i `docs/lab4_data.md`.
