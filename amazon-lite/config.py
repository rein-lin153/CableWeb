import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./amazon_cable.db"
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天
    
    # 初始管理员配置
    FIRST_SUPERUSER: str = "admin@amazoncable.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin888"

    # 【关键修复】补充缺失的 API 配置
    SINA_API_URL: str = "http://hq.sinajs.cn/list=nf_CU0"
    EXCHANGE_RATE_API: str = "https://api.exchangerate-api.com/v4/latest/USD"

    # Pydantic v2 配置
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()