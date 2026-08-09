"""Schemas for race API responses."""

from pydantic import BaseModel


class RaceEntryResponse(BaseModel):
    horse_id: int
    horse_name: str
    start_number: int
    jockey: str
    trainer: str
    weight: float
    finish_position: int | None
    finish_time: str | None
    pre_race_odds: float | None


class RaceHorseScoreResponse(BaseModel):
    horse_id: int
    horse_name: str
    start_number: int
    score: float
