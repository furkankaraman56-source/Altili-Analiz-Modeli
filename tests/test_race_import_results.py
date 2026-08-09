from pathlib import Path
import tempfile
import unittest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from backend.app.db.base import Base
from backend.app.models.entry import Entry
from backend.app.models.horse import Horse
from backend.app.models.race import Race
from backend.app.parsers.race_parser import RaceParser
from backend.app.repositories.race_repository import RaceRepository
from backend.app.services.race_service import RaceService


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RACE = PROJECT_ROOT / "database" / "samples" / "sample_race.html"


class RaceImportResultsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_directory.name) / "test.db"
        self.engine = create_engine(f"sqlite:///{database_path}")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.service = RaceService(RaceRepository(self.session))

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()
        self.temp_directory.cleanup()

    def test_reimport_updates_missing_results_without_duplicate_entry(self) -> None:
        self.service.import_from_file(SAMPLE_RACE)
        entry = self.session.scalar(select(Entry).where(Entry.horse.has(name="Golden Arrow")))
        self.assertIsNotNone(entry)
        assert entry is not None
        entry.finish_position = None
        entry.finish_time = None
        entry.pre_race_odds = None
        self.session.commit()

        self.service.import_from_file(SAMPLE_RACE)

        entries = self.session.scalars(select(Entry)).all()
        self.assertEqual(len(entries), 3)
        updated_entry = self.session.scalar(
            select(Entry).where(Entry.horse.has(name="Golden Arrow"))
        )
        self.assertIsNotNone(updated_entry)
        assert updated_entry is not None
        self.assertEqual(updated_entry.finish_position, 1)
        self.assertEqual(updated_entry.finish_time, "1:24.56")
        self.assertEqual(updated_entry.pre_race_odds, 2.4)

        self.service = RaceService(
            RaceRepository(self.session), parser=UpcomingRaceParser()
        )
        self.service.import_from_file(SAMPLE_RACE)

        preserved_entry = self.session.scalar(
            select(Entry).where(Entry.horse.has(name="Golden Arrow"))
        )
        self.assertIsNotNone(preserved_entry)
        assert preserved_entry is not None
        self.assertEqual(preserved_entry.finish_position, 1)
        self.assertEqual(preserved_entry.finish_time, "1:24.56")
        self.assertEqual(preserved_entry.pre_race_odds, 2.4)


class UpcomingRaceParser:
    """Return the sample race without result data, as for an upcoming race."""

    def parse(self, file_path: str) -> dict[str, object]:
        race = RaceParser().parse(file_path)
        for horse in race["horses"]:
            horse["finish_position"] = None
            horse["finish_time"] = None
            horse["pre_race_odds"] = None
        return race


if __name__ == "__main__":
    unittest.main()
