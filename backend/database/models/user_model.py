from datetime import datetime
from uuid import uuid4

from backend.database.base import Base

from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    telegram_id = Column(Integer, unique=True)
    joined_at = Column(DateTime, default=datetime.now())
    tasks = relationship('Task', cascade="all, delete", back_populates='user')
    is_active = Column(Boolean, default=False)

    def __repr__(self):
        return f'TelegramID : {self.telegram_id}'
