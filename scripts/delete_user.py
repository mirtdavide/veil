import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.exc import IntegrityError
from app.core.database import SessionLocal
from app.models.user import User


def delete_user(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            print(f"No user with id={user_id}.")
            return
        confirm = input(f"Delete '{user.username}' ({user.email})? [y/N] ")
        if confirm.lower() != "y":
            print("Aborted.")
            return
        db.delete(user)
        db.commit()
        print(f"User {user.username} (id={user_id}) deleted.")
    except IntegrityError:
        db.rollback()
        print("Cannot delete: user is referenced by other rows (invites, conversations, messages...).")
        print("Tip: set is_active=False instead (soft delete), or delete the related rows first.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/delete_user.py <user_id>")
        sys.exit(1)
    delete_user(int(sys.argv[1]))