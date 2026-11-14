# Podział pracy i zadania Lab 5

| Osoba | Obszar | Zakres commita Lab 5 | Kryterium odbioru |
|---|---|---|---|
| Maksym (@maksym1144) | L5-01 — Opis operacji i interfejsów | [architecture.md](../architecture.md), sekcje „Granice i odpowiedzialności”, „UC-01” i „Interfejs aplikacji”, oraz cały [contracts.md](../lab5/contracts.md). | UC-01 opisuje naciśnięcie **Sprawdź**, pobranie z obu publicznych API oraz wynik. Kontrakt `checkForecast(date)` określa typy, jednostki i obsługę błędów. Przy implementacji ten obszar obejmuje pobieranie i walidację odpowiedzi. |
| Kornel (@korrnnel) | L5-02 — Diagram sekwencji UML i przepływ danych | [architecture.md](../architecture.md), sekcje „Sekwencja UML” i „Przepływ danych”. | Diagramy pokazują kliknięcie, pobranie z obu źródeł, walidację, zapis lokalny, widok wyniku i ścieżki błędne. Przy implementacji ten obszar obejmuje ekran React Native i jego stany. |
| Kacper (@kacperd02) | L5-03 — Model danych i lokalny zapis SQLite | Sekcja „Model danych i zapis” w [architecture.md](../architecture.md), [data-model.md](../lab5/data-model.md) z ERD i [schema.sql](../lab5/schema.sql). | ERD zgadza się z DDL i polami Lab 3. Zapis zestawu jest transakcyjny i zachowuje poprzednie dane przy błędzie. Przy implementacji ten obszar obejmuje lokalny magazyn SQLite. |
| Dawid (@Privot6) | L5-04 — Decyzja architektoniczna i niezależny przegląd spójności | [001-storage.md](../decisions/001-storage.md), [lab5-review.md](lab5-review.md) z wynikiem przeglądu i ten plik. W commicie porządkowym może też uwzględnić sekcję Lab 5 w [README](../../README.md) i usunięcia zastąpionych plików Lab 5. | ADR uzasadnia lokalną SQLite i omawia alternatywę w postaci pliku JSON. Dawid sprawdza dokumentację przygotowaną przez pozostałe osoby i zapisuje wynik, w tym przypadek poprawny oraz ścieżki błędne, w GitHub Issue. |

Kolejność edycji wspólnego `architecture.md` to **Maksym → Kornel → Kacper**, a potem **Dawid** robi przegląd. Każda osoba dodaje do swojego commita tylko własne sekcje wspólnego pliku. Przy już zapisanych zmianach można użyć opcji **Stage Selected Lines** w IDE i sprawdzić zakres poleceniem `git diff --cached`.

[Architektura](../architecture.md) · [Kontrakt](../lab5/contracts.md)
