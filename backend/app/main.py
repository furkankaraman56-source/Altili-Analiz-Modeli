from fastapi import FastAPI

from backend.app.api.horse_router import router as horse_router
from backend.app.api.race_router import router as race_router

app = FastAPI()

app.include_router(horse_router)
app.include_router(race_router)


@app.get("/")
def root():
    return {"message": "AAM API is running"}
