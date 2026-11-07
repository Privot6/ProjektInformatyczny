# L5-04 Wybór przebiegu i prezentacja pochodzenia wyniku

Status: do realizacji.
Odpowiedzialny: Kornel Łazowski.
Wymaganie: R5.
Powiązanie: UC-01 w docs/architecture.md.

## Cel

Rozszerzenie istniejącego wyboru scenariusza i dnia o wybór kompletnego run_id.
Dashboard korzysta z RunView, zamiast samodzielnie łączyć niesprawdzone pliki.

## Kryteria odbioru

- Widoczne są tylko kompletne przebiegi z poprawną wersją manifestu i hashami.
- Widok wskazuje run_id, stację, zakres pomiarów, czasy pobrania źródeł i created_at_utc.
- Reanaliza ERA5 jest odróżniona od pomiaru ze stacji; brak sugestii bieżących danych dla historycznej próbki.
- Ranking obejmuje do trzech godzin rozmytego wariantu z oryginalną etykietą TRENUJ.
- Remisy rozstrzyga wcześniejszy timestamp; filtr dnia używa Europe/Warsaw.
- Brak dnia, godzin TRENUJ lub uszkodzony zapis daje komunikat bez pozornej rekomendacji.
- Pobieranie CSV dotyczy tego samego przebiegu i scenariusza co widok.

Recenzent obszaru: Kacper Dąbek. Zależność: load_run i RunView z L5-02.
