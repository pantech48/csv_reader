""" Database connection and session management. """

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from config import DATABASE_URL

SQLALCHEMY_DATABASE_URL = DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db() -> SessionLocal:
    """Get a database connection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
