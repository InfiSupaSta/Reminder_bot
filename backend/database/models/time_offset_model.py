from datetime import datetime

from backend.database.base import Base

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class TimeOffset(Base):
    __tablename__ = 'time_offset'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.telegram_id"))
    offset = relationship('User',
                          cascade='delete',
                          back_populates='offset')
    time_offset = Column(String, default=None)
    last_modified = Column(DateTime, default=datetime.now(), onupdate=datetime.now)

    def __str__(self):
        return f'{self.offset.telegram_id} : {self.time_offset}'
