# Plan pozyskania danych

| Element | Ustalenie |
|---|---|
| Źródło | Open-Meteo Forecast API `https://open-meteo.com/en/docs?latitude=50.0413&longitude=21.999&hourly=temperature_2m,precipitation,wind_speed_10m`,  API GIOŚ `https://api.prognozy.ios.edu.pl/v1/PM10/1863` |
| Właściciel danych | Open-Meteo; dane z modeli meteorologicznych udostępniane przez usługę |
| Zakres danych | `time`, `temperature_2m`, `wind_speed_10m`, `precipitation`; pomocniczo GIOŚ `pm25`, `pm10` |
| Okres i częstotliwość | Godzinowo, 7 dni wstecz + 1 dzień prognozy (parametry żądania) |
| Jednostka obserwacji | Jedna godzina dla wybranej lokalizacji |
| Dobór obserwacji i liczebność | Jedna lokalizacja: domyślnie Rzeszów (50.0413, 21.9990); minimum 48 wspólnych godzin z GIOŚ |
| Pobranie | `scripts/pobierz_open_meteo.py`; GET, parametry: `latitude`, `longitude`, `hourly`, `past_days=7`, `forecast_days=1`, `timezone=UTC` (następnie konwersja do Europe/Warsaw) |
| Limit, koszt, uprawnienia | Publiczny endpoint bez klucza dla zastosowania demonstracyjnego; aktualne limity i zasady komercyjne sprawdzić w regulaminie Open-Meteo |
| Licencja i publikacja | Warunki Open-Meteo należy potwierdzić przed publikacją danych rzeczywistych; dołączone próbki są syntetyczne |
| Plan awaryjny | Powtarzalna syntetyczna próbka `data/raw/open_meteo_syntetyczne.csv`; brak zależności od sieci w testach |


## Lab 4 Dane dla wnioskowania rozmytego

Eksperyment korzysta z niezmienionego data/processed/aerorun_dane.csv: 72 godziny
syntetyczne z Lab 3. Nie pobiera nowych pomiarów. Walidatory PM i pogody zapisują
odrębne raporty jakości i SHA-256. Definicje pól pozostają w data-dictionary.md,
a kontrakt wejścia w lab4_data.md i lab4_air.md.

PM2.5/PM10, temperatura, wiatr i opad są oceniane dla tej samej godziny.
Wynik nie jest prognozą ani oceną bezpieczeństwa medycznego. Parametry indeksu
to jawne założenia demonstracji w config/lab4.json. Pełny protokół, literatura,
wyniki porównania i ograniczenia są w experiment.md.
