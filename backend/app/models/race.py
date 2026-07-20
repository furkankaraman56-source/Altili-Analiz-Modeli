from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class Race(Base):
    __tablename__ = "races"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    hippodrome: Mapped[str] = mapped_column(String(100))
    race_number: Mapped[int] = mapped_column(Integer)
    distance: Mapped[int] = mapped_column(Integer)
    surface: Mapped[str] = mapped_column(String(20))

    entries: Mapped[list["Entry"]] = relationship(back_populates="race")
