# Kontrakt analizy i prezentacji wyników

## Istniejące obliczenia Lab 4

`run(raw_dir, lab3_path, output)` z `scripts/compare_methods.py` odczytuje dane archiwalne, przygotowuje kompletne doby, wykonuje podział czasowy i porównuje Ridge z drzewem. Zwraca klucz metody wybranej do dalszej oceny (`ridge` lub `tree`) i zapisuje wyniki obu scenariuszy. Jednostką wyniku jest µg/m³. Kontrakt plików opisuje [model danych](data-model.md).

Walidacja obejmuje hashe źródeł, czasy, jednostki, stanowisko GIOŚ, duplikaty, zakresy i kompletność. Niepełne doby historyczne są pomijane i wymienione w metadanych. Brak poprawnego wejścia daje błąd. Estymaty z próby zastosowania na prognozach Lab 3 nie mają pomiaru referencyjnego.

## Planowana publikacja i odczyt

| Interfejs | Zachowanie |
|---|---|
| `prepare_run(raw_dir, lab3_path, output_root) → RunRef` | Uruchamia obliczenia w katalogu roboczym. Zwraca `run_id` po walidacji i atomowej publikacji kompletnego katalogu. |
| `load_run(run_id) → RunView` | Sprawdza wersję schematu, komplet plików, hashe i powiązania dat. Zwraca dane gotowe do prezentacji. |
| Planowany dashboard | Umożliwia wybór przebiegu, scenariusza i daty, pokazuje pomiar, estymaty, MAE i pochodzenie. Dla próby Lab 3 pokazuje osobno prognozę IOŚ-PIB. |
| Błąd | Niepełny zapis nie dostaje statusu ukończonego. Błędny identyfikator lub brak pliku wyświetla komunikat i nie daje częściowej prezentacji. |

Modele PM10 wspierają R4. Planowana rekomendacja godzinowa R5 wymaga odrębnego kontraktu i walidacji etykiet.
