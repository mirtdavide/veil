import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User


def list_users():
    db = SessionLocal()
    try:
        for u in db.query(User).all():
            print(f"id={u.id} username={u.username} email={u.email} active={u.is_active} can_invite={u.can_invite}")
    finally:
        db.close()


if __name__ == "__main__":
    list_users()