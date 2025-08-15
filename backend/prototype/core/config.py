from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENCRYPTION_KEY: str
    BACKEND_URL: str
    OPENAI_SECRET: str

    HOST: str = "127.0.0.1"
    PORT: int = 8080

    MONGODB_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

settings: Settings = Settings()