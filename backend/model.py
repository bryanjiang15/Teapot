import sqlite3
from fastapi import Depends
from typing import Generator
from contextlib import contextmanager
import backend

def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Dependency that provides a database connection.
    Usage: add 'db: sqlite3.Connection = Depends(get_db)' to your route parameters
    """
    db = sqlite3.connect(backend.DATABASE_FILENAME)
    db.execute('PRAGMA foreign_keys = ON')
    try:
        yield db
        db.commit()
    finally:
        db.close()

# Helper context manager for use outside of routes
@contextmanager
def get_db_context():
    db = sqlite3.connect(backend.DATABASE_FILENAME)
    db.execute('PRAGMA foreign_keys = ON')
    try:
        yield db
        db.commit()
    finally:
        db.close()
