from backend.app.db.database import SessionLocal
from backend.app.models.horse import Horse
from backend.app.repositories.horse_repository import HorseRepository


def main():
    db = SessionLocal()
    repo = HorseRepository(db)

    horse = Horse(name="KIZIM ERVA")

    repo.create(horse)

    print("Horse ID:", horse.id)
    print("Horse Name:", horse.name)


if __name__ == "__main__":
    main()