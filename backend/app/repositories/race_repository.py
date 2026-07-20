"""Race persistence operations."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.race import Race


class RaceRepository:
    """Repository for race persistence."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, race: Race) -> Race:
        self.db.add(race)
        self.db.commit()
        self.db.refresh(race)
        return race

    def get_by_identity(
        self, race_date: date, hippodrome: str, race_number: int
    ) -> Race | None:
        """Return the race identified by its date, venue, and number."""
        statement = select(Race).where(
            Race.date == race_date,
            Race.hippodrome == hippodrome,
            Race.race_number == race_number,
        )
        return self.db.scalar(statement)

    def exists_by_identity(
        self, race_date: date, hippodrome: str, race_number: int
    ) -> bool:
        """Return whether a race with the natural race identity exists."""
        return self.get_by_identity(race_date, hippodrome, race_number) is not None
