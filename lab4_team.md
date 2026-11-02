# Podział Lab 4 według karty projektu

Zakres ról pochodzi z sekcji 8 przekazanej karty projektu. Metodę Lab 4 zmieniono
na wnioskowanie rozmyte zgodnie z aktualnym poleceniem użytkownika. Paczki są
materiałem przygotowanym przez AI do przeglądu, nie dowodem wkładu w repozytorium.

| Osoba | Zgodność z rolą | Rezultat do przeglądu i obrony | Nakład własnej pracy |
|---|---|---|---|
| Dawid Jopek | GIOŚ i dane środowiskowe | Walidacja PM, audyt pochodzenia i zakresu, testy błędnych pomiarów, kontrola przypadków wysokiego PM | orientacyjnie 3–4 h |
| Kacper Dąbek | Open-Meteo i integracja | Kontrakt pogody/czasu, audyt wejścia, test zmiany czasu i luk, metadane odtwarzalności | orientacyjnie 3–4 h |
| Maksym Łazowski | Analiza i rekomendacje | Konfiguracja funkcji przynależności, oba warianty, porównanie i wrażliwość, test centroidu | orientacyjnie 3–4 h |
| Kornel Łazowski | Interfejs i dokumentacja | Dashboard wyników, protokół z literaturą i interpretacją, instrukcja instalacji, test całości | orientacyjnie 3–4 h |

Nakład jest szacunkiem przeglądu, zrozumienia, ręcznej kontroli, uruchomienia i
omówienia, a nie deklaracją przepracowanych godzin. Moduł rozmyty naturalnie
pozostaje u Maksyma; pozostałe osoby przejmują porównywalne zadania weryfikacyjne
i dokumentacyjne blisko swoich ról. W razie trudności przy integracji rozdzielić
kontrolę pomiarów i odtwarzania między Dawida i Kacpra, bez przypisywania im
nieistniejącego autorstwa reguł.

## Integracja paczek

1. Najpierw zachować kopię bieżącego repozytorium lub utworzyć gałąź.
2. Rozpakować wszystkie cztery ZIP-y do katalogu głównego tej samej kopii.
   Ścieżki w archiwach są względne do katalogu głównego repozytorium.
   Nie rozpakowywać ich do czterech osobnych podfolderów projektu.
3. Pliki nie nakładają się między paczkami. Paczka Kornela zawiera pełny
   zaktualizowany README.md i docs/data.md, bazujące na dostarczonym repozytorium.
   Jeśli te dwa pliki zmieniono później, przenieść jedynie sekcję Lab 4.
4. Postępować według README: środowisko, instalacja, audyty, przykład, porównanie,
   testy, dashboard. Samodzielnie każda paczka nie stanowi pełnej aplikacji.
5. Każda osoba weryfikuje swoją część i wykonuje własny commit swoimi danymi.
   Nie tworzyć fikcyjnych commitów ani podpisów w imieniu innych osób.

## Granice zakresu

Lab 4 dotyczy R5 i stabilności demonstracyjnego indeksu. Nie dodaje działającego
API GIOŚ, prognozy PM, pełnego modelu regresji z R4 ani potwierdzonych medycznie
progów. R1–R3 pozostają pracą Lab 3. Nie zmieniono pierwotnej karty projektu.
Jeżeli wnioskowanie rozmyte ma zastąpić także obowiązek R4 całego projektu,
zespół musi później zaktualizować uzgodnione wymagania, nie uznawać ich za wykonane.
