# Pozyskanie i ocena danych w Lab 2

## Tabela źródeł

| Źródło | Co można pobrać? | Czy odpowiada potrzebom? | Dowód sprawdzenia | Braki lub ryzyko |
|---|---|---|---|---|
| IOŚ-PIB, prognoza PM10 publikowana również przez GIOŚ (źródło podstawowe) | Średnie dobowe stężenie PM10 w µg/m³ dla miasta Rzeszowa (TERYT 1863) | częściowo. Pokrywa dane dobowe potrzebne w R1, R2 i R5. | [Endpoint PM10](https://api.prognozy.ios.edu.pl/v1/PM10/1863/), [dokumentacja GIOŚ](https://powietrze.gios.gov.pl/pjp/content/api), [kod TERYT w wykazie GUS](https://bip.stat.gov.pl/files/gfx/bip/pl/defaultstronaopisowa/142/1/1/wykaz_identyfikatorow_i_nazw_jednostek_podzialu_terytorialnego_kraju_01012015.pdf), [próbka](../data/sample.json) | Brak wartości godzinowych, strefy doby w odpowiedzi i historycznego okresu do R4. |
| Open-Meteo Forecast API (źródło uzupełniające) | Godzinowa temperatura na 2 m, opady i prędkość wiatru na 10 m dla 50.0413, 21.999 | tak dla danych pogodowych wymaganych w R1, R2 i R5. | [Endpoint prognozy](https://api.open-meteo.com/v1/forecast?latitude=50.0413&longitude=21.999&hourly=temperature_2m,precipitation,wind_speed_10m), [dokumentacja Open-Meteo](https://open-meteo.com/en/docs), [próbka](../data/sample.json) | Wynik modelu dla komórki siatki. Domyślne czasy są w GMT, a zakres zapytania przesuwa się wraz z datą. |

## Wyniki pobrania i ocena obu źródeł

| Element | PM10 z IOŚ-PIB | Prognoza pogody z Open-Meteo |
|---|---|---|
| Źródło i właściciel | Prognozę opracowuje i udostępnia IOŚ-PIB. Wyniki publikuje też GIOŚ. [Opis IOŚ-PIB](https://ios.edu.pl/jakosc-powietrza/) | Open-Meteo udostępnia prognozy z modeli meteorologicznych. [Dokumentacja API](https://open-meteo.com/en/docs) |
| Link lub sposób dostępu | GET z parametrami w ścieżce `PM10/1863/`. Pełny adres w tabeli źródeł i metadanych próbki. | GET z `latitude=50.0413`, `longitude=21.999` i `hourly=temperature_2m,precipitation,wind_speed_10m`. Pełny adres w tabeli źródeł i metadanych próbki. |
| Wymagania | R1, R2, R5. Brak daty obsługiwany według R3. | R1, R2, R5. Brak godziny lub wartości obsługiwany według R3. |
| Data i wynik pobrania | 11.11.2026, ok. 18:45 czasu polskiego, HTTP 200. | 11.11.2026, ok. 18:45 czasu polskiego, HTTP 200. |
| Format i kodowanie | Treść parsuje się jako JSON w UTF-8, nagłówek `text/html; charset=utf-8`. | JSON w UTF-8, nagłówek `application/json; charset=utf-8`. |
| Liczba rekordów w próbce | 3 dni, od 11 do 13 listopada 2026. | 168 godzin, od 11.11.2026 00:00 do 17.11.2026 23:00 GMT. |
| Nazwy pól i ich znaczenie | Klucze `20261111`, `20261112` i `20261113` oznaczają daty. Wartości 39,73, 31,59 i 37,07 oznaczają prognozowane średnie dobowe PM10. | `hourly.time` to znaczniki czasu, `temperature_2m` to temperatura na 2 m, `precipitation` to suma opadów za poprzednią godzinę, a `wind_speed_10m` to prędkość wiatru na 10 m. Tablice mają wspólny indeks. Odpowiedź podaje też jednostki w `hourly_units` oraz współrzędne komórki modelu (50.03909, 22.010834). |
| Format dat i jednostki | `YYYYMMDD`, bez informacji o strefie. Stężenie w µg/m³ według dokumentacji. | ISO 8601 w formacie `YYYY-MM-DDTHH:mm` w GMT, zgodnie z metadanymi odpowiedzi. Temperatura w °C, opady w mm, wiatr w km/h. |
| Braki, duplikaty i ciągłość | 3 różne, kolejne daty i 3 liczbowe wartości. Brak luk i wartości `null` w próbce. | 168 unikalnych znaczników w odstępach 1 h, trzy tablice o tej samej długości, 0 wartości `null`. Jednostki zgodne z dokumentacją. |
| Limit zapytań, klucz i koszt | Oba żądania wykonano bez klucza, logowania i opłaty. W dokumentacji endpointu prognoz nie znaleziono limitu ani cennika. | Publiczny endpoint bez klucza. Darmowy dostęp do celów niekomercyjnych. Limity 600/min, 5 000/h, 10 000/dobę i 300 000/miesiąc. [Warunki Open-Meteo](https://open-meteo.com/en/terms) |
| Licencja, wykorzystanie i prywatność | Próbka zawiera prognozy miejskie bez danych osobowych. Przytaczamy wydawcę, adres i datę pobrania. Dokumentacja IOŚ-PIB nie wskazuje odrębnej licencji dla endpointu. GIOŚ wymaga wskazania źródła przy ponownym wykorzystaniu informacji z portalu. [Dokumentacja GIOŚ](https://powietrze.gios.gov.pl/pjp/content/api) | Dane na CC BY 4.0, z podaniem źródła Open-Meteo i oznaczeniem ewentualnych zmian. Próbka zawiera dane pogodowe bez danych osobowych. [Warunki Open-Meteo](https://open-meteo.com/en/terms) |
| Próba ponownego pobrania | Wykonano 11.11.2026 tym samym adresem. HTTP 200, te same trzy daty i wartości. Kolejne wydania prognozy zmieniają daty lub wartości. | Wykonano 11.11.2026 tym samym adresem. HTTP 200, zgodne jednostki i początek serii. Późniejsze żądanie może zwrócić inną wersję prognozy. |

Plik [data/sample.json](../data/sample.json) zawiera metadane pobrania i treści pierwszych odpowiedzi po odczycie JSON. Wartości i nazwy pól zachowano. Do odtworzenia sprawdzenia wystarczy otworzyć zapisane adresy i porównać strukturę odpowiedzi z próbką.

## Braki i pomysł realizacji

| Element | Ustalenie |
|---|---|
| Wybrany pomysł realizacji | Prosty skrypt pobiera oba JSON-y, sprawdza format, jednostki i kompletność, po czym przelicza godziny pogody z GMT na `Europe/Warsaw` i zestawia je z PM10 według lokalnej daty. Wynik pokazuje średnią PM10 raz na dobę i listę godzin pogody dla tej daty. Oba źródła mają publiczny dostęp i czytelny format. |
| Odrzucony pomysł i powód | Godzinowe łączenie obu prognoz do regresji. Jedna dobowa wartość PM10 powielona dla 24 godzin dałaby pozorne obserwacje godzinowe. |
| Brakujące dane | Z prognozy dobowej nie da się odczytać zmian stężenia PM10 w ciągu dnia. Trzy daty prognozy są za krótką serią do R4. Analiza historyczna wymaga wspólnego okresu, np. pomiarów PM10 z GIOŚ i danych pogodowych z [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api). Przykład źródeł historycznych opisano w [metadanych](../data/raw/provenance.json). |
| Plan awaryjny | Przy niedostępności API użyć zapisanej próbki w trybie demonstracyjnym z widoczną datą pobrania. Jeżeli brakuje danych dla wybranego dnia lub godziny, oznaczyć brak i wstrzymać rekomendację opartą na niepełnym zestawie. |

## Weryfikacja rezultatów Lab 2

- README prowadzi do opisu problemu, oceny danych i próbki. W opisie problemu są dwie wymagane tabele, pięć wymagań i kryteria sprawdzenia.
- [Repozytorium jest publiczne](https://github.com/Privot6/ProjektInformatyczny). Wkład czterech osób można wskazać w historii Git. `@Privot6` uzupełnił opis źródeł (`ef0e925`), `@korrnnel` przygotował analizę danych (`bbe86d1`), `@maksym1144` uzupełnił opis problemu i przygotował pierwotną próbkę (`20e43dc`, `a07a495`), a `@kacperd02` opracował pobieranie i integrację pogody (`039fa58`). Lista aktualnych uprawnień współpracowników wymaga sprawdzenia w ustawieniach GitHub.
- Instrukcja Lab 2 wymaga przechowywania karty projektu poza publicznym repozytorium. `Karta_projektu_wypelniona.docx` jest nadal śledzona w Git i widoczna na GitHub.


## Lab 4 Dane dla wnioskowania rozmytego

Eksperyment korzysta z niezmienionego data/processed/aerorun_dane.csv: 72 godziny
syntetyczne z Lab 3. Nie pobiera nowych pomiarów. Walidatory PM i pogody zapisują
odrębne raporty jakości i SHA-256. Definicje pól pozostają w data-dictionary.md,
a kontrakt wejścia w lab4_data.md i lab4_air.md.

PM2.5/PM10, temperatura, wiatr i opad są oceniane dla tej samej godziny.
Wynik nie jest prognozą ani oceną bezpieczeństwa medycznego. Parametry indeksu
to jawne założenia demonstracji w config/lab4.json. Pełny protokół, literatura,
wyniki porównania i ograniczenia są w experiment.md.
