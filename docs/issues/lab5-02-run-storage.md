# L5-02 Spójny zapis i odczyt uruchomień

Status: do realizacji.
Odpowiedzialny: Kacper Dąbek.
Wymagania: R1, R2, R3 i R5.
Powiązanie: docs/lab5/data-model.md i ADR-001.

## Cel

Planowany RunStore zachowuje niezmienne wejście i wyniki. Istniejący zapis
Lab 4 do stałego katalogu nie gwarantuje publikacji wszystkich plików razem.

## Kryteria odbioru

- Nowy run_id i manifest odpowiadają schematowi projektu; istniejące CSV nie zmieniają kolumn.
- Kopie input.csv i config.json odpowiadają input_sha256 oraz config_sha256.
- Są oba scenariusze, po dwa warianty na każdą godzinę, bez powtórzeń kluczy.
- Niepełna próba poniżej 48 godzin, luka czasu lub brak pomiaru jest odrzucony przed obliczeniami.
- Błąd zapisu drugiego scenariusza nie publikuje nowego przebiegu i nie uszkadza poprzedniego.
- Kolizja run_id nie nadpisuje katalogu; brak lub niezgodny hash daje błąd odczytu.
- Walidacja manifestu i powiązań poprzedza zwrócenie RunView.

Recenzent obszaru: Dawid Jopek. Zależność: L5-01 dla wersji źródła; L5-03 dla wyniku analizy.
