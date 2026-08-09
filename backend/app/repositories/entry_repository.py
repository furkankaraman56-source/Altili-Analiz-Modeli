"""Entry persistence operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.entry import Entry
from backend.app.models.race import Race


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
        return self.get_by_race_and_horse(race_id, horse_id) is not None

    def get_by_race_and_horse(self, race_id: int, horse_id: int) -> Entry | None:
        """Return a horse's entry for a race, if it exists."""
        statement = select(Entry).where(
            Entry.race_id == race_id,
            Entry.horse_id == horse_id,
        )
        return self.db.scalar(statement)

    def get_history_by_horse_id(self, horse_id: int) -> list[Entry]:
        """Return a horse's entries with their race details, newest first."""
        statement = (
            select(Entry)
            .join(Entry.race)
            .where(Entry.horse_id == horse_id)
            .options(joinedload(Entry.race))
            .order_by(Race.date.desc())
        )
        return self.db.scalars(statement).all()

    def update_result_fields(
        self,
        existing_entry: Entry,
        imported_entry: Entry,
    ) -> Entry:
        """Persist result values supplied by an import without clearing existing data."""
        changed = False

        for field in ("finish_position", "finish_time", "pre_race_odds"):
            value = getattr(imported_entry, field)
            if value is not None and getattr(existing_entry, field) != value:
                setattr(existing_entry, field, value)
                changed = True

        if changed:
            self.db.commit()
            self.db.refresh(existing_entry)

        return existing_entry