from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    ADMIN_ID: int
    USER_NAME: str
    BOT_PERSONA: str  
    NOTION_API_KEY: str
    NOTION_HABITS_DB_ID: str
    NOTION_MEMORY_DB_ID: str
    DEEPSEEK_API_KEY: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

config = Settings()
