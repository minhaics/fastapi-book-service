from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import urlparse, urlunparse

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_HOST: str
    REDIS_PORT: str
    # add these
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str
    REDIS_URL: str = "redis://localhost:6379/0"

    # Tự động làm sạch DATABASE_URL để loại bỏ query string
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        parsed_url = urlparse(self.DATABASE_URL)
        # Làm sạch REDIS_URL để loại bỏ khoảng trắng thừa
        self.REDIS_URL = self.REDIS_URL.strip()
        
        self.DATABASE_URL = urlunparse(
            parsed_url._replace(query="")
        )  # Xóa query string

    model_config = SettingsConfigDict(
        env_file=".env",  # Đọc từ file .env
        case_sensitive=True,  # Phân biệt chữ hoa/thường
        extra="ignore",
    )

Config = Settings()

broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup = True
