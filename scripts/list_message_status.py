
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.message_status import MessageStatus
from app.models.message import Message  # FK resolution
from app.models.user import User  # FK resolution


def list_message_status():
    db = SessionLocal()
    try:
        for s in db.query(MessageStatus).all():
            print(f"id={s.id} message={s.message_id} user={s.user_id} delivered={s.delivered_at} read={s.read_at}")
    finally:
        db.close()


if __name__ == "__main__":
    list_message_status()