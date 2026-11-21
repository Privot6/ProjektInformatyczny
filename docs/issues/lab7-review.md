# Przegląd Lab 7 i otwarte zadania odbioru

 Baza:`bd22946619a49ec0738e123c7222c40f6fc5305e`, gałąź `lab7`, roboczy diff.


## Sprawdzony fragment

`scripts/compare_scoring_methods.py`: `read_cases`, `evaluate`, `run` oraz
zmienione opisy pochodzenia ocen. Funkcje rozdzielają odczyt i walidację CSV,
obliczenia oraz zapis. Nazwy MAE wskazują punkty, a nie µg/m³. Obsługa błędów
wejścia pozostaje w `main`; brak nowych wyjątków i zależności. `training_score`
jest importowane z aplikacji, więc nie powielamy wzoru. Ręcznie sprawdzono S04
(81 pkt) i sumy błędów 47/165/161 dla 24 przypadków. Rzeczywisty problem
z interpretacją ocen poprawiono i ponowiono M16. Nie dodano sekretów,
ścieżek prywatnych ani połączeń zewnętrznych w konsoli manualnej.

## Otwarte: LAB7-02 — odbiór Androida i informacja o źródłach

Nie wykonano M14: na stanowisku nie znaleziono `adb`/działającego emulatora.
Przegląd `mobile/App.js` ujawnia, że ekran pokazuje etykietę cache, lecz nie
renderuje `warnings`, `retrieved_at_utc`, `pm10_notice` ani daty odpowiedzi.
Backend udostępnia te pola, ale odbiorca telefonu nie widzi czasu cache ani
ostrzeżenia o nieudanym zapisie. To ogranicza ocenę świeżości danych R1/R3.
Obejście techniczne: odczyt odpowiedzi przez Swagger; nie zastępuje to poprawki
ekranu. Zadanie: pokazać datę, czas źródeł i ostrzeżenia, następnie ręcznie
sprawdzić oba dni, brak połączenia i awarię zapisu na emulatorze/telefonie.
Nie oznaczamy tych elementów jako odebranych.

## Otwarte: LAB7-03 — niezależne uruchomienie i recenzja

Osoba inna niż autor ma skopiować projekt do nowego katalogu, utworzyć środowisko
z README, wykonać poprawne przetworzenie i przypadek błędnego pliku, następnie
M14. Zapisać własne imię, datę, commit, kroki i wynik w `docs/tests.md`.
Potem opublikować przegląd w rzeczywistym PR i dodać jego URL. 

## Otwarte: LAB7-04 — walidacja użyteczności

Brak niezależnych ocen treningowych i wielosezonowych danych. Wyniki z jednego
wydania prognozy oraz scenariuszy syntetycznych nie potwierdzają przydatności
rekomendacji w praktyce. R4 w mobilnym UI nie ma widoku korelacji i parametrów;
obecnie użytkownik znajdzie je w protokole Lab 4. Potrzebne osobne kryteria
i badanie. Ograniczenie nie jest błędem rachunku MAE.
