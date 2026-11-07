# ADR-001 Zapis uruchomień w plikach CSV i JSON

Status: przyjęta w projekcie Lab 5, implementacja zmiany planowana.
Wymaganie: R5 i odtwarzalność porównania z Lab 4.

## Kontekst

Jeden użytkownik uruchamia lokalną analizę godzinowych danych jednej stacji.
Istniejące skrypty i dashboard używają CSV/JSON. results/lab4/ zachowuje tylko
jeden komplet wyników i może zostać nadpisany. Niezależne zapisy kilku plików
mogą pozostawić niepełny komplet po awarii. Nie ma wymagania wspólnej historii
przez sieć, współbieżnego zapisu ani zapytań SQL po dużym zbiorze uruchomień.

## Decyzja

Pozostają CSV wyników i JSON parametrów. Każdy nowy przebieg otrzymuje osobny
run_id UUID i katalog results/runs/<run_id>/. Kopie wejścia, konfiguracji i
provenance.json oraz manifest z hashami wiążą wynik z dokładną wersją danych.
Odpowiedzi źródeł są zachowane w data/raw/snapshots/<source_version>/.

Nowy zapis trafia do .partial/<run_id>/ na tym samym systemie plików. Komplet
plików, liczebności, klucze i hashe są sprawdzane przed publikacją. Manifest
z status=complete jest tworzony po wynikach, a cały katalog jest publikowany
po zakończeniu zapisu. Dashboard odczytuje wyłącznie opublikowane katalogi.
Nie potwierdza się utrwalenia, gdy zapis lub publikacja zawiedzie.

Przy kolizji identyfikatora istniejący katalog pozostaje bez zmian; operacja
zwraca FileExistsError. Nie nadpisuje wyników. Ponowne uruchomienie z tymi samymi
danymi otrzymuje nowy identyfikator i zachowuje poprzedni wynik. Błąd odczytu,
niezgodny hash lub brak pliku wyklucza przebieg z prezentacji. Stare results/lab4/
pozostaje wersją odniesienia; schematy jego CSV są zachowane.

## Alternatywa

SQLite zapewniłby transakcję dla wielu zapisów, klucze i zapytania po historii.
Wymagałby jednak projektu tabel, migracji, odwzorowania dotychczasowych CSV
i zmiany odczytu dashboardu. W obecnym zakresie nie daje korzyści uzasadniającej
te dodatkowe elementy. Nie projektuje się fikcyjnej bazy do samego diagramu.

## Koszt i konsekwencje

Brak dodatkowego serwera i pakietu bazodanowego. Zespół wykorzystuje istniejące
umiejętności Python/Pandas i schematy plików; sama znajomość narzędzi nie zastępuje
warunku jednego lokalnego autora zapisu. Trzeba zaimplementować i utrzymywać
manifest, kontrolę relacji, publikację katalogu i obsługę wersji schematu.
Kopie wejść zwiększają zajętość dysku; dla próbki 72 godzin jest to mały koszt,
ale historia nie jest automatycznie usuwana bez ustalonej polityki retencji.

Przyjęto jednego autora zapisu i lokalny system plików z atomową zmianą nazwy
katalogu. Błąd przed publikacją może pozostawić .partial/; taki katalog nie
jest udanym przebiegiem. Atomowe opublikowanie nie zastępuje kopii zapasowej
ani gwarancji utrwalenia przy fizycznej awarii dysku. Czytelnicy korzystają
z niezmiennych, opublikowanych katalogów i nie modyfikują ich zawartości.

## Warunek ponownego rozważenia

Wielu jednoczesnych autorów, sieciowy magazyn bez tej samej semantyki publikacji,
wspólna historia użytkowników albo częste zapytania przekrojowe uzasadniają
powrót do SQLite lub PostgreSQL. Koszt wyboru bazy jest wtedy porównywany
z kosztem dalszego utrzymywania spójności plików.
