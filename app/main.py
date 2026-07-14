from fastapi import FastAPI



app = FastAPI(title = "Veil API", 
            description = "Veil API for managing and interacting with Veil services.",
            version = "1.0.0")


@app.get("/")
def root():
    return {"message": "Veil Root Endpoint"}

@app.get("/health")
def read_health():
    return {"status": "ok"}