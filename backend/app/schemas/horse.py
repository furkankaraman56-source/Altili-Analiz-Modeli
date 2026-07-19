from pydantic import BaseModel, ConfigDict, Field


class HorseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class HorseResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)