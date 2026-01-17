"""
Database configuration and session management.
"""
import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Use environment variable or default to local file
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./manualarr.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# pylint: disable=invalid-name
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency generator for database sessions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize FTS table
def init_fts(db_engine):
    with db_engine.connect() as conn:
        # Create FTS table for full-text search
        # manual_id and page_number are unindexed (stored but not searchable themselves via FTS match syntax effectively, or just kept for reference)
        conn.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS manual_fts USING fts5(
                manual_id UNINDEXED, 
                page_number UNINDEXED, 
                content
            );
        """))
        # Create trigger to clean up FTS when manual is deleted?
        # SQLite FTS doesn't support foreign keys. We handle deletion manually in service.