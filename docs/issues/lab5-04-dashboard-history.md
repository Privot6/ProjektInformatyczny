# L5-04 Wybór przebiegu i prezentacja pochodzenia wyniku

Status: do realizacji.
Odpowiedzialny: Kornel Łazowski.
Wymaganie: R4.
Powiązanie: UC-01 w docs/architecture.md.

## Cel

Planowany dashboard umożliwia wybór scenariusza, daty i kompletnego run_id.
Dashboard odczytuje dane przez RunView.

## Kryteria odbioru

- Widoczne są tylko kompletne przebiegi z poprawną wersją manifestu i hashami.
- Widok wskazuje run_id, stację, zakres pomiarów, czasy pobrania źródeł i created_at_utc.
- Widok odróżnia pomiar GIOŚ, prognozę IOŚ-PIB i estymaty modeli.
- Dla daty testowej widoczne są obie estymaty, pomiar i błędy bezwzględne.
- Filtr daty używa Europe/Warsaw.
- Brak daty albo uszkodzony zapis daje komunikat o niedostępności danych.
- Pobieranie CSV dotyczy tego samego przebiegu i scenariusza co widok.

Recenzent obszaru: Kacper Dąbek. Zależność: load_run i RunView z L5-02.
