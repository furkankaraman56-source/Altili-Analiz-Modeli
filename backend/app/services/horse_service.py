"""Business logic for horse operations."""

from backend.app.models.entry import Entry
from backend.app.models.horse import Horse
from backend.app.repositories.entry_repository import EntryRepository
from backend.app.repositories.horse_repository import HorseRepository


class HorseService:
    """Business logic for horse persistence and history."""

    def __init__(
        self,
        repository: HorseRepository,
        entry_repository: EntryRepository | None = None,
    ):
        self.repository = repository
        self.entry_repository = entry_repository or EntryRepository(repository.db)

    def get_all(self) -> list[Horse]:
        return self.repository.get_all()

    def create(self, horse: Horse) -> Horse:
        if self.repository.exists_by_name(horse.name):
            raise ValueError("Horse already exists.")

        return self.repository.create(horse)

    def get_or_create(self, name: str) -> tuple[Horse, bool]:
        """Return a horse by name, creating it when it does not yet exist."""
        horse = self.repository.get_by_name(name)
        if horse is not None:
            return horse, False

        return self.repository.create(Horse(name=name)), True

    def get_history(self, horse_id: int) -> list[Entry]:
        """Return a horse's historical race entries or raise when it is unknown."""
        if self.repository.get_by_id(horse_id) is None:
            raise ValueError("Horse not found.")

        return self.entry_repository.get_history_by_horse_id(horse_id)