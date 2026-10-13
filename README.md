# ProjektInformatyczny

SmartRoute — aplikacja do optymalizacji podróży

Aplikacja wybiera najbardziej opłacalny sposób podróży z punktu A do B
Użytkownik podaje:
- miejsce startowe,
- miejsce docelowe,
- godzinę wyjazdu,
- liczbę osób,
- ewentualnie własne auto / brak auta,
- priorytet: najniższy koszt / najkrótszy czas / kompromis koszt–czas.
A aplikacja porównuje np.:
- autobus,
- pociąg,
- samochód,
- Uber/Bolt,
- połączenie multimodalne, np. autobus + pociąg.
I zwraca coś w stylu:
Opcja	Koszt	Czas	Przesiadki	Wynik
Pociąg	28 zł	1h 20 min	0	8.7/10
Auto	45 zł	1h 05 min	0	7.9/10
Bus + pociąg	22 zł	1h 35 min	1	8.9/10
Uber	140 zł	1h 00 min	0	5.2/10


I na końcu:
Najbardziej opłacalna opcja: Bus + pociąg
Możecie policzyć prosty scoring:
score = w1 * koszt + w2 * czas + w3 * liczba_przesiadek
gdzie wagi zależą od preferencji użytkownika.
Przykładowo:
- student → większa waga ceny,
- podróż służbowa → większa waga czasu,
- podróż z rodziną → można mocniej karać przesiadki.
