from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./dashboard.db"
    telegram_api_id: int = 0
    telegram_api_hash: str = ""
    telegram_phone: str = ""
    telegram_session: str = "telegram_session"
    gdelt_fetch_interval_minutes: int = 15
    nominatim_user_agent: str = "telegram-dashboard/1.0"

    class Config:
        env_file = ".env"


settings = Settings()
