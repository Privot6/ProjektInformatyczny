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


## Struktura repozytorium i dokumentacja

* 📄 [Analiza problemu i wymagania (`docs/problem.md`)](./docs/problem.md)
* 📊 [Analiza źródeł danych i pomysł realizacji (`docs/data.md`)](./docs/data.md)
* 📁 [Próbka danych z API GIOŚ i Open-Meteo (`data/sample.json`)](./data/sample.json)
  

```text
projekt-zespolu/
├── data/
│   └── sample.json
├── docs/
│   ├── problem.md
│   └── data.md
└── README.md
```
