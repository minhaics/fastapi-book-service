from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import urlparse, urlunparse

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    
    # Tự động làm sạch DATABASE_URL để loại bỏ query string
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        parsed_url = urlparse(self.DATABASE_URL)
        self.DATABASE_URL = urlunparse(
            parsed_url._replace(query="")
        )  # Xóa query string

    model_config = SettingsConfigDict(
        env_file=".env",  # Đọc từ file .env
        case_sensitive=True,  # Phân biệt chữ hoa/thường
        extra="ignore",
    )

Config = Settings()
