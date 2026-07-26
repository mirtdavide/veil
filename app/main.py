from fastapi import FastAPI
from app.routers import auth
from app.routers import conversations
from app.routers import messages

app = FastAPI(title = "Veil API", 
            description = "Veil API for managing and interacting with Veil services.",
            version = "1.0.0")

app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(messages.router)

@app.get("/")
def root():
    return {"message": "Veil Root Endpoint"}

@app.get("/health")
def read_health():
    return {"status": "ok"}