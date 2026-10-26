# Plan pozyskania danych — zakres Kacpra

| Element | Ustalenie |
|---|---|
| Źródło | Open-Meteo Forecast API `https://api.open-meteo.com/v1/forecast` |
| Właściciel danych | Open-Meteo; dane z modeli meteorologicznych udostępniane przez usługę |
| Zakres danych | `time`, `temperature_2m`, `wind_speed_10m`, `precipitation`; pomocniczo GIOŚ `pm25`, `pm10` od Dawida |
| Okres i częstotliwość | Godzinowo, 7 dni wstecz + 1 dzień prognozy (parametry żądania) |
| Jednostka obserwacji | Jedna godzina dla wybranej lokalizacji |
| Dobór obserwacji i liczebność | Jedna lokalizacja: domyślnie Rzeszów (50.0413, 21.9990); minimum 48 wspólnych godzin z GIOŚ |
| Pobranie | `scripts/pobierz_open_meteo.py`; GET, parametry: `latitude`, `longitude`, `hourly`, `past_days=7`, `forecast_days=1`, `timezone=UTC` (następnie konwersja do Europe/Warsaw) |
| Limit, koszt, uprawnienia | Publiczny endpoint bez klucza dla zastosowania demonstracyjnego; aktualne limity i zasady komercyjne sprawdzić w regulaminie Open-Meteo |
| Licencja i publikacja | Warunki Open-Meteo należy potwierdzić przed publikacją danych rzeczywistych; dołączone próbki są syntetyczne |
| Osoba odpowiedzialna | Kacper Dąbek |
| Plan awaryjny | Powtarzalna syntetyczna próbka `data/raw/open_meteo_syntetyczne.csv`; brak zależności od sieci w testach |

Próbki `gios_syntetyczne.csv` i `open_meteo_syntetyczne.csv` są **sztucznie wygenerowane**. Nie odnotowano rzeczywistej daty pobrania z API, bo żądania sieciowego nie wykonano. Skrypt zapisuje datę pobrania i pełny URL do `open_meteo_odpowiedz_api.json` przy rzeczywistym pobraniu.

Współrzędne są domyślne dla przykładu, nie oznaczają potwierdzonego położenia stacji GIOŚ. Przy pracy z danymi Dawida należy je dopasować do jego stacji.
