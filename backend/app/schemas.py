from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EventBase(BaseModel):
    source: str
    title: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    language: Optional[str] = None
    channel_name: Optional[str] = None
    manual_location: bool = False


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    manual_location: Optional[bool] = None


class EventOut(EventBase):
    id: str
    geocoding_confidence: Optional[float] = None
    event_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ChannelBase(BaseModel):
    username: str
    name: Optional[str] = None
    description: Optional[str] = None


class ChannelCreate(ChannelBase):
    pass


class ChannelOut(ChannelBase):
    id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GeocodeSuggestion(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    confidence: float
