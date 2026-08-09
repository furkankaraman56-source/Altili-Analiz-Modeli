from pathlib import Path
import unittest

from backend.app.parsers.race_parser import RaceParser


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RaceParserTest(unittest.TestCase):
    def test_parses_entry_result_fields_from_sample_race(self) -> None:
        race = RaceParser().parse(
            str(PROJECT_ROOT / "database" / "samples" / "sample_race.html")
        )

        self.assertEqual(
            race["horses"][0],
            {
                "name": "Golden Arrow",
                "start_number": "1",
                "jockey": "Ahmet Yilmaz",
                "trainer": "Mehmet Kaya",
                "weight": "58.0",
                "finish_position": "1",
                "finish_time": "1:24.56",
                "pre_race_odds": "2.40",
            },
        )
        expected_fields = {
            "name",
            "start_number",
            "jockey",
            "trainer",
            "weight",
            "finish_position",
            "finish_time",
            "pre_race_odds",
        }
        self.assertTrue(all(set(horse) == expected_fields for horse in race["horses"]))


if __name__ == "__main__":
    unittest.main()
