from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class HorseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class HorseResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class HorsePerformanceResponse(BaseModel):
    race_date: date
    hippodrome: str
    race_number: int
    distance: int
    surface: str
    start_number: int
    jockey: str
    trainer: str
    weight: float
    finish_position: int | None
    finish_time: str | None
    pre_race_odds: float | None