# Technical Debt

## Sprint 9

- [ ] RaceParser çıktısındaki race_number string yerine int dönmeli.
- [ ] RaceParser çıktısındaki distance "1400 m" yerine 1400 (int) dönmeli.
- [ ] Surface string yerine enum kullanılmalı.
- [ ] Parser çıktısı dict yerine DTO/Pydantic model olmalı.

## Genel

- [ ] __future__ annotations kullanımı değerlendirilecek.
- [ ] Model docstring standartları gözden geçirilecek.

- [ ] import_race.py içinde sys.path değiştirme ihtiyacını kaldır.
- [ ] ValueError yerine domain-specific exception sınıfları kullan (ör. DuplicateRaceError).
- [ ] Parser should eventually return typed values (int/float/date) instead of raw strings.

- [ ]Review SQLAlchemy Session lifecycle in CLI scripts.
- [ ]Avoid DetachedInstanceError by ensuring ORM objects are not accessed after the session is closed.