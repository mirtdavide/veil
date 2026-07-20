from fastapi import FastAPI
from app.routers import auth


app = FastAPI(title = "Veil API", 
            description = "Veil API for managing and interacting with Veil services.",
            version = "1.0.0")

app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Veil Root Endpoint"}

@app.get("/health")
def read_health():
    return {"status": "ok"}