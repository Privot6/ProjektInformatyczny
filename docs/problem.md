# Problem projektu

## Użytkownik i decyzja

AeroRun wspiera biegaczy, rowerzystów, spacerowiczów i trenerów planujących aktywność na zewnątrz w Rzeszowie. Użytkownik chce wybrać godzinę treningu i zdecydować, czy trenować, ograniczyć wysiłek czy przełożyć wyjście.

## Obecna trudność

Prognozy jakości powietrza i pogody są rozproszone. Użytkownik musi sam powiązać dobową prognozę PM10 z godzinami, w których temperatura, opady i wiatr sprzyjają treningowi.

## Zakres problemu

Zakres podstawowy obejmuje miasto Rzeszów (TERYT 1863) oraz prognozę pogody dla współrzędnych 50.0413, 21.999. Dobowa średnia PM10 służy jako kontekst dla całego dnia. Godziny w obrębie dnia można porównywać według prognozy pogody. Analiza historycznej zależności PM10 od pogody wymaga dłuższej, wspólnej serii. Poza zakresem są diagnostyka medyczna, automatyczne sterowanie urządzeniami i modelowanie dyspersji zanieczyszczeń.

## Potrzebne dane

| Informacja | Do czego jest potrzebna? | Minimalny zakres | Format lub częstotliwość | Czy jest dostępna? |
|---|---|---|---|---|
| Prognozowane średnie stężenie PM10 | Informacja o jakości powietrza dla wybranego dnia (R1, R2, R5) | Co najmniej jedna doba dla Rzeszowa | JSON, jedna wartość na dzień w µg/m³ | tak, w próbce są trzy doby |
| Temperatura powietrza na 2 m | Ocena warunków pogodowych w poszczególnych godzinach (R1, R2, R5) | Godziny wybranego dnia w Rzeszowie | JSON, co godzinę, °C | tak, Open-Meteo |
| Opady | Wskazanie godzin z opadami (R1, R2, R5) | Godziny wybranego dnia w Rzeszowie | JSON, suma za poprzednią godzinę w mm | tak, Open-Meteo |
| Prędkość wiatru na 10 m | Ocena warunków pogodowych w poszczególnych godzinach (R1, R2, R5) | Godziny wybranego dnia w Rzeszowie | JSON, co godzinę, km/h | tak, Open-Meteo |
| Historyczne pary PM10 i pogody | Oszacowanie zależności statystycznej (R4) | Wiele porównywalnych obserwacji dla tej samej lokalizacji, z okresem dobranym do metody | Szereg we wspólnej rozdzielczości czasowej | częściowo, są przykładowe pomiary i reanaliza, a dwa wskazane endpointy zwracają bieżące prognozy |
| Rekomendacja treningowa | Podsumowanie danych w formie decyzji użytkownika (R5) | Wybrana doba, dobowe PM10 oraz dostępne godziny z pogodą | Etykieta i uzasadnienie | nie, wymaga obliczeń w projekcie |

## Założenia i pytania otwarte

- Prognoza PM10 dla miasta daje użytkownikowi kontekst dla Rzeszowa. Pogoda pochodzi z komórki modelu dla wskazanych współrzędnych. Warunki na konkretnej trasie mogą się różnić.
- Do zestawienia przyjmujemy datę lokalną `Europe/Warsaw`. Granicę doby w prognozie PM10 przyjmujemy roboczo według tej strefy. Odpowiedź API PM10 zawiera samą datę, więc założenie wymaga potwierdzenia u wydawcy.
- Jak długi okres i ile pełnych obserwacji potrzeba do analizy zależności PM10 od pogody?
- Jak ustalić i ocenić progi rekomendacji oraz kiedy pokazywać komunikat o niewystarczających danych?

## Wymagania

| ID | Wymaganie | Kryterium sprawdzenia | Źródło lub uzasadnienie | Status | Osoba |
|---|---|---|---|---|---|
| R1 | Użytkownik widzi w jednym miejscu prognozę PM10 oraz temperaturę, opady i wiatr dla Rzeszowa. | Dla 12.11.2026 próbka zawiera jedną średnią dobową PM10 i komplet trzech pól pogody dla 24 godzin lokalnych. Przy danych widnieją jednostki i częstotliwość. | Karta projektu i ustalony zakres danych | potwierdzone | @Privot6 |
| R2 | Pogoda i dobowa prognoza PM10 odnoszą się do tej samej daty lokalnej. | Godzina 11.11.2026 o 23:00 UTC trafia do 12.11.2026 w Rzeszowie. W tym dniu PM10 ma jedną wartość dobową. | Różna rozdzielczość i format czasu w źródłach | założenie | @kacperd02 |
| R3 | Użytkownik dostaje komunikat, gdy do oceny brakuje PM10 lub pogody. | Brak klucza daty PM10 albo `null` w polu pogodowym daje komunikat o brakujących danych. Zero opadów jest poprawną wartością. | Możliwe luki i niedostępność API | założenie | @korrnnel |
| R4 | Użytkownik może poznać siłę i kierunek historycznej zależności między pogodą a PM10. | Dla ustalonego historycznego okresu z porównywalnymi obserwacjami można zweryfikować liczebność, korelację i parametry regresji. | Cel analityczny karty projektu | pytanie | @maksym1144 |
| R5 | Użytkownik dostaje rekomendację `TRENUJ`, `OGRANICZ WYSIŁEK` albo `ZOSTAŃ W DOMU` i może porównać dostępne godziny. | Przypadki z różną pogodą i tą samą dobową wartością PM10 dają wyniki zgodne z udokumentowanymi regułami. Wynik podaje, że PM10 jest średnią dobową. | Cel użytkowy karty projektu | założenie | @maksym1144 |

Kolumna „Osoba” zawiera proponowanych opiekunów wymagań na podstawie wkładu widocznego w Git. Podział wymaga potwierdzenia przez zespół.
