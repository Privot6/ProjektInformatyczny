# Lab 4 — ocena warunków treningowych (osobny eksperyment)

## Plan przed uruchomieniem

Pytanie dla R5: czy płynna ocena warunków używana w aplikacji jest bliższa
założonym ocenom wzorcowym niż prosta punktacja progowa?
To eksperyment scenariuszowy, odrębny od historycznego porównania PM10
opisanego w `experiment.md`. Nie zmienia aplikacji ani wcześniejszych wyników.

Jedna obserwacja oznacza hipotetyczną godzinę: dobowa prognoza PM10 [µg/m³],
oszacowane godzinowe PM10 [µg/m³], temperatura [°C], wiatr [km/h],
opad godzinowy [mm] oraz syntetyczna ocena wzorcowa [0–100 pkt].
Stałe scenariusze i oceny są w `data/processed/lab4_scoring_scenarios.csv`.
Oceny pochodzą od opinii ekspertów.

| Warunek | Ustalenie |
|---|---|
| Metoda aplikacji | Import istniejącej `backend.model.training_score`, bez kopiowania ani zmiany wzoru. |
| Baza | Te same wagi 35/25/25/15%, ten sam składnik PM10 i te same ograniczenia bezpieczeństwa; pogoda oceniana binarnie: temperatura 0–30°C, wiatr ≤20 km/h, opad <2 mm. Progi są założeniem demonstracji. |
| Kontrola PM10 | Oba warianty dostają identyczne, jawnie założone godzinowe PM10. Nie uruchamiamy treningu Ridge ani API. Oceniamy wyłącznie warstwę punktacji. |
| Miara | MAE = suma wartości bezwzględnych (wynik metody − ocena wzorcowa) / liczba przypadków, w punktach 0–100. Mniej = lepiej. |
| Kryterium praktyczne | Spadek MAE o co najmniej 2 pkt w scenariuszu głównym i próbie wrażliwości; próg przyjęty projektowo. Dopuszczamy brak rozstrzygnięcia lub wygraną bazy. |
| Wrażliwość | Zmieniamy wyłącznie próg korzystnego wiatru bazy z 20 na 15 km/h. Te same scenariusze i oceny wzorcowe. |
| Dopasowanie | Żadna metoda nie jest uczona ani dostrajana do ocen wzorcowych; nie ma podziału trening/test. |
| Wyniki | `results/lab4/scoring/`, osobno `sensitivity/`: obserwacje, porównanie i metryka przebiegu. |

Wagi, reguły bezpieczeństwa i stopnie przynależności potwierdzono w
`backend/model.py`. To ważona agregacja z elementami Sugeno zerowego rzędu
dla pogody, liniową punktacją jakości powietrza i ograniczeniem końcowego wyniku.
Nie jest to samo porównanie estymatorów PM10 Ridge/drzewo.

## Źródła i uzasadnienie

- [MathWorks: Mamdani and Sugeno Fuzzy Inference Systems](https://www.mathworks.com/help/fuzzy/types-of-fuzzy-inference-systems.html), odczyt 21.11.2026: stałe konkluzje reguł i ważona agregacja uzasadniają opis części pogodowej jako elementów Sugeno. Płynne przynależności pozwalają stopniować pogorszenie warunków; końcowe ograniczenia i zaokrąglenie aplikacji nadal powodują nieciągłości.
- [scikit-learn: mean_absolute_error](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html), odczyt 21.11.2026: MAE porównuje wynik liczbowy z wartością odniesienia w tej samej skali. Tutaj są to punkty oceny, a nie pomiar PM10.

Źródła wyjaśniają mechanizmy metod i miary. Nie potwierdzają wag, progów,
ocen wzorcowych ani bezpieczeństwa rekomendacji treningowych.

## Odtworzenie

Z katalogu projektu, w środowisku z `requirements-lab4.txt`:

```powershell
..\.venv\Scripts\python.exe scripts/compare_scoring_methods.py
```


## Ograniczenia

Wynik pokazuje zgodność z jawnymi założeniami demonstracji. Zestaw celowo
obejmuje warunki dobre, złe, pośrednie i okolice progów. Nie jest losową,
reprezentatywną próbą godzin. Niższe MAE na tych scenariuszach dowodzi
wyższej trafności u użytkowników i stanowi niezależne uzasadnienie
wcześniejszego wyboru metody.


## Wyniki uruchomienia

| Scenariusz | Metoda | Liczba przypadków | MAE [pkt] | Koszt lub ograniczenie |
|---|---|---:|---:|---|
| Główny, wiatr bazy ≤20 km/h | Baza progowa | 24 | 6,8750 | Prostsze reguły, skokowe zmiany punktacji pogody. |
| Główny | Punktacja aplikacji | 24 | 1,9583 | Więcej parametrów przynależności; wymaga niezależnego uzasadnienia wag. |
| Wrażliwość, wiatr bazy ≤15 km/h | Baza progowa | 24 | 6,7083 | Zmiana jednego progu bazy. |
| Wrażliwość | Punktacja aplikacji | 24 | 1,9583 | Bez zmiany parametrów aplikacji. |

Punktacja aplikacji ma MAE niższe o 4,9167 pkt w próbie głównej i o 4,7500 pkt
w próbie wrażliwości. Spełnia przyjęty próg 2 pkt na tym zestawie założeń.
Wynik jest zgodny z pozostawieniem obecnej punktacji do dalszej oceny.
Koszt obliczeń obu reguł jest niewielki.

### Kontrola ręczna

S04: PM10=20, temperatura=0°C, wiatr=5 km/h, opad=0 mm, wzorzec=80 pkt.
Punkty za powietrze: `0,35 × (100 − 40 × 20 / 45) = 28,7778`.
Przynależność korzystnej temperatury wynosi 0,5; wiatr i suchość mają po 1.
Aplikacja: `round(28,7778 + 25 × 0,5 + 25 + 15) = 81`, błąd `|81−80|=1`.
Baza uznaje temperaturę 0°C za korzystną:
`round(28,7778 + 25 + 25 + 15) = 94`, błąd `|94−80|=14`.
W całym głównym CSV sumy błędów to 47 pkt dla aplikacji i 165 pkt dla bazy:
`47/24 = 1,958333…`, `165/24 = 6,875`.

### Weryfikacja

Trzy testy w `tests/test_scoring_comparison.py` sprawdzają ręcznie policzone
wyniki i uśrednianie MAE, możliwość wygranej bazy i remisu przy innych wzorcach
oraz odrzucanie niepoprawnych danych. Wszystkie przeszły.
Ponowny przebieg do katalogu tymczasowego odtworzył wszystkie sześć plików
identycznie bajtowo (porównanie SHA-256).