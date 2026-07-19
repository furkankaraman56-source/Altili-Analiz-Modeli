from fastapi import FastAPI

from backend.app.api.horse_router import router as horse_router

app = FastAPI()

app.include_router(horse_router)


@app.get("/")
def root():
    return {"message": "AAM API is running"}