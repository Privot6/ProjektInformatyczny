# Dane pyłowe w eksperymencie Lab 4

Wejście to istniejący `data/processed/aerorun_dane.csv`: 72 godziny pomiarów GIOŚ i pogody z reanalizy ERA5
z Lab 3. Wartości są w µg/m³. Pomiary pyłów pochodzą ze stacji 10125 w Rzeszowie. Pogoda pochodzi z reanalizy ERA5 Open-Meteo.
Sama próbka nie potwierdza skuteczności rekomendacji w terenie. Lab 4 nie zmienia
`data/raw/` ani `data/processed/`.

Uruchom `python scripts/audit_pm_lab4.py`. Raport `results/lab4/input_pm_audit.json`
zawiera liczbę wierszy, zakresy stężeń, SHA-256 wejścia i flagę PM2.5 > PM10.
Flaga wymaga przeglądu, nie usuwa rekordu. Braki, wartości ujemne i nieskończone
przerywają analizę; nie dopisujemy interpolacji w Lab 4.

Po wygenerowaniu wyników uruchom `python scripts/verify_pm_results.py`.
To niezależna kontrola kompletności wszystkich par godzina/wariant, zgodności
stężeń z wejściem, perturbacji +1 i obu przypadków wysokiego PM. Raport trafia
do `results/lab4/pm_results_check.json`. Scenariusze kontrolne są zdefiniowane
w `scripts/lab4_controls.py`, poza kodem algorytmu rekomendacji.

## Scenariusz kontrolny

W eksperymencie zwiększamy wyłącznie PM2.5 o 1 µg/m³. Jest to założona perturbacja
sprawdzająca stabilność algorytmu, a nie oszacowana niepewność czujnika.
Te same rekordy przed zmianą i po zmianie otrzymują oba warianty.
Dodatkowe przypadki silnego zapylenia sprawdzają, czy dobra pogoda nie prowadzi
do etykiety TRENUJ mimo wysokiego wejścia pyłowego. Są to testy reguł projektu,
nie kliniczna ocena bezpieczeństwa.
