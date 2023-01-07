from datetime import datetime

from sqlalchemy.orm import relationship

from backend.database.base import Base

from sqlalchemy import Column, Integer, DateTime, Boolean, Text, ForeignKey


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.telegram_id"))
    user = relationship('User', back_populates='tasks')
    # TODO check if created_at timestamp working correctly
    created_at = Column(DateTime, default=datetime.now())
    time_to_remind = Column(DateTime)
    is_regular_remind = Column(Boolean, default=False)
    description = Column(Text)
    is_done = Column(Boolean, default=False)

    def __str__(self):
        return f'{self.user.telegram_id} : {self.description}'
