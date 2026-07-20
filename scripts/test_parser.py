"""Run the RaceParser against the bundled local sample HTML file."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.parsers.race_parser import RaceParser


def main() -> None:
    sample_file = PROJECT_ROOT / "database" / "samples" / "sample_race.html"
    print(RaceParser().parse(str(sample_file)))


if __name__ == "__main__":
    main()
