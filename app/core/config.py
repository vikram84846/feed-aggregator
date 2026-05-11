"""This module defines the app configuration and enviornment variable injection into the system"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Settings class defines the configuration, enviornment variables for the app
        variables:
            - DB_URL: database connection url
            - ENV: enviornment fo the app (examples: prod,dev,stage )
    """

    DB_URL: str
    ENV: str

    # jwt essintials
    SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINS: int = 30
    model_config = SettingsConfigDict(extra="forbid", env_file=".env")


@lru_cache
def get_settings():
    """return the app configuration Settings object"""
    return Settings()
