from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.invite_code_repositories import InviteCodeRepository
from app.services.auth_service import AuthService
from app.schemas.auth import UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(db)
    invite_repo = InviteCodeRepository(db)
    return AuthService(user_repo, invite_repo)

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, service: AuthService = Depends(get_auth_service)):
    return service.register(user_data, user_data.invite_code)

@router.post("/login")
async def login(credentials: UserLogin, service: AuthService = Depends(get_auth_service)):
    return service.login(credentials.email, credentials.password)