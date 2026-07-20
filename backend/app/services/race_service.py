"""Business logic for importing races from local HTML files."""

from datetime import date
import re
from pathlib import Path

from backend.app.models.race import Race
from backend.app.parsers.race_parser import RaceParser
from backend.app.repositories.horse_repository import HorseRepository
from backend.app.repositories.race_repository import RaceRepository
from backend.app.services.horse_service import HorseService


class RaceService:
    """Import race metadata and persist it through a repository."""

    def __init__(
        self,
        repository: RaceRepository,
        parser: RaceParser | None = None,
        horse_service: HorseService | None = None,
    ):
        self.repository = repository
        self.parser = parser or RaceParser()
        self.horse_service = horse_service or HorseService(HorseRepository(repository.db))
        self.race_created = False
        self.horse_import_summary = {"created": 0, "existing": 0}

    def import_from_file(self, file_path: str | Path) -> Race:
        """Parse and persist one race from a local HTML file.

        The race's date, hippodrome, and race number form its natural identity.
        An existing race is reused, while its horses are still imported.
        """
        parsed_race = self.parser.parse(str(file_path))
        race = self._to_race(parsed_race)

        existing_race = self.repository.get_by_identity(
            race.date, race.hippodrome, race.race_number
        )
        self.race_created = existing_race is None
        race = existing_race or self.repository.create(race)
        created = 0
        existing = 0
        for name in parsed_race["horses"]:
            _, was_created = self.horse_service.get_or_create(str(name))
            if was_created:
                created += 1
            else:
                existing += 1
        self.horse_import_summary = {"created": created, "existing": existing}
        return race

    @staticmethod
    def _to_race(parsed_race: dict[str, object]) -> Race:
        """Convert parser output into a typed ``Race`` model."""
        required_fields = ("date", "hippodrome", "race_number", "distance", "surface")
        missing_fields = [field for field in required_fields if not parsed_race.get(field)]
        if missing_fields:
            raise ValueError(f"Missing race fields: {', '.join(missing_fields)}.")

        try:
            race_date = date.fromisoformat(str(parsed_race["date"]))
            race_number = int(str(parsed_race["race_number"]))
            distance_match = re.search(r"\d+", str(parsed_race["distance"]))
            if distance_match is None:
                raise ValueError("distance contains no number")
            distance = int(distance_match.group())
        except (TypeError, ValueError) as exc:
            raise ValueError("Race date, number, or distance is invalid.") from exc

        if race_number < 1 or distance < 1:
            raise ValueError("Race number and distance must be positive.")

        return Race(
            date=race_date,
            hippodrome=str(parsed_race["hippodrome"]),
            race_number=race_number,
            distance=distance,
            surface=str(parsed_race["surface"]),
        )
