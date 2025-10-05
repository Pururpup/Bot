from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    API_URL: HttpUrl
    BOT_TOKEN: str

config = Config()
