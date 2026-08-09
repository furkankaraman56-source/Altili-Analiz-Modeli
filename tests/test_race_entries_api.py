from datetime import date
from pathlib import Path
import tempfile
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.api.race_router import get_race_entries
from backend.app.db.base import Base
from backend.app.models.entry import Entry
from backend.app.models.horse import Horse
from backend.app.models.race import Race


class RaceEntriesApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_directory.name) / "test.db"
        self.engine = create_engine(f"sqlite:///{database_path}")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()
        self.temp_directory.cleanup()

    def test_entries_include_horse_and_entry_fields_in_start_number_order(self) -> None:
        race = Race(
            date=date(2026, 8, 9), hippodrome="Istanbul", race_number=6,
            distance=1400, surface="Turf",
        )
        first_horse = Horse(name="First Star")
        second_horse = Horse(name="Second Wind")
        self.session.add_all([race, first_horse, second_horse])
        self.session.flush()
        self.session.add_all([
            Entry(
                race_id=race.id, horse_id=second_horse.id, start_number=8,
                jockey="Jockey Two", trainer="Trainer Two", weight=57.5,
                finish_position=None, finish_time=None, pre_race_odds=None,
            ),
            Entry(
                race_id=race.id, horse_id=first_horse.id, start_number=2,
                jockey="Jockey One", trainer="Trainer One", weight=56.0,
                finish_position=1, finish_time="1:24.56", pre_race_odds=2.4,
            ),
        ])
        self.session.commit()

        response = get_race_entries(race.id, self.session)

        self.assertEqual([item.model_dump() for item in response], [
            {
                "horse_id": first_horse.id, "horse_name": "First Star",
                "start_number": 2, "jockey": "Jockey One",
                "trainer": "Trainer One", "weight": 56.0,
                "finish_position": 1, "finish_time": "1:24.56",
                "pre_race_odds": 2.4,
            },
            {
                "horse_id": second_horse.id, "horse_name": "Second Wind",
                "start_number": 8, "jockey": "Jockey Two",
                "trainer": "Trainer Two", "weight": 57.5,
                "finish_position": None, "finish_time": None,
                "pre_race_odds": None,
            },
        ])

    def test_entries_returns_empty_list_for_existing_race_without_entries(self) -> None:
        race = Race(
            date=date(2026, 8, 9), hippodrome="Ankara", race_number=1,
            distance=1200, surface="Dirt",
        )
        self.session.add(race)
        self.session.commit()

        self.assertEqual(get_race_entries(race.id, self.session), [])

    def test_entries_returns_not_found_for_unknown_race(self) -> None:
        with self.assertRaises(HTTPException) as context:
            get_race_entries(999, self.session)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Race not found.")


if __name__ == "__main__":
    unittest.main()
