# Kontrakt pogody i integracji dla Lab 4

`scripts/lab4_data.py` przyjmuje istniejący plik Lab 3. Kolumny: `timestamp`,
`pm25`, `pm10`, `temperature_2m`, `wind_speed_10m`, `precipitation`.
Jednostki: µg/m³, µg/m³, °C, km/h i mm sumy godzinowej. Czas zawiera offset.
Kolejność i ciągłość są sprawdzane w UTC, więc dwie lokalne godziny przy zmianie
czasu jesienią nie są mylone z duplikatem. Plik jest czytany, nie nadpisywany.

Uruchom `python scripts/audit_inputs_lab4.py`. Raport zawiera SHA-256, zakres czasu,
liczbę godzin i wynik kontroli braków, duplikatów i ciągłości. Puste, nieskończone
lub fizycznie niepoprawne wartości przerywają procedurę. Nie wykonujemy dodatkowej
interpolacji ani sortowania ukrywającego nieprawidłową kolejność.

`python scripts/reproduce_lab4.py` odtwarza przygotowanie Lab 3 w katalogu
tymczasowym i porównuje wszystkie wiersze z istniejącym wejściem. Następnie
uruchamia Lab 4 dwukrotnie i porównuje pliki wynikowe bajtowo. Raport
`results/lab4/reproducibility.json` zawiera hashe wejść i wyników. Odtworzenie
nie nadpisuje data/processed ani data/raw.

Oba warianty otrzymują pomiary z tej samej godziny. Jest to ocena historyczna
warunków, bez prognozowania przyszłego PM. Nie ma podziału train/test, ponieważ
żadna metoda nie jest dopasowywana. Użycie interpolacji z Lab 3 nie jest dowodem
działania na żywo: do takiej oceny potrzebne są dane zarejestrowane tak, jak były
dostępne w momencie decyzji. Nie wolno traktować pogody pomiarowej jako znanej
z góry prognozy. Dane pyłowe są pomiarami GIOŚ, a dane pogodowe pochodzą z reanalizy ERA5 Open-Meteo.
