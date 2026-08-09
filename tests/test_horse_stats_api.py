from datetime import date
from pathlib import Path
import tempfile
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.api.horse_router import get_horse_stats
from backend.app.db.base import Base
from backend.app.models.entry import Entry
from backend.app.models.horse import Horse
from backend.app.models.race import Race


class HorseStatsApiTest(unittest.TestCase):
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

    def test_stats_calculates_aggregate_values(self) -> None:
        horse = Horse(name="Golden Arrow")
        race = Race(
            date=date(2026, 8, 1), hippodrome="Istanbul", race_number=1,
            distance=1200, surface="Turf",
        )
        second_race = Race(
            date=date(2026, 8, 2), hippodrome="Ankara", race_number=2,
            distance=1400, surface="Dirt",
        )
        self.session.add_all([horse, race, second_race])
        self.session.flush()
        self.session.add_all([
            Entry(
                horse_id=horse.id, race_id=race.id, start_number=1,
                jockey="Jockey One", trainer="Trainer One", weight=56.0,
                finish_position=1, finish_time="1:12.34", pre_race_odds=2.0,
            ),
            Entry(
                horse_id=horse.id, race_id=second_race.id, start_number=3,
                jockey="Jockey Two", trainer="Trainer Two", weight=57.0,
                finish_position=3, finish_time="1:25.67", pre_race_odds=4.0,
            ),
        ])
        self.session.commit()

        response = get_horse_stats(horse.id, self.session)

        self.assertEqual(response.model_dump(), {
            "race_count": 2,
            "completed_count": 2,
            "win_count": 1,
            "place_count": 1,
            "win_rate": 50.0,
            "place_rate": 50.0,
            "average_finish_position": 2.0,
            "best_finish_position": 1,
            "average_pre_race_odds": 3.0,
        })

    def test_stats_returns_zeros_for_existing_horse_without_entries(self) -> None:
        horse = Horse(name="No History")
        self.session.add(horse)
        self.session.commit()

        response = get_horse_stats(horse.id, self.session)

        self.assertEqual(response.model_dump(), {
            "race_count": 0,
            "completed_count": 0,
            "win_count": 0,
            "place_count": 0,
            "win_rate": 0.0,
            "place_rate": 0.0,
            "average_finish_position": 0.0,
            "best_finish_position": 0,
            "average_pre_race_odds": 0.0,
        })

    def test_stats_returns_not_found_for_unknown_horse(self) -> None:
        with self.assertRaises(HTTPException) as context:
            get_horse_stats(999, self.session)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Horse not found.")

    def test_stats_ignores_missing_result_and_odds_values_in_averages(self) -> None:
        horse = Horse(name="Partial Results")
        race = Race(
            date=date(2026, 8, 1), hippodrome="Istanbul", race_number=1,
            distance=1200, surface="Turf",
        )
        second_race = Race(
            date=date(2026, 8, 2), hippodrome="Ankara", race_number=2,
            distance=1400, surface="Dirt",
        )
        self.session.add_all([horse, race, second_race])
        self.session.flush()
        self.session.add_all([
            Entry(
                horse_id=horse.id, race_id=race.id, start_number=1,
                jockey="Jockey One", trainer="Trainer One", weight=56.0,
                finish_position=1, finish_time="1:12.34", pre_race_odds=2.5,
            ),
            Entry(
                horse_id=horse.id, race_id=second_race.id, start_number=3,
                jockey="Jockey Two", trainer="Trainer Two", weight=57.0,
                finish_position=None, finish_time=None, pre_race_odds=None,
            ),
        ])
        self.session.commit()

        response = get_horse_stats(horse.id, self.session)

        self.assertEqual(response.model_dump(), {
            "race_count": 2,
            "completed_count": 1,
            "win_count": 1,
            "place_count": 0,
            "win_rate": 100.0,
            "place_rate": 0.0,
            "average_finish_position": 1.0,
            "best_finish_position": 1,
            "average_pre_race_odds": 2.5,
        })


if __name__ == "__main__":
    unittest.main()
