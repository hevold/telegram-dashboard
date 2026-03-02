from fastapi import APIRouter, BackgroundTasks
from app.services.gdelt_service import fetch_gdelt_events

router = APIRouter()


@router.post("/fetch")
async def trigger_gdelt_fetch(background_tasks: BackgroundTasks):
    """Manually trigger a GDELT fetch."""
    background_tasks.add_task(fetch_gdelt_events)
    return {"message": "GDELT fetch started in background"}
