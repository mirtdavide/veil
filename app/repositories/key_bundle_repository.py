from sqlalchemy.orm import Session
from app.models.key_bundle import KeyBundle
from app.schemas.key_bundle import KeyBundlePublish


class KeyBundleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, bundle: KeyBundlePublish) -> KeyBundle:
        key_bundle = KeyBundle(user_id=user_id, **bundle.model_dump())
        self.db.add(key_bundle)
        self.db.commit()
        self.db.refresh(key_bundle)
        return key_bundle

    def get_by_user_id(self, user_id: int) -> KeyBundle | None:
        return self.db.query(KeyBundle).filter(KeyBundle.user_id == user_id).first()