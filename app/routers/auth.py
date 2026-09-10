from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.invite_code_repository import InviteCodeRepository
from app.services.auth_service import AuthService
from app.schemas.auth import UserLogin, UserRegister, UserResponse, UserUpdate
from app.dependencies import get_current_user
from app.core.rate_limiter import limiter
from slowapi.util import get_remote_address
from app.core.security_logger import log_security_event
router = APIRouter(prefix="/auth", tags=["auth"])




def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(db)
    invite_repo = InviteCodeRepository(db)
    return AuthService(user_repo, invite_repo)

@router.post("/register", response_model=UserResponse)
@limiter.limit("3/hour")
async def register(request: Request, user_data: UserRegister, service: AuthService = Depends(get_auth_service)):
    ip_address = get_remote_address(request)
    try:
        result = service.register(user_data, user_data.invite_code)
        log_security_event("registration", email=user_data.email, success=True, ip_address=ip_address, user_id=result.id)
        return result
    except HTTPException:
        log_security_event("registration", email=user_data.email, success=False, ip_address=ip_address)
        raise

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: UserLogin, service: AuthService = Depends(get_auth_service)):
    ip_address = get_remote_address(request)
    try:
        result = service.login(credentials.email, credentials.password)
        log_security_event("login_attempt", email=credentials.email, success=True, ip_address=ip_address)
        return result
    except HTTPException:
        log_security_event("login_attempt", email=credentials.email, success=False, ip_address=ip_address)
        raise
@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    return service.update_profile(current_user, data)