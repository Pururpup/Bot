from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    API_URL: HttpUrl
    BOT_TOKEN: str
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

config = Config()

