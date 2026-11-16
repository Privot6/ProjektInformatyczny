# LAB6 — integracja AeroRun

## Główny przepływ

Ekran dla Rzeszowa wysyła jedno żądanie GET do FastAPI po naciśnięciu SPRAWDŹ. Serwer przyjmuje wyłącznie /forecast/today i /forecast/tomorrow. Datę ustala według Europe/Warsaw. Dla obu dni pobiera równolegle prognozowane średnie dobowe PM10 z API IOŚ-PIB dla Rzeszowa (TERYT 1863) oraz trzy godzinowe pola Open-Meteo. Z odpowiedzi PM10 wybiera wyłącznie datę lokalną wskazanego dnia. [Opis API GIOŚ](https://powietrze.gios.gov.pl/pjp/content/api)

Kod pobierania korzysta z read_pm10 i read_weather w scripts/prepare_forecast.py. Dla pogody wysyła zakres dat UTC obejmujący całą lokalną dobę. Po walidacji jednostek i zakresów przypisuje tę samą średnią dobową PM10 wszystkim godzinom lokalnej daty. Opad dotyczy godziny poprzedzającej znacznik. Zera pozostają zerami, braki pozostają NULL. Ekran pokazuje lokalny offset, co rozróżnia jesienne powtórzenie godziny. [Dokumentacja Open-Meteo](https://open-meteo.com/en/docs)

## Model i interpretacja

Eksperyment LAB4 szacował *dobowe* PM10 z trzech cech. W LAB6 wejście to prognozowane średnie dobowe PM10 w µg/m³, temperatura w °C, wiatr w km/h i opad w mm w chwili t. Cel to rzeczywisty pomiar PM10 w t+1 h na tej samej stacji. Większe przewidywane stężenie oznacza mniejszą przydatność godziny pod względem zapylenia. W zbiorze nie ma ocen samopoczucia ani rezultatów treningów. Score łączy tę estymację z oceną komfortu pogodowego.

FastAPI łączy archiwalną prognozę IOŚ-PIB i pogodę z data/raw/sample.json z rzeczywistymi pomiarami GIOŚ stacji 16344 z data/raw/lab6/gios.json. Źródło i SHA-256 pomiarów zapisano w sources.json. Uwzględnia tylko godziny po pobraniu obu prognoz. Prognoza dobowa jest wspólna dla godzin jednej daty. Cel uczenia to obserwacja stacji z kolejnej godziny. StandardScaler i Ridge(alpha=1, solver="svd") dopasowano na 28 godzinach z 11–12 listopada, z wykluczeniem pary przekraczającej granicę testu. Na 24 godzinach 13 listopada MAE wyniosło 6,81 µg/m³ (użycie samej prognozy dobowej jako oszacowania godzinowego: 22,79 µg/m³). Trzy daty z jednego wydania prognozy nie pozwalają ocenić jakości w innych warunkach.

W score 35% pochodzi z prognozy Ridge przeliczonej na skalę 0–100 (100 − 40 × PM10 / 45 z ograniczeniem do zakresu). Reguły rozmyte Sugeno mają konsekwencje 100 i 0 punktów dla warunków korzystnych i niekorzystnych oraz dopełniające się stopnie przynależności. Temperatura ma wagę 25%. Pełna przynależność do zakresu komfortu obejmuje 5–25°C, a poza nim maleje liniowo do zera przy −5 i 35°C. Wiatr ma wagę 25% i pełną punktację do 10 km/h, stopniowo malejącą do zera przy 30 km/h. Opad ma wagę 15%, z liniowym przejściem od pełnej punktacji przy 0 mm do zera przy 4 mm. Stopnie przynależności pozostają w zakresie 0–1. Wagi i zakresy są założeniami projektowymi. Zaokrąglany jest wynik końcowy. Obowiązuje weto projektu dla prognozowanego średniego dobowego PM10 ≥112,5 µg/m³ lub opadu ≥4 mm: score może wtedy wynieść najwyżej 39. Klasy po zaokrągleniu wynoszą 70–100 TRENUJ, 40–69 OGRANICZ, 0–39 ZOSTAŃ W DOMU. Są to progi projektu. Wynik maksymalny wybierany jest z godzin o pełnych danych, przy remisie najwcześniejsza. Może to być godzina miniona. Wynik godziny historycznej opisuje to, co przewidziałby model przy jej danych.

## SQLite i obsługa błędów

Brakowało pliku bazy. Przy pierwszym starcie powstaje aerorun.sqlite3 z DDL LAB5. W istniejącym pliku migracja dodaje forecast_hour.pm10 i tabelę day_capture z czasem pobrania danego źródła dla konkretnego dnia. Aktualna wersja zapisuje prognozę raz w forecast_day.pm10_daily_mean. Przy odczycie cache rozpoznaje źródło ios_pib_pm10. Poprzednie godzinowe pomiary GIOŚ nie są używane jako średnie dobowe. Zapis zestawu godzin i metadanych odbywa się w jednej transakcji. Błąd zapisu daje ostrzeżenie, pozostawia wcześniejsze rekordy i pozwala wyświetlić poprawny wynik sieciowy. Backend przy błędzie źródła odczytuje wyłącznie dane tego źródła i wybranego dnia z cache. Pokazuje pochodzenie i czas. Przy całkowitym braku dostępu do obu źródeł i zapisu zwraca HTTP 503. Brak pomiarów po udanym pobraniu daje HTTP 200 z pustymi score.

## Weryfikacja i usprawnienie

- Integracja HTTP pierwotnej wersji godzinowej 15.11.2026: today i tomorrow zwróciły HTTP 200 i po 24 godziny. Żaden dzień nie miał kompletnego godzinowego PM10. Obce oznaczenie dnia otrzymało HTTP 422.
- Test integracyjny na zapisanych odpowiedziach API z 12.11.2026 potwierdza 24 godziny ze wspólną prognozą 31,59 µg/m³, maksymalny score, transakcyjny zapis i odtworzenie identycznego wyniku po błędzie sieci. Osobne testy obejmują migrację LAB5, 23-godzinną dobę, progi, błędny JSON źródłowy, brak danych i wycofanie rozpoczętego zapisu.
- Usprawnienie w backend/model.py: dla 24 pełnych godzin 24 osobnych wywołań predict zastąpiono jednym wywołaniem na macierzy 24 × 4. test_archive_day_batch_and_cache porównuje każdy wynik i komunikat z wariantem pojedynczym. Brak kompletnych wierszy oznacza zero wywołań predict. Ekran nigdy nie ładuje historycznych plików testowych jako danych dnia.

## Odbiór zespołowy

W pierwotnej wersji godzinowej 15.11.2026 zbudowano i zainstalowano debug APK x86_64 na Pixel 5 AVD z Androidem 16. Skrypt scripts/check_android.py uruchomił ekran, wybrał DZISIAJ i JUTRO oraz nacisnął SPRAWDŹ dla każdego dnia. Potwierdził osobne daty, etykiety źródeł i komunikat o braku godzinowej prognozy PM10. Lokalny Uvicorn działał na porcie 8765, Metro na 8081. SQLite zawierał 48 godzin pogody, 0 liczbowych PM10 i poprawny wynik integrity_check. Wszystkie 9 testów LAB3–6 zakończyło się powodzeniem, w tym sprawdzenie Retry-After. Podczas instalacji npm zgłosił 22 pozycje audytu w drzewie zależności SDK 52. Odbiór obejmował wersję deweloperską.

Proponowani właściciele według podziału LAB5. Poniższe pozycje służą do niezależnego odbioru. Wkład w LAB6 wymaga faktycznego Issue/PR i wyniku sprawdzenia przez daną osobę.

| Obszar | Osoba | Kryterium odbioru |
|---|---|---|
| Dane i Ridge | Maksym | Odtworzyć liczby godzin i MAE, sprawdzić kolejność cech i brak przecieku celu. |
| Ekran Android | Kornel | Uruchomić oba dni, awarię połączenia i ponowienie. |
| SQLite | Kacper | Potwierdzić migrację LAB5 i brak częściowego zapisu po błędzie. |
| Niezależny przegląd | Dawid | Sprawdzić diff i przepływ na drugim komputerze, zapisać wynik w PR, uruchomić po scaleniu. |
