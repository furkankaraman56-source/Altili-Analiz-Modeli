from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    horse_id: Mapped[int] = mapped_column(ForeignKey("horses.id"))
    race_id: Mapped[int] = mapped_column(ForeignKey("races.id"))
    start_number: Mapped[int] = mapped_column(Integer)
    jockey: Mapped[str] = mapped_column(String(100))
    trainer: Mapped[str] = mapped_column(String(100))
    weight: Mapped[float] = mapped_column(Float)
    finish_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    finish_time: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pre_race_odds: Mapped[float | None] = mapped_column(Float, nullable=True)

    horse: Mapped["Horse"] = relationship(back_populates="entries")
    race: Mapped["Race"] = relationship(back_populates="entries")
