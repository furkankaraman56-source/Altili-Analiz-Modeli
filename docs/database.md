# AAM Database Design

## Amaç

Bu veritabanı;

- Yarış programlarını saklar.
- At bilgilerini saklar.
- Jokey bilgilerini saklar.
- Antrenör bilgilerini saklar.
- Yarış sonuçlarını saklar.
- AI analizlerini saklar.
- Üretilen kuponları saklar.

---

## Temel Tablolar

1. Horse
2. Jockey
3. Trainer
4. Race
5. Entry (RaceEntry)
6. Prediction

---

## İlişkiler

Horse (1) ------ (N) Entry

Race (1) ------- (N) Entry

Jockey (1) ---- (N) RaceEntry

Trainer (1) --- (N) RaceEntry

Entry (RaceEntry) (1) -- (N) Prediction

---

## Tasarım Prensipleri

- Aynı veri iki farklı tabloda tutulmaz.
- Geçmiş yarışlar silinmez.
- AI skorları ayrı tabloda tutulur.
- Tahminler yarış sonuçlarından bağımsızdır.
- Veri modeli SQLite ile başlayacak, PostgreSQL'e taşınabilecek şekilde tasarlanacaktır.

## Gelecek Sürümlerde Eklenecek Tablolar

### Historical Performance

Bir atın geçmiş yarış performansı şu anda `Entry` (RaceEntry) ile bağlı `Race` ve `Horse` kayıtlarının birleşimiyle temsil edilir; ayrı bir `Performance` tablosu yoktur.

### Workout

Galop ve idman bilgileri.

### Statistics

Model tarafından hesaplanan istatistikler.

### Ticket

Üretilen altılı kuponları saklar.

### Learning

Modelin sonuç analizlerinden öğrendiği verileri saklar.

---

## Tasarım İlkeleri

- Veriler normalize edilir.
- Aynı bilgi tek tabloda tutulur.
- Performans verileri Horse tablosunda tutulmaz.
- Analiz sonuçları Prediction tablosunda tutulur.
- Sistem PostgreSQL'e taşınabilecek şekilde geliştirilir.
