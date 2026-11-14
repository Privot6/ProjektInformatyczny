# Przegląd projektu Lab 5 — UC-01

**Sprawdzony przypadek:** użytkownik wybiera 12.11.2026 i naciska **Sprawdź**. Aplikacja pobiera oba źródła, waliduje odpowiedzi i pokazuje PM10 31,59 µg/m³ oraz 24 godziny pogody według próbki Lab 3.

**Znaleziona niespójność i poprawa:** projekt zakładał cykliczny import przez FastAPI. Zgodnie z doprecyzowaniem pobranie odbywa się bezpośrednio w React Native na żądanie, a ostatni zestaw jest zapisywany lokalnie w SQLite.

**Do niezależnego przeglądu:** Dawid (@Privot6) prześledzi dokumentację przygotowaną przez Maksyma, Kornela i Kacpra. Sprawdzi poprawną datę, brak PM10, awarię jednego źródła i błąd zapisu oraz porówna kontrakt, ERD, SQL i pola Lab 3. Zapisze recenzenta, zakres, wynik i ewentualną poprawkę w GitHub Issue.

[Opis UC-01](../architecture.md) · [Kontrakt](../lab5/contracts.md)
