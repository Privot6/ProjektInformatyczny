# L5-03 Koordynator analizy zgodny z kontraktem

Status: do realizacji.
Odpowiedzialny: Maksym Łazowski.
Wymaganie: R4.
Powiązanie: docs/lab5/contracts.md i docs/diagrams/uc01-sequence.mmd.

## Cel

Połączenie istniejącej walidacji i modeli z prepare_run, które zwraca wynik
dopiero po spójnym zapisie. Obie metody, MAE i podział po datach wynikają z Lab 4.

## Kryteria odbioru

- Oba warianty i scenariusze korzystają z tych samych dat uczących i testowych.
- Parametr próby wrażliwości zmienia się w kopii konfiguracji, nie w podstawie.
- Znana próbka i ręczny przykład zachowują wyniki z tolerancją 1e-6.
- ValueError modelu daje komunikat o błędzie, bez zastępczej estymaty.
- Błąd obliczeń nie publikuje katalogu, a RunRef jest zwracany dopiero po publikacji.
- Próba zastosowania na Lab 3 jawnie wskazuje brak pomiarów do oceny błędu.

Recenzent obszaru: Kornel Łazowski. Zależność: uzgodniony interfejs RunStore z L5-02.
