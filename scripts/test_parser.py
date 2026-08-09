"""Run the RaceParser against the bundled local sample HTML file."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.parsers.race_parser import RaceParser


def main() -> None:
    sample_file = PROJECT_ROOT / "database" / "samples" / "sample_race.html"
    parsed_race = RaceParser().parse(str(sample_file))
    expected_results = [
        ("1", "1:24.56", "2.40"),
        ("2", "1:25.03", "3.75"),
        ("3", "1:25.61", "5.10"),
    ]

    for horse, (finish_position, finish_time, pre_race_odds) in zip(
        parsed_race["horses"], expected_results, strict=True
    ):
        assert horse["finish_position"] == finish_position
        assert horse["finish_time"] == finish_time
        assert horse["pre_race_odds"] == pre_race_odds

    print(parsed_race)


if __name__ == "__main__":
    main()
