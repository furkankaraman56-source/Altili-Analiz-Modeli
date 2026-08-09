"""Add nullable result columns to the existing SQLite entries table."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT_ROOT / "aam.db"

COLUMNS = {
    "finish_position": "INTEGER",
    "finish_time": "VARCHAR(20)",
    "pre_race_odds": "FLOAT",
}


def migrate(database_path: Path) -> list[str]:
    """Add missing entry result columns and return the columns added."""
    if not database_path.is_file():
        raise FileNotFoundError(f"SQLite database does not exist: {database_path}")

    with sqlite3.connect(database_path) as connection:
        table_exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'entries'"
        ).fetchone()
        if table_exists is None:
            raise ValueError("SQLite database does not contain an entries table.")

        existing_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(entries)")
        }
        added_columns: list[str] = []
        for name, column_type in COLUMNS.items():
            if name not in existing_columns:
                connection.execute(f"ALTER TABLE entries ADD COLUMN {name} {column_type}")
                added_columns.append(name)

    return added_columns


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help=f"SQLite database path (default: {DEFAULT_DATABASE})",
    )
    args = parser.parse_args()

    try:
        added_columns = migrate(args.database)
    except (FileNotFoundError, ValueError, sqlite3.Error) as exc:
        parser.error(str(exc))

    if added_columns:
        print(f"Added columns to entries: {', '.join(added_columns)}")
    else:
        print("Migration already applied; no columns added.")


if __name__ == "__main__":
    main()
