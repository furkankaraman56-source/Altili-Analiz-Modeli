from backend.app.db.database import engine
from backend.app.db.base import Base

# Modelleri import etmek zorundayız
from backend.app.models.horse import Horse
from backend.app.models.race import Race
from backend.app.models.entry import Entry

Base.metadata.create_all(bind=engine)

print("Database oluşturuldu.")
