# Przetwarzanie i kontrola jakości — Kacper Dąbek

## Dobór narzędzi
- Źródło i format: Open-Meteo JSON/CSV oraz przygotowany przez Dawida CSV/JSON GIOŚ.
- Narzędzie główne: Python + Pandas, ponieważ umożliwia powtarzalne łączenie godzinowych szeregów i testy.
- Pomocniczo: `requests` do pobierania API; nie jest konieczny Postman ani SQL.
- Wynik: `data/processed/aerorun_dane.csv`, `.json`.

## Transformacje
| Krok | Operacja | Powód | Wpływ |
|---|---|---|---|
| 1 | Parsowanie dat i konwersja na Europe/Warsaw | Różne strefy czasu | Wspólny klucz godzinowy; błędne daty są odrzucane/zgłaszane |
| 2 | Kontrola duplikatów godzin pogody i nieujemności wiatru/opadu | Uniknięcie ukrytych konfliktów i błędnych pomiarów | Niepoprawny plik jest odrzucany, bez zapisu wyniku |
| 3 | Interpolacja pojedynczych wewnętrznych braków pogodowych | Zachowanie krótkich przerw bez wstawiania zera | Wypełniane są tylko luki o maks. 1 obserwacji |
| 4 | Agregacja powtórzeń GIOŚ i interpolacja krótkich luk PM (maks. 2) | Zgodność kluczy i kompletność | Długie luki pozostają niekompletne |
| 5 | Łączenie po pełnej godzinie i odrzucanie niekompletnych wierszy | Wspólne obserwacje dla analizy | Pozostają tylko wspólne kompletne godziny |

## Kontrole automatyczne
1. `timestamp` jest unikatowy i niepusty w wyniku (oczekiwane: 0 naruszeń).
2. Wszystkie kolumny liczbowe są niepuste, PM/wiatr/opad nieujemne (oczekiwane: 0 naruszeń).
3. Wynik ma strefę Europe/Warsaw.
4. Powtarzalność: dwa uruchomienia na tych samych plikach mają dać identyczny bajtowo CSV.
5. Negatywny test `data/test/open_meteo_bledne.csv`: powtórzony timestamp i ujemny wiatr; oczekiwany błąd o duplikacie i brak pliku wynikowego.

## Ograniczenia i decyzje
- Próbki są **syntetyczne**; nie wyciągać wniosków o faktycznej jakości powietrza ani pogodzie.
- Wartości GIOŚ w próbce nie są danymi rzeczywistymi od Dawida. Prawdziwa integracja wymaga dopasowania stacji i okresu.
- Prognoza temperatury/wiatru nie jest prognozą PM. Nie interpolujemy długich braków, bo mogłoby to zniekształcić analizę.
- Przy jesiennej zmianie czasu lokalne znaczniki API bez offsetu mogą być niejednoznaczne. W rzeczywistej integracji preferować UTC lub dane z jednoznacznym offsetem.
- Decyzja: odrzucać nieprawidłowe wartości fizyczne i duplikaty pogody zamiast arbitralnie wybierać rekord.

Wyniki liczebności i testów są wypisywane po uruchomieniu `python scripts/prepare_data.py` i `python -m unittest discover -s tests -v`.
