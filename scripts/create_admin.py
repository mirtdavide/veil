import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

def create_admin(username: str, email: str, password: str):
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User {email} already exists.")
            return

        admin = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            public_key=None,
            can_invite=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin created: {admin.username} (id={admin.id})")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python scripts/create_admin.py <username> <email> <password>")
        sys.exit(1)

    db = SessionLocal()
    admin = User(
        username=sys.argv[1],
        email=sys.argv[2],
        hashed_password=hash_password(sys.argv[3]),
        public_key=None,
        can_invite=True,
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"Admin created: {admin.username} (id={admin.id})")
    db.close()