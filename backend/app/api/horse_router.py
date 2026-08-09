from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.horse import Horse
from backend.app.repositories.entry_repository import EntryRepository
from backend.app.repositories.horse_repository import HorseRepository
from backend.app.schemas.horse import (
    HorseCreate,
    HorsePerformanceResponse,
    HorseResponse,
    HorseStatsResponse,
)
from backend.app.services.horse_service import HorseService


router = APIRouter(
    prefix="/horses",
    tags=["Horses"],
)


@router.get("/", response_model=list[HorseResponse])
def get_horses(db: Session = Depends(get_db)):
    repository = HorseRepository(db)
    service = HorseService(repository)

    return service.get_all()


@router.get(
    "/{horse_id}/history",
    response_model=list[HorsePerformanceResponse],
)
def get_horse_history(
    horse_id: int,
    db: Session = Depends(get_db),
):
    service = HorseService(
        HorseRepository(db),
        EntryRepository(db),
    )

    try:
        entries = service.get_history(horse_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return [
        HorsePerformanceResponse(
            race_date=entry.race.date,
            hippodrome=entry.race.hippodrome,
            race_number=entry.race.race_number,
            distance=entry.race.distance,
            surface=entry.race.surface,
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


@router.get(
    "/{horse_id}/stats",
    response_model=HorseStatsResponse,
)
def get_horse_stats(
    horse_id: int,
    db: Session = Depends(get_db),
) -> HorseStatsResponse:
    service = HorseService(
        HorseRepository(db),
        EntryRepository(db),
    )

    try:
        return HorseStatsResponse(**service.get_stats(horse_id))
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.post("/", response_model=HorseResponse)
def create_horse(
    horse: HorseCreate,
    db: Session = Depends(get_db),
):
    repository = HorseRepository(db)
    service = HorseService(repository)

    new_horse = Horse(name=horse.name)

    try:
        return service.create(new_horse)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
