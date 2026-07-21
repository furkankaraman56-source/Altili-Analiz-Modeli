"""Entry persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.entry import Entry


class EntryRepository:
    """Repository for race entry persistence."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, entry: Entry) -> Entry:
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def exists(self, race_id: int, horse_id: int) -> bool:
        """Return whether a horse has already been entered in a race."""
        statement = select(Entry.id).where(
            Entry.race_id == race_id,
            Entry.horse_id == horse_id,
        )
        return self.db.scalar(statement) is not None
