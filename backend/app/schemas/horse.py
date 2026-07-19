from pydantic import BaseModel, ConfigDict


class HorseCreate(BaseModel):
    name: str


class HorseResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)