from datetime import date
from pathlib import Path
import tempfile
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.api.horse_router import get_horse_history
from backend.app.db.base import Base
from backend.app.models.entry import Entry
from backend.app.models.horse import Horse
from backend.app.models.race import Race


class HorseHistoryApiTest(unittest.TestCase):
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

    def test_history_returns_newest_race_first_with_race_and_entry_fields(self) -> None:
        horse = Horse(name="Golden Arrow")
        old_race = Race(
            date=date(2026, 7, 1), hippodrome="Istanbul", race_number=2,
            distance=1200, surface="Turf",
        )
        new_race = Race(
            date=date(2026, 8, 1), hippodrome="Ankara", race_number=5,
            distance=1400, surface="Dirt",
        )
        self.session.add_all([horse, old_race, new_race])
        self.session.flush()
        self.session.add_all([
            Entry(
                horse_id=horse.id, race_id=old_race.id, start_number=3,
                jockey="Old Jockey", trainer="Old Trainer", weight=56.0,
                finish_position=4, finish_time="1:12.34", pre_race_odds=5.5,
            ),
            Entry(
                horse_id=horse.id, race_id=new_race.id, start_number=1,
                jockey="New Jockey", trainer="New Trainer", weight=58.0,
                finish_position=1, finish_time="1:25.67", pre_race_odds=2.4,
            ),
        ])
        self.session.commit()

        response = get_horse_history(horse.id, self.session)

        self.assertEqual([item.model_dump(mode="json") for item in response], [
            {
                "race_date": "2026-08-01", "hippodrome": "Ankara",
                "race_number": 5, "distance": 1400, "surface": "Dirt",
                "start_number": 1, "jockey": "New Jockey",
                "trainer": "New Trainer", "weight": 58.0,
                "finish_position": 1, "finish_time": "1:25.67",
                "pre_race_odds": 2.4,
            },
            {
                "race_date": "2026-07-01", "hippodrome": "Istanbul",
                "race_number": 2, "distance": 1200, "surface": "Turf",
                "start_number": 3, "jockey": "Old Jockey",
                "trainer": "Old Trainer", "weight": 56.0,
                "finish_position": 4, "finish_time": "1:12.34",
                "pre_race_odds": 5.5,
            },
        ])

    def test_history_returns_empty_list_for_existing_horse_without_entries(self) -> None:
        horse = Horse(name="No History")
        self.session.add(horse)
        self.session.commit()

        response = get_horse_history(horse.id, self.session)

        self.assertEqual(response, [])

    def test_history_returns_not_found_for_unknown_horse(self) -> None:
        with self.assertRaises(HTTPException) as context:
            get_horse_history(999, self.session)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Horse not found.")


if __name__ == "__main__":
    unittest.main()
