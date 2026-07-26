import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.message import Message
from app.models.conversation import Conversation  # FK resolution
from app.models.user import User  # FK resolution


def list_messages():
    db = SessionLocal()
    try:
        for m in db.query(Message).all():
            print(f"id={m.id} conv={m.conversation_id} sender={m.sender_id} type={m.type} content={m.content_encrypted[:50]}")
    finally:
        db.close()


if __name__ == "__main__":
    list_messages()