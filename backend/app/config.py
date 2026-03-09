from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./dashboard.db"
    telegram_api_id: int = 0
    telegram_api_hash: str = ""
    telegram_phone: str = ""
    telegram_session: str = "telegram_session"
    gdelt_fetch_interval_minutes: int = 15
    nominatim_user_agent: str = "telegram-dashboard/1.0"
    # Kommaseparert liste med tillatte IP-adresser eller CIDR-subnett.
    # Eksempel: "192.168.1.1,10.0.0.0/8"
    # Tom streng betyr at alle IP-adresser er tillatt.
    allowed_ips: str = ""
    # Sett til True kun når backend kjøres bak en omvendt proxy (f.eks. Nginx)
    # som videresender ekte klient-IP i X-Forwarded-For-headeren.
    # La stå False (standard) for å unngå header-forfalskning.
    trust_forwarded_for: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
