from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # PostgreSQL
    database_url: str

    # Redis
    redis_url: str

    # JWT authentication
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60

    # Redis Streams
    stream_name: str = "chat:messages"
    consumer_group: str = "chat-workers"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()