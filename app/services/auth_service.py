
from datetime import datetime, timezone
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.schemas.auth import UserRegister as UserRegisterSchema
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.invite_code_repositories import InviteCodeRepository
from fastapi import HTTPException

class AuthService:
    def __init__(self, user_repo: UserRepository, invite_repo: InviteCodeRepository):
        self.user_repo = user_repo
        self.invite_repo = invite_repo
    
    def register(self, user: UserRegisterSchema, invite_code: str):
        # Check if the invite code is valid
        invite = self.invite_repo.get_by_code(invite_code)
        if not invite:
            raise HTTPException(status_code=400, detail="Invalid invite code")
        if invite.used_at is not None:
            raise HTTPException(status_code=409, detail="Invite code has already been used")
        
        # Check if the invite code has expired
        if invite.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Invite code has expired")

        # Check if the email or username is already taken
        if self.user_repo.get_by_email(user.email):
            raise HTTPException(status_code=409, detail="Email is already registered")
        if self.user_repo.get_by_username(user.username):
            raise HTTPException(status_code=409, detail="Username is already taken")

        #Hash the password before storing it
        hashed_pw = hash_password(user.password)
        

        # Create a new user
        new_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_pw,
            public_key=None
        )
        created_user = self.user_repo.create(new_user)

        # Mark the invite code as used
        self.invite_repo.mark_as_used(invite)

        return created_user
    
    def login(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {"access_token": access_token, "refresh_token": refresh_token}
        