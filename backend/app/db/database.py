from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./aam.db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)