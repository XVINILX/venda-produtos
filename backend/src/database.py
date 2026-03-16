# backend/src/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./wisesales.db"  # Ajuste o nome do arquivo

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Importante para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()