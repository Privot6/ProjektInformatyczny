# Sprawdzenie techniczne paczek Lab 4

Data: 2 listopada 2026. Sprawdzenia wykonano w kopii repozytorium poza projektem.
Python 3.13, Windows; dokładne wersje zapisano w requirements-lab4-lock.txt.

- Audyt PM: 72 rekordy, brak ujemnych i nieskończonych wartości, 8 flag PM2.5 > PM10.
- Audyt wejścia: 72 unikatowe pełne godziny, ciągłość UTC i komplet wymaganych pól.
- Demonstracja centroidu: 90 dla najlepszego zestawu i 10 dla wysokiego PM.
- Eksperyment: po 72 godziny na wariant, 144 wiersze obserwacji w każdym scenariuszu.
- Kontrola wyników PM: zgodność oryginalnych wartości i perturbacji z wejściem;
  po 4 przechodzące kontrole na scenariusz, obejmujące obie metody.
- Odtworzenie Lab 3 w katalogu tymczasowym: te same 72 wiersze co w próbce.
- Dwa uruchomienia Lab 4: identyczne bajtowo CSV i JSON; wejście pozostało bez zmian.
- Testy unittest: 19/19 przeszło, łącznie z testami Lab 3 i interfejsu.
- Streamlit AppTest: oba scenariusze bez wyjątków, metryki i oznaczenie syntetyczności.

Testy obejmują błędne pomiary, flagi PM, niekompletne godziny, duplikaty,
zmianę czasu, centroid, pokrycie funkcji przynależności, ciągłość przy progu,
silny PM mimo dobrej pogody, odtwarzalność i niezmienność danych.
Testy interfejsu wymagały lokalnych gniazd pętli zdarzeń Streamlit, blokowanych
przez początkowy sandbox. Po dopuszczeniu tego lokalnego mechanizmu przeszły.
W bibliotece scikit-fuzzy 0.5.0 z NumPy 2.5.4 występuje ostrzeżenie deprecacji
dotyczące argumentu out; obliczenia i testy przechodzą. To ograniczenie zależności.

Nie sprawdzono skuteczności zdrowotnej, ruchu produkcyjnego ani działania na
rzeczywistych danych GIOŚ. Test interfejsu sprawdza działanie elementów i zmianę
scenariusza, nie zastępuje ręcznej oceny wyglądu w przeglądarce. Nie wykonano
commitów w imieniu zespołu. Student nadal sam sprawdza wynik jednostkowy.
