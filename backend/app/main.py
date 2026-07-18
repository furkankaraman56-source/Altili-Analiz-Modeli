from fastapi import FastAPI

app = FastAPI(title="AAM API")


@app.get("/")
def root():
    return {
        "message": "Hello AAM"
    }