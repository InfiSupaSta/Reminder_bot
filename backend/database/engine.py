import os
from sqlalchemy import create_engine


engine = create_engine(os.getenv('POSTGRES_URL'), echo=False, future=True)
