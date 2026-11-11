# Przetwarzanie i kontrola jakości

## Dobór narzędzi

Python 3.10+ odczytuje oba formaty odpowiedzi zapisane w [próbce Lab 2](../data/raw/sample.json). Moduł `json` zachowuje strukturę tablic i umożliwia wykrycie powtórzonych kluczy, a `zoneinfo` przelicza czas na `Europe/Warsaw`. Pakiet `tzdata` dostarcza reguły strefy na Windows. [Skrypt](../scripts/prepare_forecast.py) można uruchomić ponownie na tych samych danych bez zapytań do API.

## Kroki przetwarzania prognoz

| Krok | Operacja | Powód | Wpływ na dane |
|---|---|---|---|
| 1 | Walidacja kluczy JSON, jednostek, typów i zakresów | Wykrycie błędnego schematu, powtórzeń kluczy i wartości fizycznie niepoprawnych | Błąd przerywa przetwarzanie przed zapisem. Puste wartości pogodowe mogą pozostać jako `null`. |
| 2 | Zamiana równoległych tablic na rekordy i konwersja GMT/UTC do `Europe/Warsaw` | Jednoznaczny czas i wspólny lokalny klucz daty | Znaczniki mają offset. Godzina 11.11 o 23:00 GMT trafia do 12.11 o 00:00 czasu lokalnego. |
| 3 | Zestawienie źródeł po lokalnej dacie i uporządkowanie godzin | Zachowanie dobowej rozdzielczości PM10 i godzinowej rozdzielczości pogody | Dzień ma pojedyncze pole PM10 i listę godzin. W wyniku są daty występujące w co najmniej jednym źródle. |
| 4 | Oznaczenie braków bez uzupełniania prognozy | Użytkownik musi widzieć, gdzie dane są niepełne | Brak PM10 ma wartość `null`. Licznik `missing_weather_hours` uwzględnia brakujące godziny i godziny z niepełną pogodą. |

## Profil i wyniki kontroli

| Kontrola | Wynik | Działanie lub ograniczenie |
|---|---|---|
| Liczba i struktura rekordów | Wejście to 3 klucze dat PM10 i 4 równoległe tablice po 168 pozycji. Wynik to 8 lokalnych dat, 3 wartości PM10 i 168 rekordów godzinowych. | Skrypt porównuje liczebność godzin i wartości PM10 przed i po transformacji. |
| Brakujące wartości | Na wejściu 0 wartości `null`. W wyniku 5 dat bez PM10. Dni 11.11 i 18.11 zawierają odpowiednio 23 i 1 godzinę pogody. | Braki wynikają z różnych horyzontów prognoz oraz granic doby po konwersji. Dni 12–13.11 mają komplet 24 godzin i PM10. |
| Duplikaty | 0 powtórzonych kluczy JSON i 0 powtórzonych godzin w wyniku. | Obie kontrole są automatyczne. Próba na [błędnej kopii](../data/test/forecast-duplicate.json) miała wykryć powtórzenie godziny. Uzyskano komunikat `Powtórzony timestamp Open-Meteo po konwersji: 2026-11-11T01:00+01:00`, kod 1 i brak pliku wynikowego. |
| Zakresy, formaty i jednostki | 0 naruszeń. Temperatura w °C, opad w mm, wiatr w km/h, PM10 w µg/m³. | Skrypt sprawdza jednostki źródłowe, pełne godziny, liczby skończone, nieujemność PM10, wiatru i opadów oraz kontrolny przedział temperatury od −90 do 60 °C. |
| Zgodność kluczy | Każdy znacznik z offsetem należy do daty lokalnej swojego rekordu. | Automatyczna kontrola dat przed zapisem. Liczba oczekiwanych godzin uwzględnia długość lokalnej doby. |
| Otwarcie i powtarzalność | Wynik odczytano ponownie jako JSON. Dwa uruchomienia dały identyczną strukturę, wartości i liczebności oraz zgodny SHA-256. | Pierwszy [wynik porównawczy](../data/test/sample-clean-reference.json) przeniesiono poza katalog wynikowy. Drugi odtworzono poleceniem z README, gdy pliku wynikowego już tam nie było. |

## Odtworzenie i porównanie w PowerShell

Po instalacji zależności w katalogu głównym projektu można odtworzyć plik i sprawdzić jego zgodność z zachowaną kopią.

```powershell
python scripts/prepare_forecast.py
Get-FileHash -Algorithm SHA256 data/processed/sample-clean.json,data/test/sample-clean-reference.json
```

Oba pliki dały SHA-256 `62be7c7abb28c1f8128fc4d9f6decd73d8453a6b3a966194b5470b069df8cc01`.

## Ograniczenia

Na podstawie średniej dobowej nie można rozstrzygnąć, w której godzinie PM10 będzie najniższe. Trzy dobowe wartości nie wystarczają do analizy historycznej zależności pogody od PM10. Endpoint PM10 podaje daty bez informacji o granicy doby. W zestawieniu przyjęto roboczo datę polską zgodnie z Lab 2. Prognoza pogodowa pochodzi z modelu dla komórki siatki, więc na konkretnej trasie warunki mogą się różnić.

### Dobór narzędzi
- Źródło i format: Open-Meteo JSON/CSV oraz przygotowany przez Dawida CSV/JSON GIOŚ.
- Narzędzie główne: Python + Pandas, ponieważ umożliwia powtarzalne łączenie godzinowych szeregów i testy.
- Pomocniczo: `requests` do pobierania API; nie jest konieczny Postman ani SQL.
- Wynik: `data/processed/aerorun_dane.csv`, `.json`.

### Transformacje
| Krok | Operacja | Powód | Wpływ |
|---|---|---|---|
| 1 | Parsowanie dat i konwersja na Europe/Warsaw | Różne strefy czasu | Wspólny klucz godzinowy; błędne daty są odrzucane/zgłaszane |
| 2 | Kontrola duplikatów godzin pogody i nieujemności wiatru/opadu | Uniknięcie ukrytych konfliktów i błędnych pomiarów | Niepoprawny plik jest odrzucany, bez zapisu wyniku |
| 3 | Interpolacja pojedynczych wewnętrznych braków pogodowych | Zachowanie krótkich przerw bez wstawiania zera | Wypełniane są tylko luki o maks. 1 obserwacji |
| 4 | Agregacja powtórzeń GIOŚ i interpolacja krótkich luk PM (maks. 2) | Zgodność kluczy i kompletność | Długie luki pozostają niekompletne |
| 5 | Łączenie po pełnej godzinie i odrzucanie niekompletnych wierszy | Wspólne obserwacje dla analizy | Pozostają tylko wspólne kompletne godziny |

### Kontrole automatyczne
1. `timestamp` jest unikatowy i niepusty w wyniku (oczekiwane: 0 naruszeń).
2. Wszystkie kolumny liczbowe są niepuste, PM/wiatr/opad nieujemne (oczekiwane: 0 naruszeń).
3. Wynik ma strefę Europe/Warsaw.
4. Powtarzalność: dwa uruchomienia na tych samych plikach mają dać identyczny bajtowo CSV.
5. Negatywny test `data/test/open_meteo_bledne.csv`: powtórzony timestamp i ujemny wiatr; oczekiwany błąd o duplikacie i brak pliku wynikowego.

### Ograniczenia i decyzje
- Pomiary PM są rzeczywistymi danymi GIOŚ; pogoda jest reanalizą ERA5 Open-Meteo, nie pomiarem punktowym.
- Stacja: Rzeszów, al. Piłsudskiego, 10125. Okres: 20–22 października 2026. Źródła i parametry: data/raw/provenance.json.
- Prognoza temperatury/wiatru nie jest prognozą PM. Nie interpolujemy długich braków, bo mogłoby to zniekształcić analizę.
- Przy jesiennej zmianie czasu lokalne znaczniki API bez offsetu mogą być niejednoznaczne. W rzeczywistej integracji preferować UTC lub dane z jednoznacznym offsetem.
- Decyzja: odrzucać nieprawidłowe wartości fizyczne i duplikaty pogody zamiast arbitralnie wybierać rekord.

Wyniki liczebności i testów są wypisywane po uruchomieniu `python scripts/prepare_data.py` i `python -m unittest discover -s tests -v`.


### Wynik kontroli zapisanej próbki

Wejście: 72 pomiary PM2.5 i 72 pomiary PM10 oraz 72 wspólne godziny pogody.
Archiwalny czas GIOŚ CET przeliczono do Europe/Warsaw; czas Open-Meteo z UTC
do Europe/Warsaw. Po integracji: 72 godziny, zero braków i duplikatów, poprawne
jednostki i zakresy. Nie było potrzeby interpolacji. Surowe odpowiedzi JSON
pozostawiono bez zmian. Źródła, czas pobrania i hashe są w data/raw/provenance.json.
