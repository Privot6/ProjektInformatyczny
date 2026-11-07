# L5-05 Przegląd spójności projektu UC-01

Status: do przeglądu.
Odpowiedzialny za zebranie wyniku: Kacper Dąbek.
Wymaganie: przegląd projektu Lab 5, UC-01 powiązany z R5.

## Wynik kontroli technicznej

Nazwy pól wejściowych i wynikowych porównano z Lab 3–4. Wyniki liczbowe odnoszą
się do próbki rzeczywistej, nie wcześniejszej syntetycznej. Zidentyfikowano brak
run_id i atomowej publikacji w obecnym zapisie oraz brak egzekwowania minimum
48 godzin w load_data. W projekcie oznaczono je jako zmiany planowane.

## Obszary niezależnego przeglądu

| Autor obszaru | Recenzent | Przedmiot |
|---|---|---|
| Dawid Jopek | Maksym Łazowski | Źródła, jednostki, stacja i czas |
| Kacper Dąbek | Dawid Jopek | Dane, manifest i zachowanie po nieudanym zapisie |
| Maksym Łazowski | Kornel Łazowski | Kontrakt, sekwencja i zgodność metod z Lab 4 |
| Kornel Łazowski | Kacper Dąbek | UC-01, ADR i prezentacja wyniku |

## Kryteria zakończenia

- Recenzent wskazuje wejście, wynik, moduł odpowiedzialny i reakcję na błąd wyłącznie na podstawie dokumentacji.
- Wynik przeglądu zawiera recenzenta, datę oraz poprawkę lub wynik bez zastrzeżeń.
- Diagramy, kontrakt, ścieżki i nazwy pól są zgodne; istniejące i planowane elementy są odróżnione.
- Zgłoszenia L5-01 do L5-04 mają właścicieli i kryteria odbioru w GitHub.
