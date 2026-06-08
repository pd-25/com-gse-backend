from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.database.config import databaseconfig
from typing import Generator

# Create the SQLAlchemy engine
SQLALCHEMY_DATABASE_URL = databaseconfig.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SESSIONLOCAL = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    db = SESSIONLOCAL()
    try:
        yield db
    finally:
        db.close()