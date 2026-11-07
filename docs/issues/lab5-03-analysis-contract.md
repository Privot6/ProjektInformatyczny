# L5-03 Koordynator analizy zgodny z kontraktem

Status: do realizacji.
Odpowiedzialny: Maksym Łazowski.
Wymaganie: R5.
Powiązanie: docs/lab5/contracts.md i docs/diagrams/uc01-sequence.mmd.

## Cel

Połączenie istniejącej walidacji i modeli z prepare_run, które zwraca wynik
dopiero po spójnym zapisie. Metody, progi i miary Lab 4 pozostają bez zmian.

## Kryteria odbioru

- Oba warianty i scenariusze korzystają z tych samych oryginalnych godzin.
- Parametr próby wrażliwości zmienia się w kopii konfiguracji, nie w podstawie.
- Znana próbka i ręczny przykład zachowują wyniki z tolerancją 1e-6.
- ValueError modelu nie jest zamieniany na score=0 ani domyślną etykietę.
- Błąd obliczeń nie publikuje katalogu, a RunRef jest zwracany dopiero po publikacji.
- R5 nie jest opisywane jako wykonanie regresji R4 ani prognoza przyszłego PM.

Recenzent obszaru: Kornel Łazowski. Zależność: uzgodniony interfejs RunStore z L5-02.
