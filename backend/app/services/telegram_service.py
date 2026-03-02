"""
Telegram service using Telethon.
Monitors configured channels and stores new messages as events.
"""
import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import Channel
from sqlalchemy import select
from app.config import settings
from app.database import AsyncSessionLocal
from app.models import Event, TelegramChannel
from app.services.nlp_service import geocode_text

logger = logging.getLogger(__name__)

_client: TelegramClient | None = None


def get_client() -> TelegramClient:
    global _client
    if _client is None:
        _client = TelegramClient(
            settings.telegram_session,
            settings.telegram_api_id,
            settings.telegram_api_hash,
        )
    return _client


async def start_telegram_listener():
    """Start listening to all active channels in the database."""
    if not settings.telegram_api_id or not settings.telegram_api_hash:
        logger.warning("Telegram credentials not configured – listener not started")
        return

    client = get_client()
    await client.start(phone=settings.telegram_phone)
    logger.info("Telegram client started")

    @client.on(events.NewMessage)
    async def handler(event_msg):
        chat = await event_msg.get_chat()
        username = getattr(chat, "username", None)
        if not username:
            return

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(TelegramChannel).where(
                    TelegramChannel.username == username,
                    TelegramChannel.active == True,
                )
            )
            channel = result.scalar_one_or_none()
            if not channel:
                return

        message = event_msg.message
        if not message or not message.text:
            return

        text = message.text
        msg_id = message.id
        channel_url = f"https://t.me/{username}/{msg_id}"

        # Auto-geocode
        geo = await geocode_text(text)

        async with AsyncSessionLocal() as db:
            ev = Event(
                source="telegram",
                title=text[:200],
                content=text,
                url=channel_url,
                channel_name=username,
                latitude=geo["latitude"] if geo else None,
                longitude=geo["longitude"] if geo else None,
                location_name=geo["location_name"] if geo else None,
                geocoding_confidence=geo["confidence"] if geo else None,
                event_date=message.date or datetime.utcnow(),
            )
            db.add(ev)
            await db.commit()
            logger.info(f"Stored Telegram message from @{username} (msg {msg_id})")

    await client.run_until_disconnected()


async def fetch_channel_history(username: str, limit: int = 50) -> int:
    """Fetch recent messages from a channel."""
    client = get_client()
    if not client.is_connected():
        await client.start(phone=settings.telegram_phone)

    new_count = 0
    try:
        async for message in client.iter_messages(username, limit=limit):
            if not message.text:
                continue

            geo = await geocode_text(message.text)
            channel_url = f"https://t.me/{username}/{message.id}"

            async with AsyncSessionLocal() as db:
                existing = await db.execute(
                    select(Event).where(Event.url == channel_url)
                )
                if existing.scalar_one_or_none():
                    continue

                ev = Event(
                    source="telegram",
                    title=message.text[:200],
                    content=message.text,
                    url=channel_url,
                    channel_name=username,
                    latitude=geo["latitude"] if geo else None,
                    longitude=geo["longitude"] if geo else None,
                    location_name=geo["location_name"] if geo else None,
                    geocoding_confidence=geo["confidence"] if geo else None,
                    event_date=message.date or datetime.utcnow(),
                )
                db.add(ev)
                await db.commit()
                new_count += 1

    except Exception as e:
        logger.error(f"Error fetching channel @{username}: {e}")

    return new_count
