# ADR-001 — Lokalna SQLite na telefonie

**Status:** przyjęta w projekcie Lab 5. Implementacja jest planowana.

## Kontekst

Użytkownik naciska **Sprawdź**, a aplikacja pobiera dwa zestawy danych. Przy niedostępności źródła przydaje się ostatnia zapisana prognoza wraz z czasem pobrania. Doby i godziny trzeba odczytywać razem.

## Decyzja

SQLite w aplikacji przechowuje ostatni poprawny zestaw. Transakcja obejmuje metadane obu źródeł, doby i godziny. Aplikacja korzysta z kluczy relacyjnych i odczytu po dacie.

## Alternatywa

Jeden plik JSON na telefonie byłby prosty do zapisania i pasowałby do formatu Lab 3. Wymagałby jednak własnej obsługi spójnego zastąpienia pliku i filtrowania godzin. SQLite daje transakcje i klucz obcy do doby.

## Konsekwencje

Potrzebna jest biblioteka React Native z obsługą SQLite i migracje schematu. Zapis jest lokalny dla urządzenia. Cache zachowuje ostatni zestaw, a ekran wyświetla czas jego pobrania.
