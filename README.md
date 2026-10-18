# AeroRun – Analityczny asystent wyboru okna treningowego na podstawie danych smogowych (GIOŚ) i meteorologicznych (Open-Meteo)

**Specjalność:** Analiza Danych Społeczno-gospodarczych
**Zespół:** Dawid Jopek, Kornel Łazowski, Maksym Łazowski, Kacper Dąbek 
**Data opracowania:** 18.10.2026 r.

---

## Opis problemu

Osoby trenujące na zewnątrz (biegacze, rowerzyści) w polskich miastach w sezonie jesienno-zimowym są narażone na wysokie stężenia pyłów zawieszonych PM2.5 i PM10 oraz dynamiczne zmiany pogody. Obecnie dane o jakości powietrza i prognozy pogody znajdują się w osobnych aplikacjach i mają postać surowych wykresów bez analizy zależności między wiatrem, temperaturą a stężeniem zanieczyszczeń. W efekcie użytkownik podejmuje decyzję o wyjściu na trening intuicyjnie, narażając układ oddechowy na smog lub rezygnując z aktywności mimo sprzyjającego okna pogodowego.

## Cel i wartość rozwiązania

**AeroRun** zastępuje ręczne przeglądanie kilku źródeł jednym narzędziem wspierającym decyzję w modelu *Rekomendacja zamiast automatycznego sterowania*. Użytkownik otrzymuje:
* wyliczoną statystyczną zależność (współczynnik korelacji Pearsona oraz model regresji liniowej) pokazującą, jak prędkość wiatru i temperatura wpływają na przewiewanie smogu w jego lokalizacji,
* jednoznaczną rekomendację decyzyjną (`TRENUJ` / `OGRANICZ WYSIŁEK` / `ZOSTAŃ W DOMU`) wraz ze wskazaniem najkorzystniejszych godzin treningowych w ciągu doby na podstawie progów norm WHO/GIOŚ.

## Odbiorcy rozwiązania

* Osoby aktywne fizycznie na świeżym powietrzu w miastach (biegacze, rowerzyści, spacerowicze).
* Trenerzy grup biegowych.
* Rodzice planujący wyjścia z dziećmi w okresach grzewczych.

---

## Zespół projektowy i podział zadań

| Członek zespołu (GitHub) | Zakres odpowiedzialności | Mierzalny rezultat |
| :--- | :--- | :--- |
| `@login_osoba_1` | Pozyskiwanie i obsługa danych środowiskowych (API GIOŚ) | Moduł w Pythonie pobierający listę stacji oraz pomiary PM10/PM2.5 i zapisujący próbkę JSON (min. 48 rekordów godzinowych) |
| `@login_osoba_2` | Pozyskiwanie danych meteorologicznych (API Open-Meteo) i integracja zbiorów | Skrypt łączący dane pogodowe ze smogowymi w ramkę Pandas (`DataFrame`) z ujednoliceniem czasu (`Europe/Warsaw`) i czyszczeniem braków (`dropna`/interpolacja) |
| `@login_osoba_3` | Moduł analityczno-ekonometryczny i algorytm rekomendacji | Kod wyliczający korelację Pearsona, model regresji liniowej oraz reguły decyzyjne indeksu treningowego |
| `@login_osoba_4` | Interfejs użytkownika (Streamlit) i dokumentacja danych (`docs/data.md`) | Dashboard z wykresami i komunikatem decyzyjnym oraz opracowanie dokumentacji źródeł danych |

---

## Struktura repozytorium i dokumentacja

* 📄 [Analiza problemu i wymagania (`docs/problem.md`)](./docs/problem.md)
* 📊 [Analiza źródeł danych i pomysł realizacji (`docs/data.md`)](./docs
