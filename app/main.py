from fastapi import FastAPI
from app.routers import auth, connection, key_bundle, media
from app.routers import conversations
from app.routers import messages
from app.routers import ws
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limiter import limiter
from app.core.security_headers import SecurityHeadersMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings


app = FastAPI(title = "Veil API", 
            description = "Veil API for managing and interacting with Veil services.",
            version = "1.0.0")

app.add_middleware(SecurityHeadersMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(messages.router)
app.include_router(ws.router)
app.include_router(media.router)
app.include_router(connection.router)
app.include_router(key_bundle.router)

@app.get("/")
def root():
    return {"message": "Veil Root Endpoint"}

@app.get("/health")
def read_health():
    return {"status": "ok"}

