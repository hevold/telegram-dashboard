from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventOut, EventUpdate
from app.services.nlp_service import geocode_text

router = APIRouter()


@router.get("/", response_model=List[EventOut])
async def list_events(
    source: Optional[str] = Query(None, description="Filter by source: telegram or gdelt"),
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
):
    query = select(Event).order_by(desc(Event.event_date)).limit(limit)
    if source:
        query = query.where(Event.source == source)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/map", response_model=List[EventOut])
async def list_map_events(
    source: Optional[str] = Query(None),
    limit: int = Query(500, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Events that have coordinates – used for map rendering."""
    query = (
        select(Event)
        .where(Event.latitude.is_not(None))
        .where(Event.longitude.is_not(None))
        .order_by(desc(Event.event_date))
        .limit(limit)
    )
    if source:
        query = query.where(Event.source == source)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=EventOut, status_code=201)
async def create_event(event_in: EventCreate, db: AsyncSession = Depends(get_db)):
    event = Event(**event_in.model_dump())

    # Auto-geocode if no coordinates provided
    if event.latitude is None and event.content:
        suggestion = await geocode_text(event.content)
        if suggestion:
            event.latitude = suggestion["latitude"]
            event.longitude = suggestion["longitude"]
            event.location_name = event.location_name or suggestion["location_name"]
            event.geocoding_confidence = suggestion["confidence"]

    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.patch("/{event_id}", response_model=EventOut)
async def update_event_location(
    event_id: str, update: EventUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    await db.commit()
    await db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    await db.delete(event)
    await db.commit()
