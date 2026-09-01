from fastapi import HTTPException
from app.repositories.key_bundle_repository import KeyBundleRepository
from app.schemas.key_bundle import KeyBundlePublish
from app.models.key_bundle import KeyBundle


class KeyBundleService:
    def __init__(self, key_bundle_repository: KeyBundleRepository):
        self.key_bundle_repository = key_bundle_repository

    def publish_bundle(self, user_id: int, bundle: KeyBundlePublish) -> KeyBundle:
        if self.key_bundle_repository.get_by_user_id(user_id) is not None:
            raise HTTPException(status_code=400, detail="Key bundle already published")
        return self.key_bundle_repository.create(user_id, bundle)

    def get_bundle(self, user_id: int) -> KeyBundle:
        bundle = self.key_bundle_repository.get_by_user_id(user_id)
        if bundle is None:
            raise HTTPException(status_code=404, detail="Key bundle not found")
        return bundle