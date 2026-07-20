"""Import exactly one race from a local HTML file."""

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.base import Base
from backend.app.db.database import SessionLocal, engine
from backend.app.models.entry import Entry
from backend.app.models.horse import Horse
from backend.app.models.race import Race
from backend.app.repositories.race_repository import RaceRepository
from backend.app.services.race_service import RaceService


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_file", type=Path, help="Path to the local race HTML file")
    args = parser.parse_args()

    if not args.html_file.is_file():
        parser.error(f"HTML file does not exist: {args.html_file}")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        service = RaceService(RaceRepository(db))
        race = service.import_from_file(args.html_file)
    except ValueError as exc:
        parser.error(str(exc))
    finally:
        db.close()

    race_status = "created" if service.race_created else "already existed"
    print(
        f"Race {race_status}: {race.race_number} at {race.hippodrome} "
        f"on {race.date.isoformat()} (ID: {race.id})"
    )
    print(
        "Horses imported: "
        f"{service.horse_import_summary['created']} created, "
        f"{service.horse_import_summary['existing']} already existed."
    )


if __name__ == "__main__":
    main()
