from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserProfile

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
