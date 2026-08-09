from datetime import date, timedelta
from pathlib import Path
import tempfile
import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.api.race_router import get_race_scores
from backend.app.db.base import Base
from backend.app.models.entry import Entry
from backend.app.models.horse import Horse
from backend.app.models.race import Race


class RaceScoresApiTest(unittest.TestCase):
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

    def test_scores_are_sorted_descending(self) -> None:
        target_race = self._make_race(date(2026, 8, 9), 1)
        winner = Horse(name="Winner")
        placer = Horse(name="Placer")
        self.session.add_all([winner, placer])
        self.session.flush()
        self._add_history(winner, 1)
        self._add_history(placer, 3)
        self.session.add_all([
            self._entry(target_race, winner, 8),
            self._entry(target_race, placer, 2),
        ])
        self.session.commit()

        response = get_race_scores(target_race.id, self.session)

        self.assertEqual([item.horse_name for item in response], ["Winner", "Placer"])
        self.assertGreater(response[0].score, response[1].score)

    def test_equal_scores_use_start_number_ascending(self) -> None:
        target_race = self._make_race(date(2026, 8, 9), 2)
        first_horse = Horse(name="First")
        second_horse = Horse(name="Second")
        self.session.add_all([first_horse, second_horse])
        self.session.flush()
        self.session.add_all([
            self._entry(target_race, second_horse, 9),
            self._entry(target_race, first_horse, 3),
        ])
        self.session.commit()

        response = get_race_scores(target_race.id, self.session)

        self.assertEqual([item.start_number for item in response], [3, 9])
        self.assertEqual([item.score for item in response], [0.0, 0.0])

    def test_unknown_race_returns_not_found(self) -> None:
        with self.assertRaises(HTTPException) as context:
            get_race_scores(999, self.session)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Race not found.")

    def test_existing_race_without_entries_returns_empty_list(self) -> None:
        race = self._make_race(date(2026, 8, 9), 3)
        self.session.commit()

        self.assertEqual(get_race_scores(race.id, self.session), [])

    def _make_race(self, race_date: date, race_number: int) -> Race:
        race = Race(
            date=race_date, hippodrome="Istanbul", race_number=race_number,
            distance=1200, surface="Turf",
        )
        self.session.add(race)
        self.session.flush()
        return race

    def _add_history(self, horse: Horse, finish_position: int) -> None:
        for offset in range(5):
            race = self._make_race(date(2026, 8, 1) + timedelta(days=offset), offset + 10)
            self.session.add(self._entry(race, horse, 1, finish_position))

    @staticmethod
    def _entry(
        race: Race,
        horse: Horse,
        start_number: int,
        finish_position: int | None = None,
    ) -> Entry:
        return Entry(
            race_id=race.id, horse_id=horse.id, start_number=start_number,
            jockey="Jockey", trainer="Trainer", weight=56.0,
            finish_position=finish_position, finish_time=None, pre_race_odds=None,
        )


if __name__ == "__main__":
    unittest.main()
