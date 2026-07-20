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