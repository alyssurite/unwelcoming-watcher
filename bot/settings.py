"""Settings module"""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # database connection
    db_uri: str = Field("sqlite:///database.db")

    # telegram tokens
    api_id: str
    api_hash: str
    bot_token: str

    # log settings
    log_settings_file: Path = Field("./settings.toml")


bot_settings = Settings()
