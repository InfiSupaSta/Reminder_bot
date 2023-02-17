from backend.database.engine import engine

from sqlalchemy.orm import sessionmaker

__all__ = [
    'session',
]

Session = sessionmaker(bind=engine)
session = Session()
