# Analiza źródeł danych i pomysł realizacji

## 1. Zidentyfikowane źródła danych

| Źródło | Co można pobrać? | Czy odpowiada potrzebom? | Dowód sprawdzenia | Braki lub ryzyko |
| :--- | :--- | :--- | :--- | :--- |
| **Publiczne API GIOŚ** (Portal Jakości Powietrza) | Lista stacji pomiarowych, stanowiska (czujniki) oraz godzinowe pomiary stężeń pyłów PM10 i PM2.5 z ostatnich 48–72h w formacie JSON. | **częściowo** | Pobrano próbkę do `data/sample.json` (endpoint `getData/{sensorId}`). | Pojedyncze braki pomiarowe (`null`) w ostatnich godzinach, ograniczony horyzont historii w pojedynczym zapytaniu (48–72h) oraz ryzyko czasowej niedostępności API. |
| **Publiczne API Open-Meteo** | Godzinowe dane historyczne (np. z ostatnich 7 dni) oraz prognoza (24h+) dla temperatury (`temperature_2m`), prędkości wiatru (`wind_speed_10m`) i opadów (`precipitation`) w formacie JSON. | **tak** | Pobrano próbkę do `data/sample.json` (endpoint `/v1/forecast`). | Domyślny zapis czasu w strefie UTC wymaga jawnej konwersji na strefę lokalną (`Europe/Warsaw`) przy łączeniu z danymi GIOŚ. |

---

## 2. Ocena źródeł według pytań kontrolnych

### Źródło 1: API GIOŚ (Główny Inspektorat Ochrony Środowiska)

| Obszar | Pytanie kontrolne | Wynik sprawdzenia |
| :--- | :--- | :--- |
| **Dopasowanie do problemu** | Czy źródło zawiera dane potrzebne do realizacji konkretnego wymagania? | Obsługuje wymagania **R1**, **R3**, **R4** i **R5** w zakresie rzeczywistych stężeń PM2.5 i PM10. Odpowiada potrzebom częściowo, ponieważ udostępnia bieżące serie (48–72h) bez bezpośredniej prognozy smogowej na kolejne godziny. |
| **Właściciel i znaczenie danych** | Kto publikuje dane? Co oznaczają pola, jednostki i daty? | Dane publikuje Główny Inspektorat Ochrony Środowiska (GIOŚ). Pole `key` oznacza kod zanieczyszczenia (`PM10` lub `PM2.5`), `date` to lokalny znacznik czasu pomiaru (`YYYY-MM-DD HH:MM:SS`), a `value` to stężenie wyrażone w µg/m³. |
| **Jakość** | Czy występują braki, duplikaty, błędne jednostki, niepełne okresy albo nieaktualne rekordy? | Najnowszy rekord godzinowy często zawiera wartość `null` (trwający pomiar lub kalibracja czujnika). Sporadycznie występują pojedyncze luki w środku szeregu czasowego. |
| **Dostęp i koszt** | Ile zapytań można wykonać? Czy wymagany jest klucz, logowanie albo opłata? | Dostęp jest całkowicie darmowy, publiczny i nie wymaga klucza API ani logowania. Zbyt częste odpytywanie może jednak skutkować blokadą lub błędem połączenia. |
| **Licencja i prywatność** | Czy można użyć danych w projekcie i czy nie zawierają danych osobowych? | Dane stanowią informację sektora publicznego (otwarte dane publiczne) i można je legalnie wykorzystywać w projekcie akademickim. Zbiór zawiera wyłącznie pomiary środowiskowe i jest całkowicie wolny od danych osobowych. |
| **Powtarzalność** | Czy inna osoba może ponownie pobrać podobne dane, korzystając z zapisanego adresu, parametrów i daty? | Tak, wywołanie tego samego adresu URL dla wybranego identyfikatora stanowiska (`sensorId`) zwraca identyczną strukturę JSON z bieżącymi pomiarami z ostatnich kilkudziesięciu godzin. |

### Źródło 2: API Open-Meteo

| Obszar | Pytanie kontrolne | Wynik sprawdzenia |
| :--- | :--- | :--- |
| **Dopasowanie do problemu** | Czy źródło zawiera dane potrzebne do realizacji konkretnego wymagania? | W pełni obsługuje wymagania **R1**, **R2**, **R4** i **R5**. Dostarcza zarówno historię z 7 dni (`past_days=7`), jak i prognozę na kolejną dobę (`forecast_days=1`) w rozdzielczości godzinowej. |
| **Właściciel i znaczenie danych** | Kto publikuje dane? Co oznaczają pola, jednostki i daty? | Dane udostępnia serwis Open-Meteo (integrujący oficjalne modele numeryczne, m.in. DWD/IMGW/NOAA). Pola w obiekcie `hourly`: `time` (data i godzina w ISO 8601), `temperature_2m` (temperatura na wys. 2 m w °C), `wind_speed_10m` (prędkość wiatru na wys. 10 m w km/h), `precipitation` (suma opadów w mm). |
| **Jakość** | Czy występują braki, duplikaty, błędne jednostki, niepełne okresy albo nieaktualne rekordy? | Szeregi czasowe są kompletne (brak wartości `null`), z jednostajnym krokiem 1 godziny i jednoznacznie zdefiniowanymi jednostkami w obiekcie `hourly_units`. |
| **Dostęp i koszt** | Ile zapytań można wykonać? Czy wymagany jest klucz, logowanie albo opłata? | Do zastosowań niekomercyjnych i edukacyjnych API jest darmowe i nie wymaga klucza API. Limit wynosi do 10 000 zapytań dziennie, co wielokrotnie przewyższa potrzeby projektu. |
| **Licencja i prywatność** | Czy można użyć danych w projekcie i czy nie zawierają danych osobowych? | Dane są udostępniane na licencji Creative Commons Attribution 4.0 International (CC BY 4.0). Brak jakichkolwiek danych osobowych. |
| **Powtarzalność** | Czy inna osoba może ponownie pobrać podobne dane, korzystając z zapisanego adresu, parametrów i daty? | Tak, przekazanie tych samych współrzędnych (`latitude`, `longitude`), strefy czasowej (`timezone=Europe/Warsaw`) oraz parametrów zwraca identyczną strukturę JSON. |

---

## 3. Szczegółowy opis sprawdzonych źródeł i próbki (`data/sample.json`)

| Element | Wynik sprawdzenia |
| :--- | :--- |
| **Źródło i właściciel** | 1. Główny Inspektorat Ochrony Środowiska (GIOŚ) – Portal Jakości Powietrza.<br>2. Open-Meteo – otwarte API meteorologiczne. |
| **Link lub sposób dostępu** | 1. GIOŚ (HTTP GET): `https://api.gios.gov.pl/pjp-api/rest/data/getData/{sensorId}`.<br>2. Open-Meteo (HTTP GET): `https://api.open-meteo.com/v1/forecast?latitude=50.06&longitude=19.94&hourly=temperature_2m,wind_speed_10m,precipitation&past_days=2&forecast_days=1&timezone=Europe%2FWarsaw`. |
| **Wymaganie, które źródło obsługuje** | **R1** (integracja danych smogowych i pogodowych), **R2** (synchronizacja czasu), **R3** (obsługa luk pomiarowych), **R4** (analiza korelacji/regresji), **R5** (rekomendacja okna treningowego). |
| **Data pobrania** | 18.10.2026 r. |
| **Format i kodowanie** | Format `JSON`, kodowanie znaków `UTF-8`. |
| **Liczba rekordów w próbce** | Docelowo min. 48 rekordów godzinowych w pełnym pobraniu (w pliku `data/sample.json` zapisano reprezentatywny wycinek godzinowy potwierdzający strukturę obu odpowiedzi oraz połączonych rekordów). |
| **Nazwy pól i ich znaczenie** | **GIOŚ:** `key` (kod pyłu: `PM2.5`, `PM10`), `values[].date` (data i godzina pomiaru), `values[].value` (stężenie pyłu).<br>**Open-Meteo:** `hourly.time` (wektor czasu), `hourly.temperature_2m` (temperatura na 2 m), `hourly.wind_speed_10m` (wiatr na 10 m), `hourly.precipitation` (opady). |
| **Format dat i jednostki** | **GIOŚ:** daty `YYYY-MM-DD HH:MM:SS` (czas lokalny), jednostka: `µg/m³`.<br>**Open-Meteo:** daty `YYYY-MM-DDTHH:MM` (ISO 8601), jednostki: temperatura w `°C`, wiatr w `km/h`, opady w `mm`. |
| **Brakujące wartości lub rekordy** | W odpowiedzi GIOŚ ostatni rekord często ma wartość `"value": null` (opóźnienie spływu danych ze stacji); w Open-Meteo brak brakujących wartości. |
| **Limit zapytań, klucz i koszt** | Oba źródła są darmowe, nie wymagają klucza API ani rejestracji. Limit Open-Meteo: 10 000 zapytań/dzień (niekomercyjnie). |
| **Licencja i ograniczenia wykorzystania** | GIOŚ: otwarte dane publiczne (ponowne wykorzystywanie informacji sektora publicznego). Open-Meteo: licencja CC BY 4.0 (wymagane podanie źródła). Brak danych osobowych w obu źródłach. |
| **Próba ponownego pobrania** | **Wykonano** – wywołanie zapytań z innego komputera w zespole zwraca tę samą strukturę pól i typów danych. |
| **Brakujące dane** | API GIOŚ nie zwraca prognozy stężenia pyłów na kolejne 24h, a jedynie pomiary historyczne z ostatnich 48–72h. |
| **Plan awaryjny** | 1. Zapisanie lokalnej próbki danych (`data/sample.json`) jako pliku awaryjnego (*fallback*) na wypadek niedostępności API GIOŚ podczas prezentacji.<br>2. Filtrowanie braków (`dropna` / interpolacja liniowa) oraz jawna konwersja czasu do strefy `Europe/Warsaw`. |
| **Wybrany pomysł realizacji** | **Pobieranie danych z API** połączone z wariantem **Rekomendacja zamiast automatycznego sterowania** oraz **Lekki skrypt lub usługa lokalna** (aplikacja w Pythonie z interfejsem Streamlit uruchamiana lokalnie, z zapisaną próbką awaryjną JSON). |
| **Odrzucony pomysł i powód** | 1. **Wykorzystanie własnych czujników domowych (smart):** odrzucono ze względu na koszt zakupu sprzętu, brak kalibracji referencyjnej i ograniczenie pomiaru do jednego balkonu zamiast obszaru miasta.<br>2. **Automatyczne sterowanie (np. blokada treningu w urządzeniu użytkownika):** odrzucono ze względu na ryzyko błędnej decyzji przy awarii czujnika – bezpieczniejsza i bardziej użyteczna jest czytelna rekomendacja wspierająca decyzję człowieka. |

---

## 4. Podział pracy w zespole przy analizie źródeł

| Osoba | Analizowane źródło lub aspekt danych | Rezultat w repozytorium |
| :--- | :--- | :--- |
| `@login_osoba_1` | Analiza API GIOŚ (endpointy stacji, stanowisk i pomiarów PM10/PM2.5, identyfikacja luk `null`) | Weryfikacja struktury odpowiedzi GIOŚ w `data/sample.json` oraz opis źródła GIOŚ w `docs/data.md` |
| `@login_osoba_2` | Analiza API Open-Meteo, weryfikacja formatów dat (`ISO 8601` vs `YYYY-MM-DD HH:MM:SS`) i stref czasowych | Zapisanie próbki pogodowej w `data/sample.json`, opis źródła Open-Meteo oraz wymagań R2 i R3 |
| `@login_osoba_3` | Definicja problemu decyzyjnego, dobór zmiennych do korelacji/regresji oraz progów norm WHO/GIOŚ | Opracowanie sekcji merytorycznych i tabeli wymagań w `docs/problem.md` |
| `@login_osoba_4` | Ocena ograniczeń źródeł, licencji, planu awaryjnego (*fallback*) oraz koncepcji prezentacji rekomendacji | Zestawienie porównawcze źródeł, wybór wariantu realizacji w `docs/data.md` oraz przygotowanie `README.md` |
