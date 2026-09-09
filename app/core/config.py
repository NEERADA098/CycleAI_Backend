from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "CycleAI Backend"
    version: str = "1.0.0"
    environment: str = "development"
    database_url: str
    secret_key: str
    anthropic_api_key: str = ""
    groq_api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
