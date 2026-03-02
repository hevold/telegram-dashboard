"""
NLP geocoding service.
Uses spaCy for Named Entity Recognition (location extraction)
and Nominatim (OpenStreetMap) for geocoding.
"""
import asyncio
import logging
from typing import Optional, Dict
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from app.config import settings

logger = logging.getLogger(__name__)

_geocoder = Nominatim(user_agent=settings.nominatim_user_agent, timeout=10)

# spaCy models loaded lazily
_nlp_models: Dict = {}


def _load_spacy():
    """Load spaCy models. Called once at first use."""
    global _nlp_models
    if _nlp_models:
        return _nlp_models

    try:
        import spacy

        # Try language-specific models first, fall back to multilingual
        for model_name in ["en_core_web_sm", "xx_ent_wiki_sm"]:
            try:
                _nlp_models[model_name] = spacy.load(model_name)
                logger.info(f"Loaded spaCy model: {model_name}")
            except OSError:
                logger.warning(f"spaCy model not found: {model_name}")

    except ImportError:
        logger.warning("spaCy not installed – NLP geocoding disabled")

    return _nlp_models


def _detect_language(text: str) -> str:
    try:
        from langdetect import detect
        return detect(text)
    except Exception:
        return "en"


def _extract_locations_spacy(text: str) -> list[str]:
    models = _load_spacy()
    if not models:
        return []

    # Pick best available model
    nlp = models.get("en_core_web_sm") or next(iter(models.values()), None)
    if not nlp:
        return []

    doc = nlp(text[:1000])  # limit length for performance
    locations = [
        ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC", "FAC")
    ]
    return locations


def _geocode_location(location_name: str) -> Optional[Dict]:
    try:
        result = _geocoder.geocode(location_name, language="en")
        if result:
            return {
                "location_name": result.address,
                "latitude": result.latitude,
                "longitude": result.longitude,
                "confidence": 0.8,
            }
    except GeocoderTimedOut:
        logger.warning(f"Geocoder timed out for: {location_name}")
    except Exception as e:
        logger.warning(f"Geocoding error for '{location_name}': {e}")
    return None


async def geocode_text(text: str) -> Optional[Dict]:
    """
    Extract location from text using NLP and geocode it.
    Returns dict with latitude, longitude, location_name, confidence.
    """
    loop = asyncio.get_event_loop()

    # Run blocking NLP in thread pool
    locations = await loop.run_in_executor(None, _extract_locations_spacy, text)

    if not locations:
        return None

    # Try each location until one geocodes successfully
    for loc in locations:
        result = await loop.run_in_executor(None, _geocode_location, loc)
        if result:
            return result

    return None


async def geocode_query(query: str) -> Optional[Dict]:
    """Direct geocode of a user-supplied location string."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _geocode_location, query)
    return result
