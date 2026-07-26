import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember
from app.models.user import User  # FK resolution


def list_conversations():
    db = SessionLocal()
    try:
        for c in db.query(Conversation).all():
            member_ids = [m.user_id for m in db.query(ConversationMember).filter(ConversationMember.conversation_id == c.id).all()]
            print(f"id={c.id} type={c.type} name={c.name} created_by={c.created_by} members={member_ids}")
    finally:
        db.close()


if __name__ == "__main__":
    list_conversations()