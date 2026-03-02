import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text, Boolean, Integer
from sqlalchemy.dialects.sqlite import TEXT as SQLITE_TEXT
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(20), nullable=False)  # 'telegram' or 'gdelt'
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(1000), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_name = Column(String(500), nullable=True)
    geocoding_confidence = Column(Float, nullable=True)
    language = Column(String(10), nullable=True)
    channel_name = Column(String(200), nullable=True)
    event_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    manual_location = Column(Boolean, default=False)


class TelegramChannel(Base):
    __tablename__ = "telegram_channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=True)
    username = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
