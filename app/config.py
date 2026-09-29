import re
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    BOT_TOKEN: str
    DATABASE_URL: str
    MODE: Literal["polling", "webhook"] = "polling"

    # webhook
    WEBHOOK_URL: str = ""
    WEBHOOK_SECRET: str = ""
    WEBHOOK_PATH: str = "/webhook"
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    SLOTS_COUNT: int = 17

    @field_validator("DATABASE_URL")
    @classmethod
    def _normalize_db_url(cls, v: str) -> str:
        """Neon/Render дають postgres:// або postgresql://?sslmode=require,
        а asyncpg потребує драйвера в схемі та параметра ssl замість sslmode."""
        v = re.sub(r"^postgres(ql)?://", "postgresql+asyncpg://", v)
        v = v.replace("sslmode=", "ssl=")
        # asyncpg не розуміє channel_binding
        v = re.sub(r"[&?]channel_binding=[^&]*", "", v)
        v = v.replace("?&", "?").rstrip("?&")
        return v

    @model_validator(mode="after")
    def _check_webhook(self) -> "Settings":
        if self.MODE == "webhook" and not (self.WEBHOOK_URL and self.WEBHOOK_SECRET):
            raise ValueError("MODE=webhook потребує WEBHOOK_URL і WEBHOOK_SECRET")
        return self


settings = Settings()
