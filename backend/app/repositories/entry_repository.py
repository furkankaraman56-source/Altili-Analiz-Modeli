"""Entry persistence operations."""

from sqlalchemy import case, func, select
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

    def get_entries_by_race_id(self, race_id: int) -> list[Entry]:
        """Return a race's entries with horses, ordered by start number."""
        statement = (
            select(Entry)
            .where(Entry.race_id == race_id)
            .options(joinedload(Entry.horse))
            .order_by(Entry.start_number.asc())
        )
        return self.db.scalars(statement).all()

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

    def get_stats_by_horse_id(self, horse_id: int) -> dict[str, int | float]:
        """Return aggregate race statistics for one horse's entries."""
        statement = select(
            func.count(Entry.id).label("race_count"),
            func.count(Entry.finish_position).label("completed_count"),
            func.coalesce(
                func.sum(case((Entry.finish_position == 1, 1), else_=0)),
                0,
            ).label("win_count"),
            func.coalesce(
                func.sum(
                    case((Entry.finish_position.in_((2, 3)), 1), else_=0)
                ),
                0,
            ).label("place_count"),
            func.coalesce(func.avg(Entry.finish_position), 0.0).label(
                "average_finish_position"
            ),
            func.coalesce(func.min(Entry.finish_position), 0).label(
                "best_finish_position"
            ),
            func.coalesce(func.avg(Entry.pre_race_odds), 0.0).label(
                "average_pre_race_odds"
            ),
        ).where(Entry.horse_id == horse_id)
        result = self.db.execute(statement).one()

        return {
            "race_count": int(result.race_count),
            "completed_count": int(result.completed_count),
            "win_count": int(result.win_count),
            "place_count": int(result.place_count),
            "average_finish_position": float(result.average_finish_position),
            "best_finish_position": int(result.best_finish_position),
            "average_pre_race_odds": float(result.average_pre_race_odds),
        }

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
