"""
Horse repository.

Responsible only for horse database operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.horse import Horse


class HorseRepository:
    """Repository for horse persistence."""
    def __init__(self, db: Session):
        self.db = db

    def create(self, horse: Horse) -> Horse:
        self.db.add(horse)
        self.db.commit()
        self.db.refresh(horse)
        return horse

    def get_all(self) -> list[Horse]:
        """Return all horses."""
        statement = select(Horse)
        return self.db.scalars(statement).all()

    def get_by_id(self, horse_id: int) -> Horse | None:
        """Return one horse by its ID."""
        return self.db.get(Horse, horse_id)
    
