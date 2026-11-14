# Kontrakt modułu sprawdzania prognoz

Ekran React Native wywołuje `checkForecast(date: string): Promise<ForecastCheckResult>` wyłącznie po naciśnięciu **Sprawdź**. `date` to poprawna data kalendarzowa `YYYY-MM-DD` w strefie `Europe/Warsaw`. Moduł pobiera dwa JSON-y przez HTTPS według [adresów z Lab 2](../data.md). Miasto to Rzeszów, TERYT 1863.

| Pole wyniku | Typ i znaczenie |
|---|---|
| `day` | Obiekt dnia według [słownika Lab 3](../data-dictionary.md#wynik-lab-3) albo `null`, gdy dzień jest niedostępny. |
| `day.date` | Data lokalna `YYYY-MM-DD`. |
| `day.pm10_daily_mean` | Dobowa wartość w µg/m³ albo `null`. |
| `day.weather` | Lista godzin. Każda ma `timestamp` z offsetem, `temperature_2m` w °C, `precipitation` w mm za poprzednią godzinę, `wind_speed_10m` w km/h. Wartości liczbowe są skończone. Brak pola pomiarowego ma wartość `null`. |
| `day.missing_weather_hours` | Liczba godzin doby pomniejszona o godziny z kompletem trzech wartości. Doba może mieć 23, 24 albo 25 godzin. |
| `origin` | `network`, `cache` albo `null`, zgodnie z pochodzeniem zwróconego dnia. |
| `retrieved_at_utc` | Dwa czasy pobrania ISO 8601 UTC pod kluczami `ios_pib_pm10` i `open_meteo`, albo `null`, gdy wynik nie zawiera dnia. |
| `issue` | Kod problemu albo `null`. |

Moduł sortuje godziny według chwili UTC. Jesienią powtórzona lokalna godzina ma dwa offsety. Zero opadów jest poprawną wartością.

| Sytuacja | Zachowanie |
|---|---|
| Błędna data | `INVALID_DATE`. Brak żądań i odczytu cache. |
| Poprawne pobranie, ale brak wybranej daty | `DATE_NOT_AVAILABLE`. Ekran pokazuje komunikat o braku prognozy dla dnia. |
| Błąd sieci, limit źródła lub niepoprawna odpowiedź | `FETCH_FAILED` albo `INVALID_SOURCE_DATA`. Jeżeli SQLite zawiera żądany dzień, dołącz go z `origin=cache`. Ponowienie odbywa się przyciskiem. Gdy źródło zwróci 429 z `Retry-After`, poczekaj wskazany czas przed ponowieniem. |
| Błąd lokalnego zapisu | `CACHE_WRITE_FAILED`. Poprzedni zestaw pozostaje w bazie. Jeśli nadeszły poprawne dane dla dnia, ekran nadal może je wyświetlić z `origin=network` i informacją o błędzie zapisu. |

Przykład na [próbce Lab 3](../../data/processed/sample-clean.json) dla `2026-11-12` daje `pm10_daily_mean=31.59`, `missing_weather_hours=0` i 24 godziny. Pierwsza godzina `2026-11-12T00:00+01:00` ma temperaturę 4,5 °C, opad 0 mm i wiatr 9,7 km/h.
