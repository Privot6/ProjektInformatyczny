# Reguły progowe i wnioskowanie rozmyte

Wykorzystano API `control` oraz funkcje `trapmf`, `trimf`, `interp_membership`
gotowej biblioteki scikit-fuzzy. Nie powstaje własna biblioteka wnioskowania.
Konfiguracja jest wspólna dla obu wariantów w `config/lab4.json`.

## Wejścia

Z godziny t: `pollution=max(pm25/25, pm10/50)`,
`thermal=abs(temperature_2m-15)`, `wind=wind_speed_10m`, `rain=precipitation`.
Nie przewidujemy t+1. Przy stałym zmierzonym PM wiatr nie zmniejsza zapylenia;
jest osobnym kryterium komfortu. Temperatura jest reprezentowana odległością
od założonego środka 15°C. To uproszczenie, a nie model termofizjologiczny.

| Wejście | a | b | c | Limit domeny |
|---|---:|---:|---:|---:|
| pollution | 0,6 | 1,0 | 1,4 | 10 |
| thermal [°C od 15°C] | 5 | 12 | 20 | 120 |
| wind [km/h] | 10 | 25 | 40 | 300 |
| rain [mm sumy godzinowej] | 0 | 0,5 | 2 | 1000 |

Dla każdego wejścia: dobre = trapez [0,0,a,b], średnie = trójkąt [a,b,c],
złe = trapez [b,c,limit,limit]. Wartości powyżej limitu są nasycane, a nie
usuwane; braki, nieskończoności i wartości fizycznie błędne są odrzucane wcześniej.
Liczby 25 i 50 są skalami demonstracji, nie przyjętymi normami WHO/GIOŚ.

## Trzy reguły Mamdaniego

1. Dowolne wejście złe → niski indeks.
2. Wszystkie wejścia dobre LUB średnie, a co najmniej jedno średnie → średni indeks.
3. Wszystkie wejścia dobre → wysoki indeks.

AND = minimum, OR = maksimum, implikacja = obcięcie minimum, agregacja = maksimum.
Wyjście: niski [0,0,30], średni [20,50,80], wysoki [70,100,100]. Defuzyfikacja:
centroid obszaru, indeks 0–100. Wnioskowanie i defuzyfikację wykonuje API control.
Etykiety: <35 ZOSTAŃ W DOMU, [35,65) OGRANICZ WYSIŁEK, >=65 TRENUJ.
Są to etykiety demonstracyjne z karty projektu, bez walidacji zdrowotnej.

Wariant bazowy przypisuje każdemu wejściu 90, jeżeli x <= (a+b)/2;
50, jeżeli (a+b)/2 < x <= (b+c)/2; w przeciwnym razie 10.
Wynikiem jest minimum czterech ocen, z tym samym mapowaniem etykiet.
Końce przedziałów są jawne i objęte testem.

## Ręczne sprawdzenie

Dla PM2.5=5, PM10=10, T=15, wiatru=5 i opadu=0 wszystkie przynależności dobre=1.
Aktywna jest tylko reguła wysoka. Centroid trójkąta (70,0), (100,1), (100,0)
wynosi (70+100+100)/3=90. Dla PM2.5=100 i pozostałych takich samych danych
aktywna jest tylko niska: (0+0+30)/3=10. Testy sprawdzają te wyniki numerycznie.
