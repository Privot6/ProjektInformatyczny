# LAB7-01 — błędne przypisanie ocen ekspertom

Status: poprawiono skrypt lokalnie i ponownie sprawdzono manualnie (M16).
Rozbieżność w `docs/experiment_scoring.md` pozostaje jawna: na wyraźne
polecenie użytkownika ten plik zachowano bez zmian.
Priorytet: wysoki dla wiarygodności wniosków; wartości punktacji bez zmian.

## Odtworzenie i oczekiwanie

1. W bazowym commicie `bd22946619a49ec0738e123c7222c40f6fc5305e` odczytać
   `data/processed/lab4_scoring_scenarios.csv`: wszystkie `reference_source`
   mają wartość `synthetic_assumption`.
2. Uruchomić `python scripts/compare_scoring_methods.py --output results/lab7/scoring-before`.
3. Porównać końcowy komunikat, pole `reference_note` w `run.json` i opis
   `docs/experiment_scoring.md` z pochodzeniem ocen w CSV.

Oczekiwane: informacja o syntetycznych założeniach i ograniczeniu oceny do
tej próbki. Rzeczywiste: „Domyślne oceny są opinią ekspertów. Wynik dowodzi
przewagę w rzeczywistym użyciu.” To nieuprawniony wniosek o użyteczności R5.
[Dowód przed poprawką](../../results/lab7/scoring-before/run.json).

## Poprawka i ponowne sprawdzenie

Poprawiono docstring, `reference_note` i komunikat konsoli skryptu.
Nie zmieniono wag, oczekiwań ani danych. Ponowiono to samo polecenie
z `--output results/lab7/scoring`. Operator odczytał metadane i komunikat:
„Domyślne oceny są syntetycznymi założeniami. Wynik dotyczy tej próbki;
nie potwierdza skuteczności u użytkowników.”

MAE pozostały 1,958333 / 6,875000 pkt (główna próba) i 1,958333 / 6,708333 pkt
(wrażliwość). M16: FAIL przed, PASS po poprawce. [Dowód po](../../results/lab7/scoring/run.json).
Hashe obu wersji skryptu są w plikach `run.json`; wersja po to baza z roboczym
diffem Lab 7. Historycznych wyników Lab 4 nie nadpisano.


