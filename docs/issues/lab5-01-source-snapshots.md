# L5-01 Niezmienne snapshoty danych źródłowych

Status: do realizacji.
Odpowiedzialny: Dawid Jopek.
Wymagania: R1, R2, R3 jako podstawa R5.
Powiązanie: docs/architecture.md, docs/lab5/data-model.md, ADR-001.

## Cel

Zachowanie dokładnych odpowiedzi GIOŚ i ERA5, metadanych oraz czasu pozyskania
tak, aby późniejsze pobranie nie zmieniało źródła wcześniejszego uruchomienia.
Obecne odpowiedzi i provenance.json istnieją; niezmienne wersjonowanie jest planowane.

## Kryteria odbioru

- Snapshot ma source_version równy SHA-256 dokładnych bajtów provenance.json.
- Każdy plik źródłowy ma hash zgodny z sources, bez zmiany odpowiedzi JSON.
- Stacja, identyfikatory stanowisk, współrzędne siatki ERA5 i czasy są zachowane.
- Archiwalny CET GIOŚ i UTC pogody mają jawne reguły przeliczenia.
- Ponowne pobranie nie nadpisuje istniejącego snapshotu.
- Nieudane pobranie nie zastępuje wcześniejszych odpowiedzi ani metadanych.

Recenzent obszaru: Maksym Łazowski. Zależność: brak.
