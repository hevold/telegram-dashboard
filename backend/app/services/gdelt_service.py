"""
GDELT 2.0 service.
Downloads the latest 15-minute event export, parses it, and stores events.
"""
import io
import logging
import zipfile
from datetime import datetime
import httpx
import pandas as pd
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import Event

logger = logging.getLogger(__name__)

GDELT_LASTUPDATE_URL = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

# GDELT 2.0 export CSV column names (61 columns)
GDELT_COLUMNS = [
    "GLOBALEVENTID", "SQLDATE", "MonthYear", "Year", "FractionDate",
    "Actor1Code", "Actor1Name", "Actor1CountryCode", "Actor1KnownGroupCode",
    "Actor1EthnicCode", "Actor1Religion1Code", "Actor1Religion2Code",
    "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code",
    "Actor2Code", "Actor2Name", "Actor2CountryCode", "Actor2KnownGroupCode",
    "Actor2EthnicCode", "Actor2Religion1Code", "Actor2Religion2Code",
    "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code",
    "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode",
    "QuadClass", "GoldsteinScale", "NumMentions", "NumSources",
    "NumArticles", "AvgTone",
    "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code", "Actor1Geo_Lat",
    "Actor1Geo_Long", "Actor1Geo_FeatureID",
    "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code", "Actor2Geo_ADM2Code", "Actor2Geo_Lat",
    "Actor2Geo_Long", "Actor2Geo_FeatureID",
    "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code", "ActionGeo_ADM2Code", "ActionGeo_Lat",
    "ActionGeo_Long", "ActionGeo_FeatureID",
    "DATEADDED", "SOURCEURL",
]


async def _get_latest_export_url() -> str | None:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(GDELT_LASTUPDATE_URL)
        resp.raise_for_status()
    # Each line: "<size> <md5> <url>"
    for line in resp.text.strip().splitlines():
        parts = line.strip().split(" ")
        if len(parts) == 3 and "export.CSV.zip" in parts[2]:
            return parts[2]
    return None


async def fetch_gdelt_events() -> int:
    """Fetch latest GDELT export and store new events. Returns count of new events."""
    try:
        export_url = await _get_latest_export_url()
        if not export_url:
            logger.warning("Could not find GDELT export URL")
            return 0

        logger.info(f"Downloading GDELT export: {export_url}")
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(export_url)
            resp.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            csv_name = z.namelist()[0]
            with z.open(csv_name) as f:
                df = pd.read_csv(
                    f,
                    sep="\t",
                    header=None,
                    names=GDELT_COLUMNS,
                    low_memory=False,
                )

        # Filter: only events with coordinates and a source URL
        df = df.dropna(subset=["ActionGeo_Lat", "ActionGeo_Long", "SOURCEURL"])
        df = df[df["ActionGeo_Lat"] != 0]

        new_count = 0
        async with AsyncSessionLocal() as db:
            for _, row in df.iterrows():
                event_id = str(row["GLOBALEVENTID"])
                existing = await db.execute(
                    select(Event).where(Event.id == f"gdelt-{event_id}")
                )
                if existing.scalar_one_or_none():
                    continue

                event_date_str = str(row["SQLDATE"])
                try:
                    event_date = datetime.strptime(event_date_str, "%Y%m%d")
                except ValueError:
                    event_date = datetime.utcnow()

                event = Event(
                    id=f"gdelt-{event_id}",
                    source="gdelt",
                    title=str(row.get("ActionGeo_FullName", ""))[:500] or None,
                    content=None,
                    url=str(row["SOURCEURL"])[:1000],
                    latitude=float(row["ActionGeo_Lat"]),
                    longitude=float(row["ActionGeo_Long"]),
                    location_name=str(row.get("ActionGeo_FullName", ""))[:500] or None,
                    geocoding_confidence=1.0,
                    event_date=event_date,
                )
                db.add(event)
                new_count += 1

            await db.commit()

        logger.info(f"GDELT: stored {new_count} new events")
        return new_count

    except Exception as e:
        logger.error(f"GDELT fetch failed: {e}")
        return 0
