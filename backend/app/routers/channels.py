from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models import TelegramChannel
from app.schemas import ChannelCreate, ChannelOut

router = APIRouter()


@router.get("/", response_model=List[ChannelOut])
async def list_channels(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TelegramChannel))
    return result.scalars().all()


@router.post("/", response_model=ChannelOut, status_code=201)
async def add_channel(channel_in: ChannelCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(TelegramChannel).where(TelegramChannel.username == channel_in.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Channel already exists")

    channel = TelegramChannel(**channel_in.model_dump())
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return channel


@router.patch("/{channel_id}/toggle")
async def toggle_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TelegramChannel).where(TelegramChannel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    channel.active = not channel.active
    await db.commit()
    return {"id": channel.id, "active": channel.active}


@router.delete("/{channel_id}", status_code=204)
async def delete_channel(channel_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TelegramChannel).where(TelegramChannel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    await db.delete(channel)
    await db.commit()
