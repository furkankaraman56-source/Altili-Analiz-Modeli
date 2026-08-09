"""Race API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.repositories.entry_repository import EntryRepository
from backend.app.repositories.race_repository import RaceRepository
from backend.app.schemas.race import RaceEntryResponse
from backend.app.services.race_service import RaceService


router = APIRouter(
    prefix="/races",
    tags=["Races"],
)


@router.get("/{race_id}/entries", response_model=list[RaceEntryResponse])
def get_race_entries(
    race_id: int,
    db: Session = Depends(get_db),
) -> list[RaceEntryResponse]:
    service = RaceService(RaceRepository(db), entry_repository=EntryRepository(db))

    try:
        entries = service.get_entries(race_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return [
        RaceEntryResponse(
            horse_id=entry.horse_id,
            horse_name=entry.horse.name,
            start_number=entry.start_number,
            jockey=entry.jockey,
            trainer=entry.trainer,
            weight=entry.weight,
            finish_position=entry.finish_position,
            finish_time=entry.finish_time,
            pre_race_odds=entry.pre_race_odds,
        )
        for entry in entries
    ]
