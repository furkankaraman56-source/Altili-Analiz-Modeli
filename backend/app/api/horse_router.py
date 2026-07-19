from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.horse import Horse
from backend.app.repositories.horse_repository import HorseRepository
from backend.app.schemas.horse import HorseCreate, HorseResponse
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

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )