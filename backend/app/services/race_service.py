"""Business logic for importing races from local HTML files."""

from datetime import date
import re
from pathlib import Path

from backend.app.models.entry import Entry
from backend.app.models.race import Race
from backend.app.parsers.race_parser import RaceParser
from backend.app.repositories.entry_repository import EntryRepository
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
        entry_repository: EntryRepository | None = None,
    ):
        self.repository = repository
        self.parser = parser or RaceParser()
        self.horse_service = horse_service or HorseService(HorseRepository(repository.db))
        self.entry_repository = entry_repository or EntryRepository(repository.db)
        self.race_created = False
        self.horse_import_summary = {"created": 0, "existing": 0}
        self.entry_import_summary = {"created": 0, "existing": 0}

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
        entries_created = 0
        entries_existing = 0
        for parsed_horse in parsed_race["horses"]:
            horse, was_created = self._import_horse(parsed_horse)
            if was_created:
                created += 1
            else:
                existing += 1
            entry = self._to_entry(race.id, horse.id, parsed_horse)
            if self.entry_repository.exists(entry.race_id, entry.horse_id):
                entries_existing += 1
            else:
                self.entry_repository.create(entry)
                entries_created += 1
        self.horse_import_summary = {"created": created, "existing": existing}
        self.entry_import_summary = {
            "created": entries_created,
            "existing": entries_existing,
        }
        return race

    def _import_horse(self, parsed_horse: object):
        if not isinstance(parsed_horse, dict) or not parsed_horse.get("name"):
            raise ValueError("Horse name is missing.")
        return self.horse_service.get_or_create(str(parsed_horse["name"]))

    @staticmethod
    def _to_entry(race_id: int | None, horse_id: int | None, parsed_horse: object) -> Entry:
        if race_id is None or horse_id is None or not isinstance(parsed_horse, dict):
            raise ValueError("Race or horse could not be persisted.")

        required_fields = ("start_number", "jockey", "trainer", "weight")
        missing_fields = [field for field in required_fields if not parsed_horse.get(field)]
        if missing_fields:
            raise ValueError(f"Missing entry fields: {', '.join(missing_fields)}.")

        try:
            start_number = int(str(parsed_horse["start_number"]))
            weight = float(str(parsed_horse["weight"]))
        except (TypeError, ValueError) as exc:
            raise ValueError("Entry start number or weight is invalid.") from exc
        if start_number < 1 or weight <= 0:
            raise ValueError("Entry start number and weight must be positive.")

        return Entry(
            race_id=race_id,
            horse_id=horse_id,
            start_number=start_number,
            jockey=str(parsed_horse["jockey"]),
            trainer=str(parsed_horse["trainer"]),
            weight=weight,
        )

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
