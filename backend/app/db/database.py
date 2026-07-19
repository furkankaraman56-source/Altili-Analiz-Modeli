"""
Database engine and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./aam.db"

# Database Engine
engine = create_engine(
    DATABASE_URL,
    echo=True
)

# Session factory used by FastAPI request dependencies.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI dependency: provides one database session per request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()