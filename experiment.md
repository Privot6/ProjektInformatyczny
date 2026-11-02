# AeroRun Lab 4 Porównanie progów i wnioskowania rozmytego

## Pytanie i wymaganie

Czy wnioskowanie rozmyte Mamdaniego daje stabilniejszy indeks rekomendacji niż
reguły progowe po niewielkiej zmianie PM2.5, przy tych samych pomiarach pogodowych?
Eksperyment wspiera R5 z docs/problem.md, czyli rekomendację dla godziny.
Nie testuje R4 dotyczącego korelacji i regresji. Nie jest prognozą stężeń.

## Źródła zweryfikowane 2 listopada 2026

| Źródło | Co wyjaśnia | Ograniczenie | Co wykorzystano |
|---|---|---|---|
| MathWorks, Fuzzy Inference Process, dokumentacja R2026b, 2026, https://www.mathworks.com/help/fuzzy/fuzzy-inference-process.html | Etapy Mamdaniego, operatory i centroid | Przykład napiwku; brak progów dla powietrza | Schemat fuzzification → reguły → agregacja → centroid |
| Zespół scikit-fuzzy, Fuzzy Control Systems The Tipping Problem, dokumentacja online bez jawnego roku publikacji, https://scikit-fuzzy.readthedocs.io/en/latest/auto_examples/plot_tipping_problem_newapi.html | Przykład reguł językowych i ich implementacji | Demonstracja dydaktyczna, nie walidacja rekomendacji zdrowotnych | Adaptacja gotowych funkcji przynależności i defuzyfikacji do danych AeroRun |
| MathWorks, Mamdani and Sugeno Fuzzy Inference Systems, R2026b, 2026, https://www.mathworks.com/help/fuzzy/types-of-fuzzy-inference-systems.html | Alternatywa Sugeno i różnice wyjścia | Dobór zależy od zastosowania i parametrów | Mamdani wybrany ze względu na czytelne reguły; Sugeno pominięty, bo nie potrzebujemy dopasowywania liniowych następników |

Źródła opisują mechanikę, nie uzasadniają wybranych liczbowo progów PM, temperatury,
wiatru ani opadu. Wszystkie te parametry są założeniami demonstracji.
Mamdani umożliwia stopniowe przejście między ocenami, ale sam w sobie nie gwarantuje
trafności. Baseline pozostaje obowiązkowym punktem odniesienia.

## Protokół ustalony przed uruchomieniem

| Element | Ustalenie |
|---|---|
| Dane | Niezmieniony data/processed/aerorun_dane.csv z Lab 3, 72 syntetyczne godziny od 20 do 22 października 2026, Europe/Warsaw |
| Wersja | Stan bazowy repozytorium a30b4e16960f39bbf8bb25f69bf66fab3e347457; SHA-256 pliku w input_audit.json i run.json |
| Jednostka obserwacji | Jedna godzina, po dwa wyniki algorytmów; 72 przypadki na wariant, 144 wiersze observations.csv |
| Warianty | Minimum czterech ocen progowych vs trzy reguły Mamdaniego; pełne definicje w docs/lab4_model.md |
| Wejścia | PM2.5 i PM10 w µg/m³, temperatura w °C, wiatr w km/h, opad w mm sumy godzinowej; wszystkie z tej samej godziny |
| Parametry | Zamrożone w config/lab4.json przed pierwszym porównaniem; brak dopasowania na wynikach |
| Scenariusz | Każda godzina w wersji oryginalnej i z PM2.5 zwiększonym dokładnie o 1 µg/m³; pozostałe wartości bez zmian |
| Miara podstawowa | Średnia bezwzględna zmiana indeksu: mean(abs(score_plus-score)), punkty skali 0–100; mniej oznacza stabilniej |
| Kryterium praktyczne | Na potrzeby ćwiczenia co najmniej 20% mniejsza średnia zmiana niż baseline i zero TRENUJ w dwóch kontrolach wysokiego PM; bez dodatkowych źródeł danych |
| Dodatkowe diagnostyki | Minimum/maksimum zmian wśród godzin i liczba zmian etykiety; nie zastępują miary głównej |
| Warunki oceny | Te same 72 godziny, bez losowania i trenowania, brak podziału train/test; oba warianty oceniają historyczne warunki |
| Wrażliwość | Zmiana wyłącznie pm25_scale z 25 na 30 dla obu metod; te same 72 godziny, ten sam przyrost +1; wyniki w sensitivity/ |
| Odtworzenie | Polecenia z README; wersje środowiska w requirements-lab4-lock.txt; bez ziarna, bo brak losowania |

Próg 20% jest przyjętym kryterium ćwiczenia, nie uzgodnioną preferencją użytkownika
końcowego. Jeżeli średnia baseline wynosi zero, względna poprawa jest niezdefiniowana
i kryterium nie jest uznawane za spełnione. Brak powtórzeń losowych: min/max dotyczy
różnych godzin, nie przedziału ufności. Powtórzenie obliczeń sprawdza odtwarzalność.

## Kontrole i ograniczenia

Przed obliczeniami kontrolowane są duplikaty, braki, offset czasu, pełne godziny,
ciągłość UTC i poprawność jednostek/zakresów. Audyty są odrębnymi rezultatami
Dawida i Kacpra. Dane Lab 3 nie są modyfikowane. Kontrolne przypadki wysokiego
PM2.5 i PM10 używają najlepszej pogody i są zapisane w control_checks.csv.

Miara dotyczy stabilności indeksu, nie prawdziwości etykiet. Metoda stała również
mogłaby mieć zerową zmianę, dlatego samej stabilności nie wolno utożsamiać z jakością.
Dwie kontrole skrajnych warunków nie wykluczają pozostałych błędów reguł.
Brakuje niezależnych ocen eksperckich, zróżnicowanych rzeczywistych danych,
uzasadnionych progów, profilu użytkownika i kosztu błędnej rekomendacji.
Do oceny trafności potrzebne są niezależne etykiety przyznane przed porównaniem
oraz miara pominięć niekorzystnych warunków. Nie tworzymy pseudoetykiet tymi
samymi regułami, które potem oceniamy.

Interpolacja Lab 3 mogła korzystać z późniejszych godzin. W ocenie historycznej
opisuje to sposób budowy próbki; w eksperymencie online byłby to potencjalny
wyciek informacji. Nie potwierdzamy gotowości do pracy w czasie rzeczywistym.
Wnioskowanie nie wykazuje związku przyczynowego pogody ze stężeniami pyłów.

## Kontrola ręczna i użycie AI

Gotowy przykład: `python examples/lab4/fuzzy_demo.py`. Dla najlepszego zestawu
wejść centroid trójkąta (70,0), (100,1), (100,0) wynosi 90. Dla silnego PM
centroid niskiego trójkąta wynosi 10. Test sprawdza oba wyniki.
Agent AI przygotował kod, protokół, paczki, wyszukanie i odczyt wskazanych źródeł
oraz automatyczne sprawdzenia. Numeryczna kontrola kodu przez agenta nie zastępuje
wymaganego samodzielnego sprawdzenia przez studenta. Każda osoba odtwarza własną
część i dokumentuje rzeczywisty wkład we własnym commicie. Nie wykonano commitów
w imieniu członków zespołu. Wyniki uruchomienia i arytmetyczna kontrola są poniżej.

## Wyniki wykonanego porównania

| Scenariusz i wariant | Godziny | Średnia zmiana [pkt] | Min–max [pkt] | Zmiany etykiety |
|---|---:|---:|---:|---:|
| Podstawowy, bazowy | 72 | 10.000000 | 0.000000–40.000000 | 18 |
| Podstawowy, rozmyty | 72 | 1.439708 | 0.000000–5.520755 | 8 |
| Wrażliwość pm25_scale=30, bazowy | 72 | 0.000000 | 0.000000–0.000000 | 0 |
| Wrażliwość pm25_scale=30, rozmyty | 72 | 1.847444 | 0.000000–9.540610 | 0 |

W wariancie podstawowym średnia zmiana indeksu spadła z 10,000000 do 1,439708 pkt,
czyli o 8,560292 pkt (85.60%). Kryterium demonstracyjne 20% zostało
spełnione. Obie metody przeszły po dwa przypadki wysokiego PM bez etykiety TRENUJ.
Liczba zmian etykiety wyniosła odpowiednio 18 i 8; to diagnostyka, nie ocena błędów.

Po zmianie pm25_scale z 25 na 30 baseline nie zmienił indeksu w żadnej z godzin,
a model rozmyty zmieniał go średnio o 1,847444 pkt. W tym scenariuszu metoda
progowa jest stabilniejsza, a względnej poprawy nie wyliczamy, bo baseline=0.
Nie oznacza to, że próg jest trafniejszy: próbka po zmianie skali nie przekracza
jego granicy. Kryterium dla modelu rozmytego nie zostało spełnione w próbie
wrażliwości, więc wynik podstawowy nie daje odpornego uzasadnienia przewagi.

Wniosek: wnioskowanie rozmyte pozostaje wybraną przez zespół metodą projektową,
ale ten eksperyment nie dowodzi jej ogólnej przewagi. Kosztem jest konieczność
utrzymywania funkcji przynależności, reguł i dodatkowych zależności. Nie potrzeba
nowych pól wejściowych; korzyść biznesowa nie została wykazana. Przed użyciem
praktycznym potrzebne są rzeczywiste dane i niezależna ocena etykiet oraz
uzgodnienie kryteriów z odbiorcami. Nie dobierano progów po obejrzeniu wyników.

Audyt danych wykrył 8 syntetycznych godzin z PM2.5 > PM10. Zachowano je i
oznaczono do przeglądu. Jest to dodatkowy powód, by nie interpretować próbki
jako pomiarów referencyjnych. Nie usuwano niewygodnych rekordów z porównania.

## Kontrola liczb na zapisanym wyniku

Dla 20 października 2026, 08:00+02:00: PM2.5=19,21, PM10=27,90,
temperatura=10,88°C, wiatr=11,16 km/h, opad=0. Znormalizowany PM przed zmianą:
max(19,21/25; 27,90/50)=0,7684. Po +1 µg/m³: max(20,21/25; 0,558)=0,8084.
Przekracza to próg dobrego wejścia 0,8, podczas gdy pozostałe wejścia są dobre.
Baseline zmienia indeks 90 → 50, zatem bezwzględna zmiana wynosi 40 pkt.
Model rozmyty dla tego samego wiersza daje 64.544252 →
61.947524, zmianę 2.596728 pkt.

Suma zmian baseline w 72 godzinach wynosi 720, więc miara=720/72=10 pkt.
Suma zmian modelu rozmytego wynosi 103,65900545149316, więc po podzieleniu
przez 72 otrzymujemy 1,439708409048516 pkt. Sumy sprawdzono odrębnym odczytem
CSV i arytmetyką dziesiętną, poza funkcją wyliczającą porównanie.
Jest to kontrola wykonana przez agenta; student powinien odtworzyć ją samodzielnie.
