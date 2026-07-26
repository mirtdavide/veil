
#Repository for invite code-related database operations
from app.models.invite_code import InviteCode
from sqlalchemy.orm import Session
from datetime import datetime, timezone

class InviteCodeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, code: str):
        return self.db.query(InviteCode).filter(InviteCode.code == code).first()

    def mark_as_used(self, invite_code: InviteCode):
        invite_code.used_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(invite_code)
        return invite_code
    
    def create(self, invite_code: InviteCode):
        self.db.add(invite_code)
        self.db.commit()
        self.db.refresh(invite_code)
        return invite_code

