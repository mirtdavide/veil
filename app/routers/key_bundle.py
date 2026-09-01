from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.repositories.key_bundle_repository import KeyBundleRepository
from app.schemas.key_bundle import KeyBundlePublish, KeyBundleResponse
from app.services.key_bundle_service import KeyBundleService

router = APIRouter(tags=["key-bundle"])


def get_key_bundle_service(db: Session = Depends(get_db)) -> KeyBundleService:
    return KeyBundleService(KeyBundleRepository(db))


@router.post("/users/me/key-bundle", response_model=KeyBundleResponse)
async def publish_key_bundle(
    body: KeyBundlePublish,
    current_user: User = Depends(get_current_user),
    service: KeyBundleService = Depends(get_key_bundle_service),
):
    return service.publish_bundle(current_user.id, body)


@router.get("/users/{user_id}/key-bundle", response_model=KeyBundleResponse)
async def get_key_bundle(
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: KeyBundleService = Depends(get_key_bundle_service),
):
    return service.get_bundle(user_id)