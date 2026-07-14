from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Create a SQLAlchemy engine
engine = create_engine(settings.database_url, echo=True)

# Create a SQLAlchemy session
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass