from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.middleware import IPWhitelistMiddleware
from app.routers import events, channels, gdelt


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Telegram Dashboard API", version="1.0.0", lifespan=lifespan)

app.add_middleware(IPWhitelistMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(channels.router, prefix="/api/channels", tags=["channels"])
app.include_router(gdelt.router, prefix="/api/gdelt", tags=["gdelt"])


@app.get("/health")
async def health():
    return {"status": "ok"}
