from backend.app.models.horse import Horse
from backend.app.repositories.horse_repository import HorseRepository


class HorseService:
    def __init__(self, repository: HorseRepository):
        self.repository = repository

    def get_all(self) -> list[Horse]:
        return self.repository.get_all()

    def create(self, horse: Horse) -> Horse:
        if self.repository.exists_by_name(horse.name):
            raise ValueError("Horse already exists.")
            
        return self.repository.create(horse)

    def get_or_create(self, name: str) -> tuple[Horse, bool]:
        """Return a horse by name, creating it when it does not yet exist.

        The boolean is ``True`` only when this call created the horse.
        """
        horse = self.repository.get_by_name(name)
        if horse is not None:
            return horse, False

        return self.repository.create(Horse(name=name)), True
