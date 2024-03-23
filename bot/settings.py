"""Bot settings"""

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

    # cache directory
    cache_dir: Path = Field("./.cache")

    # bot persistence
    persist_file: Path = Field("./.bot_data")

    # su token
    su_token: str = Field(min_length=30)


bot_settings = Settings()
