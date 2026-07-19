from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.repositories.horse_repository import HorseRepository
from backend.app.schemas.horse import HorseResponse
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