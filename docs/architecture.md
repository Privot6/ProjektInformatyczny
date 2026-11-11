# Architektura AeroRun

AeroRun korzysta z publicznych danych o PM10 i pogodzie dla Rzeszowa. Obliczenia działają lokalnie na zapisanych plikach.

| Etap | Wejście | Wynik i stan |
|---|---|---|
| Lab 2 | Prognoza dobowa IOŚ-PIB dla TERYT 1863 i prognoza godzinowa Open-Meteo | Zapisana odpowiedź z metadanymi w `data/raw/sample.json`. |
| Lab 3 | Surowa próbka prognoz | `scripts/prepare_forecast.py` zapisuje `data/processed/sample-clean.json` z datą lokalną, dobowym PM10 i godzinami pogody. |
| Lab 4, R4 | Próbka Lab 3 oraz historyczne pomiary GIOŚ i pogoda z `data/raw/lab4/` | `scripts/compare_methods.py` porównuje Ridge i drzewo regresyjne na wspólnych dobach. Ridge wybrano do dalszej oceny. |
| R5 | Dobowe PM10 i godziny pogody z Lab 3 | Planowany moduł decyzji treningowej. Wymaga uzgodnienia reguł i niezależnej oceny. |
| Lab 5 | Dane i wyniki obliczeń | Planowane wersjonowanie i prezentacja przebiegów. |

## UC-01 — Porównanie metod i odczyt wyniku

Lokalny użytkownik uruchamia CLI i sprawdza, która metoda ma niższy MAE na późniejszej części szeregu. Procedura sprawdza pochodzenie, jednostki i kompletność, dopasowuje modele na wcześniejszych datach oraz zapisuje porównanie, obserwacje, parametry i próbę wrażliwości. Próba na pliku Lab 3 jest oznaczona jako zastosowanie bez pomiarów referencyjnych. Błędne wejście przerywa obliczenia z komunikatem.

[Przepływ danych](diagrams/data-flow.mmd) · [Sekwencja docelowa](diagrams/uc01-sequence.mmd) · [Model plików](diagrams/file-model.mmd)

## Planowane wersjonowanie i odczyt

`RunStore` i `RunRef` mają zapewnić atomową publikację katalogu i zwrot identyfikatora po pełnym zapisie. `RunView` ma udostępniać tylko przebiegi z poprawnym manifestem. Wybrana data, źródło, rodzaj danych i jednostki powinny być jawne w widoku. Dashboard ma pokazać porównanie estymat i dostępny kontekst pogodowy. Rekomendacja R5 pozostaje osobnym zadaniem.

[Kontrakt](lab5/contracts.md) · [Model danych](lab5/data-model.md) · [ADR-001](decisions/001-storage.md) · [Eksperyment Lab 4](experiment.md)

## Zmiany do realizacji i przegląd

| Zmiana | Właściciel | Zgłoszenie |
|---|---|---|
| Niezmienne snapshoty odpowiedzi i metadanych | Dawid Jopek | [L5-01](issues/lab5-01-source-snapshots.md) |
| Wersjonowany zapis i kontrola spójności danych | Kacper Dąbek | [L5-02](issues/lab5-02-run-storage.md) |
| Koordynator analizy z odroczoną publikacją | Maksym Łazowski | [L5-03](issues/lab5-03-analysis-contract.md) |
| Wybór przebiegu i jawne daty w dashboardzie | Kornel Łazowski | [L5-04](issues/lab5-04-dashboard-history.md) |
| Przegląd przez innych członków zespołu | Kacper Dąbek | [L5-05](issues/lab5-05-review.md) |
