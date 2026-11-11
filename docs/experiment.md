# Lab 4 — Porównanie modeli estymujących dobowe PM10 w Rzeszowie

## Pytanie i wymaganie

Czy płytkie drzewo regresyjne szacuje średnie dobowe stężenie PM10 z temperatury, wiatru i opadów dokładniej niż regresja liniowa Ridge na późniejszych dniach? Porównanie dotyczy [R4](problem.md#wymagania), czyli historycznego związku pogody z PM10. Współczynniki Ridge pokazują kierunek i wielkość związku w modelu. Celem jest wybór metody do dalszej oceny.

## Literatura

| Źródło | Co wyjaśnia | Założenie lub ograniczenie | Zastosowanie |
|---|---|---|---|
| Zespół scikit-learn, *Ridge*, dokumentacja online, odczyt 11.11.2026. [Dokumentacja](https://scikit-learn.org/1.7/modules/generated/sklearn.linear_model.Ridge.html) | Regresja liniowa z karą L2 za duże współczynniki. | Skala cech wpływa na wielkość kary, a liniowość ogranicza postać modelu. | Standaryzacja pogody na danych uczących i Ridge jako prosty wariant bazowy. |
| Zespół scikit-learn, *DecisionTreeRegressor*, dokumentacja online, odczyt 11.11.2026. [Dokumentacja](https://scikit-learn.org/1.7/modules/generated/sklearn.tree.DecisionTreeRegressor.html) | Drzewo dzieli przestrzeń cech i zwraca średnią celu w liściu przy kryterium błędu kwadratowego. | Głębokie drzewo może dopasować się do szumu. | Limit głębokości i minimalna liczebność liścia. |
| Zespół scikit-learn, *Lagged features for time series forecasting*, dokumentacja online, odczyt 11.11.2026. [Przykład](https://scikit-learn.org/stable/auto_examples/applications/plot_time_series_lagged_features.html) | Ocena modelu na późniejszych obserwacjach i stosowanie MAE. | Sąsiednie obserwacje w czasie mogą być zależne. | Rozdzielenie danych w czasie i raportowanie błędu na wspólnym okresie. |

Ridge daje prostą zależność liniową i trzy współczynniki do interpretacji. Drzewo sprawdza, czy podziały według pogody poprawiają wynik. Las losowy pominięto, bo seria obejmuje dwa miesiące, a zadanie zakłada porównanie dwóch metod o jawnych parametrach.

## Warunki porównania

| Element | Co należy ustalić? |
|---|---|
| Pytanie i wymaganie projektu | Czy drzewo regresyjne szacuje średnie dobowe PM10 w Rzeszowie dokładniej niż Ridge na późniejszych dniach? Wynik wspiera wybór metody do dalszej oceny w ramach [R4](problem.md#wymagania). |
| Dane | Jedna obserwacja to lokalna doba w Rzeszowie. Z 61 dób w okresie 01.09–31.10.2026 wykorzystano 47 kompletnych. Cel to średnia z godzinowych pomiarów PM10 GIOŚ na stanowisku 16344, a cechy to dobowe średnie temperatury na 2 m i prędkości wiatru na 10 m oraz suma opadów z Open-Meteo. [Pliki źródłowe, daty pobrania i SHA-256](../data/raw/lab4/sources.json). [Próbka Lab 3 do próby zastosowania](../data/processed/sample-clean.json). |
| Wariant bazowy i metoda | **Ridge (bazowy)** dopasowuje liniową zależność między trzema cechami pogody a PM10 z karą L2. **Drzewo regresyjne** dzieli obserwacje według cech pogody i zwraca średnią PM10 z dni uczących w danym liściu. |
| Parametry i założenia | Ridge ma `alpha=1` i solver SVD. Standaryzację dopasowano wyłącznie na zbiorze uczącym. Drzewo używa błędu kwadratowego, `max_depth=3`, `min_samples_leaf=5` i `random_state=42`. Ujemne oszacowania obu modeli zastępowano zerem. |
| Miara i kierunek poprawy | Średni błąd bezwzględny (MAE) względem pomiarów GIOŚ, w µg/m³. Niższa wartość oznacza lepszy wynik. |
| Kryterium praktyczne | Drzewo uzasadnia dodatkową złożoność, jeżeli obniża MAE względem Ridge o co najmniej 1,0 µg/m³ w obu scenariuszach, przy tych samych danych wejściowych. Próg jest założeniem projektu. |
| Warunki oceny | Chronologiczny podział na 28 kompletnych dób uczących z okresu 01.09–11.10.2026 i 19 kompletnych dób testowych z okresu 12.10–31.10.2026. Obie metody ocenia się na tych samych datach. Pominięte doby są wymienione w [metryce przebiegu](../results/lab4/run.json). |
| Próba wrażliwości | Zmieniono wyłącznie `max_depth` drzewa z 3 na 4. [Wyniki próby](../results/lab4/sensitivity/comparison.csv). |
| Odtworzenie | W katalogu projektu uruchom `.\.venv\Scripts\python.exe scripts/compare_methods.py`, a do sprawdzenia powtarzalności `.\.venv\Scripts\python.exe scripts/reproduce_lab4.py`. Ziarno drzewa wynosi 42. [Instrukcja w README](../README.md). |

Suma opadów obejmuje wartości oznaczone lokalną datą. Każda wartość dotyczy godziny poprzedzającej znacznik, więc do sumy wchodzi przedział kończący się o północy rozpoczynającej dzień. Dane archiwalne Open-Meteo służą do historycznej estymacji. Do oceny prognoz przyszłego PM10 trzeba zebrać wersje danych pogodowych dostępne przed ocenianą dobą. Prognoza obszarowa IOŚ-PIB z Lab 3 służy jako kontekst przy próbie zastosowania. Wartością docelową w treningu i teście jest pomiar punktowy GIOŚ.

Źródła danych to [archiwum pomiarów GIOŚ](https://powietrze.gios.gov.pl/pjp/content/api) oraz [Open-Meteo Forecast API](https://open-meteo.com/en/docs), z atrybucją Open-Meteo zgodnie z [warunkami CC BY 4.0](https://open-meteo.com/en/terms).

## Wyniki

Z 61 lokalnych dób 47 miało komplet danych. Odpadło 13 dat uczących i jedna data testowa. Wśród 14 odrzuconych dat 10 miało niepełną pogodę, siedem miało luki PM10, a trzy miały oba braki. Dokładne daty i liczby godzin są w [run.json](../results/lab4/run.json). Doba zmiany czasu 25.10 miała 25 godzin. Oba modele otrzymały 28 dób do dopasowania i 19 tych samych dób do oceny.

| Scenariusz | Model i parametry | MAE [µg/m³] | Koszt lub ograniczenie |
|---|---|---:|---|
| Główny | Ridge, alpha = 1 | 10,0773 | Trzy współczynniki. Zależność liniowa może ekstrapolować poza zakres uczący. |
| Główny | Drzewo, limit głębokości 3, liść od 5 dni | 13,1345 | Model zwraca średnie z podzbiorów dni uczących. |
| Wrażliwość | Ridge, alpha = 1 | 10,0773 | Ten sam zbiór uczący i te same parametry. |
| Wrażliwość | Drzewo, limit głębokości 4, liść od 5 dni | 13,1345 | Dopasowane drzewo osiągnęło głębokość 3 także przy wyższym limicie. |

**Wybór do dalszej oceny to Ridge.** W obu scenariuszach miała MAE niższy o 3,0572 µg/m³, czyli 23,28% względem drzewa. Drzewo nie osiągnęło wymaganego spadku MAE o 1,0 µg/m³ względem Ridge. Oba modele wymagają tych samych danych. Zwiększenie limitu głębokości nie zmieniło wyboru. [Wyniki główne](../results/lab4/comparison.csv) · [Próba wrażliwości](../results/lab4/sensitivity/comparison.csv)

## Kontrola ręczna i diagnostyka

Dla 12.10.2026 pogoda miała średnią temperaturę 9,5667 °C, średni wiatr 10,1292 km/h i sumę opadów 0 mm. Po przeliczeniu współczynników Ridge na jednostki oryginalne prognoza wynosi `−0,842131 + 1,608384 × 9,566667 + 0,118688 × 10,129167 − 0,663715 × 0 ≈ 15,74695` µg/m³. Przy pomiarze 14,40 µg/m³ błąd bezwzględny wynosi 1,34695 µg/m³. Drzewo przypisało tę dobę do liścia z wartościami uczącymi 7,3875, 6,9667, 7,8625, 8,4708, 10,4375, 18,4333 i 14,0125. Ich średnia to 10,51012 µg/m³, a błąd bezwzględny 3,88988 µg/m³. Obie wartości zgadzają się z pierwszym wierszem CSV. Suma błędów z 19 dób wynosi odpowiednio 191,4690 i 249,5562 µg/m³. Dzielenie przez 19 daje MAE 10,0773 i 13,1345 µg/m³. [Obserwacje](../results/lab4/observations.csv) · [Współczynniki i liść](../results/lab4/run.json)

W części uczącej korelacje Pearsona z PM10 wynoszą +0,399 dla temperatury, −0,132 dla wiatru i −0,391 dla opadów. Współczynniki warunkowe Ridge wynoszą odpowiednio +1,608 µg/m³ na °C, +0,119 µg/m³ na km/h i −0,664 µg/m³ na mm. Odmienny znak dla wiatru przy porównaniu obu miar wskazuje, że zależność pojedynczej zmiennej i współczynnik po uwzględnieniu pozostałych cech mogą się różnić. Wynik opisuje związek w tej próbce.

Dni testowe były chłodniejsze. Średnie temperatury dobowe miały zakres 5,66–12,47 °C wobec 10,65–18,48 °C w uczeniu. Średnia reszta (pomiar minus estymacja) wynosiła +9,66 µg/m³ dla Ridge i +13,13 µg/m³ dla drzewa. Oba modele zaniżały wyniki w tym okresie. Jeden podział czasowy nie daje miary rozrzutu między sezonami.

## Zastosowanie do Lab 3 i ograniczenia

Oba modele uruchomiono na dwóch pełnych dniach z [próbki Lab 3](../data/processed/sample-clean.json). [Wynik zastosowania](../results/lab4/lab3_application.csv) zestawia oszacowania z opublikowaną prognozą IOŚ-PIB. Prognozy IOŚ-PIB są średnimi obszarowymi, a cel modelu dotyczy jednej stacji. Do obliczenia rzeczywistego błędu na dniach Lab 3 potrzebne są późniejsze pomiary. W tej próbie Ridge dla 13.11 dała 0 po obcięciu ujemnego wyniku. Średnia temperatura i opady tej doby wykraczają poza zakres treningu, co jest istotnym ograniczeniem stosowania modelu.

Do oceny przyszłego zastosowania potrzebne są pomiary z kilku sezonów, prognozy Open-Meteo zapisane przed ocenianą dobą oraz osobny okres testowy. Brakujące doby mogły zmienić reprezentatywność próby. Dane nie rozstrzygają o wpływie pogody na stężenie, przydatności modelu w innych częściach miasta ani trafności rekomendacji treningowych R5.

## Odtworzenie i wkład


