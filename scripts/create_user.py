import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def create_user(username: str, email: str, password: str):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User {email} already exists.")
            return
        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            public_key=None,
            can_invite=False,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"User created: {user.username} (id={user.id})")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python scripts/create_user.py <username> <email> <password>")
        sys.exit(1)
    create_user(sys.argv[1], sys.argv[2], sys.argv[3])