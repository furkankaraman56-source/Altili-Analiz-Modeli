import unittest

from backend.app.scoring.horse_scorer import HorseScorer


class HorseScorerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.scorer = HorseScorer()

    def test_score_matches_perfect_win_regression_value(self) -> None:
        score = self.scorer.score({
            "race_count": 1,
            "completed_count": 1,
            "win_rate": 100.0,
            "place_rate": 0.0,
            "average_finish_position": 1.0,
        })

        self.assertEqual(score, 67.0)

    def test_score_matches_second_place_regression_value(self) -> None:
        score = self.scorer.score({
            "race_count": 1,
            "completed_count": 1,
            "win_rate": 0.0,
            "place_rate": 100.0,
            "average_finish_position": 2.0,
        })

        self.assertEqual(score, 43.0)

    def test_score_matches_third_place_regression_value(self) -> None:
        score = self.scorer.score({
            "race_count": 1,
            "completed_count": 1,
            "win_rate": 0.0,
            "place_rate": 100.0,
            "average_finish_position": 3.0,
        })

        self.assertEqual(score, 39.0)

    def test_score_is_always_clamped_to_valid_range(self) -> None:
        for stats in (
            {
                "race_count": 5, "completed_count": 5, "win_rate": 500.0,
                "place_rate": -500.0, "average_finish_position": -10.0,
            },
            {
                "race_count": 100, "completed_count": 1, "win_rate": -100.0,
                "place_rate": 500.0, "average_finish_position": 100.0,
            },
        ):
            score = self.scorer.score(stats)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 100.0)

    def test_horse_without_completed_result_scores_zero(self) -> None:
        self.assertEqual(self.scorer.score({
            "race_count": 3,
            "completed_count": 0,
            "win_rate": 0.0,
            "place_rate": 0.0,
            "average_finish_position": 0.0,
        }), 0.0)

    def test_experience_score_caps_after_five_races(self) -> None:
        base_stats = {
            "completed_count": 5,
            "win_rate": 100.0,
            "place_rate": 0.0,
            "average_finish_position": 1.0,
        }

        self.assertEqual(
            self.scorer.score({**base_stats, "race_count": 5}),
            self.scorer.score({**base_stats, "race_count": 10}),
        )


if __name__ == "__main__":
    unittest.main()
