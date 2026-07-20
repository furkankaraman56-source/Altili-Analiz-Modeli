from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class Horse(Base):
    __tablename__ = "horses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    entries: Mapped[list["Entry"]] = relationship(back_populates="horse")
