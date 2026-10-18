# Problem projektu

## Użytkownik i decyzja
* **Użytkownicy:** Osoby aktywne fizycznie na świeżym powietrzu w miastach (biegacze, rowerzyści, spacerowicze), trenerzy grup biegowych oraz rodzice planujący wyjścia z dziećmi w okresach grzewczych.
* **Wspierana decyzja:** Wybór optymalnej godziny na trening zewnętrzny w ciągu doby oraz podjęcie jednoznacznej decyzji: `TRENUJ`, `OGRANICZ WYSIŁEK` lub `ZOSTAŃ W DOMU` na podstawie aktualnych i prognozowanych warunków smogowo-pogodowych.

## Obecna trudność
* Dane o stężeniach pyłów zawieszonych (PM2.5, PM10) oraz prognozy pogody (wiatr, temperatura, opady) są rozproszone w różnych serwisach.
* Aplikacje prezentują surowe szeregi czasowe bez wskazania statystycznej zależności pokazującej, jak siła wiatru i zmiana temperatury wpływają na przewiewanie smogu w konkretnej lokalizacji.
* Użytkownik podejmuje decyzję intuicyjnie, co skutkuje narażeniem układu oddechowego na smog lub niepotrzebną rezygnacją z treningu mimo pojawienia się sprzyjającego okna pogodowego.

## Zakres problemu
* **Zakres uwzględniony w projekcie (MVP):** Analiza danych godzinowych z jednej wybranej referencyjnej stacji pomiarowej w Polsce oraz odpowiadających jej współrzędnych geograficznych dla danych pogodowych. Obejmuje integrację pomiarów z ostatnich 48–72 godzin (oraz 7 dni tła pogodowego i 24h prognozy), wyliczenie korelacji i prostej regresji liniowej między warunkami meteo a pyłami oraz wyznaczenie rekomendacji treningowej na bieżący dzień.
* **Poza zakresem projektu:** Automatyczne sterowanie urządzeniami zewnętrznymi, diagnostyka medyczna oraz modelowanie dyspersji zanieczyszczeń w skali całego kraju.

## Potrzebne dane

| Informacja | Do czego jest potrzebna? | Minimalny zakres | Format lub częstotliwość | Czy jest dostępna? |
| :--- | :--- | :--- | :--- | :--- |
| Stężenie pyłów PM2.5 i PM10 | Ocena jakości powietrza, porównanie z normami WHO/GIOŚ i wyliczenie korelacji z pogodą | 1 stacja referencyjna w mieście, min. 48 ostatnich godzin | JSON, dane godzinowe (1h) | **częściowo** (dostępne bieżące serie 48–72h w API GIOŚ, ale występują pojedyncze braki pomiarowe `null`) |
| Temperatura powietrza (`temperature_2m`) | Analiza wpływu niskich temperatur (sezon grzewczy/inwersja) na poziom zanieczyszczeń oraz komfort treningu | Lokalizacja stacji pomiarowej, 7 dni historii + 24h prognozy | JSON, dane godzinowe (1h) | **tak** (publiczne API Open-Meteo) |
| Prędkość wiatru (`wind_speed_10m`) | Wyznaczenie zależności przewiewania smogu od siły wiatru | Lokalizacja stacji pomiarowej, 7 dni historii + 24h prognozy | JSON, dane godzinowe (1h) | **tak** (publiczne API Open-Meteo) |
| Opady atmosferyczne (`precipitation`) | Wykluczenie godzin z intensywnym deszczem/śniegiem z rekomendowanych okien treningowych i analiza wymywania pyłów | Lokalizacja stacji pomiarowej, 7 dni historii + 24h prognozy | JSON, dane godzinowe (1h) | **tak** (publiczne API Open-Meteo) |
| Zintegrowany wskaźnik wpływu pogody na smog i rekomendacja okna treningowego | Bezpośrednie wsparcie decyzji użytkownika bez konieczności ręcznej analizy dwóch źródeł | Połączony szereg godzinowy (min. 48h) + prognoza na bieżącą dobę | Tabela godzinowa / komunikat decyzyjny (1h) | **nie** (wymaga samodzielnej synchronizacji stref czasowych, oczyszczenia braków i obliczeń w projekcie) |

## Założenia i pytania otwarte
* **Założenie 1:** Pomiary z wybranej miejskiej stacji referencyjnej GIOŚ są reprezentatywne dla obszaru, w którym użytkownik planuje trening biegowy lub rowerowy.
* **Założenie 2:** Przyjęte progi norm WHO/GIOŚ (np. PM2.5 < 25 µg/m³, brak opadów, umiarkowany wiatr) wystarczają do jednoznacznej klasyfikacji godziny jako bezpiecznej (`TRENUJ`).
* **Pytanie otwarte 1:** Jaką maksymalną lukę czasową w pomiarach GIOŚ (np. 2 czy 4 godziny wartości `null` z rzędu) można bezpiecznie uzupełnić interpolacją, zanim system powinien wyświetlić ostrzeżenie o niepełnych danych?
* **Pytanie otwarte 2:** Czy okno 48–72 godzin wystarczy do zaobserwowania istotnej statystycznie korelacji między wiatrem a pyłami przy stabilnej pogodzie, czy konieczne będzie dogrywanie danych z 7 dni?

## Wymagania

| ID | Wymaganie | Kryterium sprawdzenia | Źródło lub uzasadnienie | Status | Osoba |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R1** | Użytkownik powinien mieć dostęp do połączonych danych godzinowych o stężeniu pyłów (PM10, PM2.5) oraz pogodzie (temperatura, wiatr, opady) dla wybranej lokalizacji. | Można sprawdzić, czy zestawienie zawiera co najmniej 48 połączonych rekordów godzinowych z obu źródeł bez błędów dopasowania dat. | Karta projektu – rozproszenie danych w osobnych aplikacjach | potwierdzone | `@login_osoba_1` |
| **R2** | System powinien ujednolicać znaczniki czasu z obu źródeł do wspólnej lokalnej strefy czasowej przed analizą. | Można sprawdzić, czy rekordy z API pogodowego (UTC) i smogowego odpowiadają dokładnie tej samej godzinie czasu lokalnego (`Europe/Warsaw`). | Dokumentacja źródeł / Karta projektu (ryzyko rozbieżności stref czasowych) | potwierdzone | `@login_osoba_2` |
| **R3** | System powinien wykrywać i obsługiwać brakujące wartości pomiarowe ze stacji jakości powietrza. | Można sprawdzić, czy pojawienie się wartości pustej (`null`) w danych ze stacji nie powoduje błędu obliczeń i zostaje odfiltrowane lub uzupełnione. | Wynik próby pobrania danych z API GIOŚ | potwierdzone | `@login_osoba_2` |
| **R4** | Użytkownik powinien otrzymać informację o sile i kierunku zależności statystycznej między prędkością wiatru oraz temperaturą a stężeniem pyłów. | Można sprawdzić, czy dla pobranej próbki wyliczany jest współczynnik korelacji liniowej oraz parametry równania regresji. | Karta projektu – brak analizy zależności w obecnych aplikacjach | potwierdzone | `@login_osoba_3` |
| **R5** | Użytkownik powinien otrzymać jednoznaczną rekomendację decyzyjną (`TRENUJ` / `OGRANICZ WYSIŁEK` / `ZOSTAŃ W DOMU`) wraz ze wskazaniem najkorzystniejszych godzin w ciągu doby. | Można sprawdzić, czy dla zadanych progów (np. PM2.5 < 25 µg/m³, brak opadów) system przypisuje właściwą etykietę decyzyjną dla każdej godziny. | Karta projektu – kryterium sukcesu i użyteczność rozwiązania | potwierdzone | `@login_osoba_4` |
