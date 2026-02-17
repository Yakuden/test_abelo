from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    author = Column(String, nullable=False, default="system")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
