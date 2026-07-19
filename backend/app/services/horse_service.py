from backend.app.models.horse import Horse
from backend.app.repositories.horse_repository import HorseRepository


class HorseService:
    def __init__(self, repository: HorseRepository):
        self.repository = repository

    def get_all(self) -> list[Horse]:
        return self.repository.get_all()

    def create(self, horse: Horse) -> Horse:
        return self.repository.create(horse)