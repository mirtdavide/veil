import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal
from app.models.invite_code import InviteCode
from app.models.user import User  # needed for foreign key resolution
import secrets

def create_invite(created_by_id: int, expires_hours: int = 24):
    db = SessionLocal()
    code = secrets.token_urlsafe(16)
    invite = InviteCode(
        code=code,
        created_by=created_by_id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    print(f"Invite code created: {invite.code}")
    print(f"Expires at: {invite.expires_at}")
    db.close()

if __name__ == "__main__":
    create_invite(created_by_id=3)