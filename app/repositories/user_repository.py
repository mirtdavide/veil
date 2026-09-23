

#Repository for user-related database operations
from app.models.user import User
from sqlalchemy.orm import Session


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    
    
    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    #Create a new user in the database
    def create(self, user: User):
        self.db.add(user)
        self.db.commit()
        #Refresh the user instance to get the updated data from the database
        self.db.refresh(user)   
        return user
    
    def update(self, user: User):
            self.db.commit()
            self.db.refresh(user)
            return user

    #Case-insensitive partial match on username, excluding the searching user, capped to 20 results
    def search_by_username(self, query: str, exclude_user_id: int) -> list[User]:
        return self.db.query(User).filter(
            User.username.ilike(f"%{query}%"),
            User.id != exclude_user_id
        ).limit(20).all()