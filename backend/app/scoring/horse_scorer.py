"""Deterministic horse scoring calculations."""

from collections.abc import Mapping


class HorseScorer:
    """Calculate an explainable score from pre-calculated horse statistics."""

    def score(self, stats: Mapping[str, int | float]) -> float:
        """Return a score from 0.0 to 100.0, rounded to two decimal places."""
        completed_count = int(stats["completed_count"])
        if completed_count == 0:
            return 0.0

        win_rate = float(stats["win_rate"])
        place_rate = float(stats["place_rate"])
        average_finish_position = float(stats["average_finish_position"])
        race_count = float(stats["race_count"])

        finish_position_score = max(
            0.0,
            100.0 - ((average_finish_position - 1.0) * 20.0),
        )

        experience_score = min(race_count / 5.0, 1.0) * 100.0

        raw_score = (
            win_rate * 0.45
            + place_rate * 0.25
            + finish_position_score * 0.20
            + experience_score * 0.10
        )

        return round(
            min(100.0, max(0.0, raw_score)),
            2,
        )