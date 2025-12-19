# config.py
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # --- 基础配置 ---
    APP_NAME: str = "Amazon Cable API"
    API_V1_STR: str = "/api/v1"
    
    # --- 数据库 ---
    # 默认使用 SQLite，生产环境可通过 .env 覆盖为 PostgreSQL
    DATABASE_URL: str = "sqlite:///./amazon_cable.db"
    
    # --- 安全与认证 ---
    # 生产环境必须在 .env 中设置复杂的随机字符串
    SECRET_KEY: str = "dev_secret_key_change_this_in_production" 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # --- 初始化数据 (Seeding) ---
    FIRST_SUPERUSER: str = "admin@amazoncable.com"
    FIRST_SUPERUSER_PASSWORD: str = "456dsa"
    
    # --- 爬虫/第三方接口 ---
    SINA_API_URL: str = "http://hq.sinajs.cn/list=nf_CU0"
    EXCHANGE_RATE_API: str = "https://api.exchangerate-api.com/v4/latest/USD"

    # 配置：自动读取 .env 文件
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

# 实例化，供其他模块导入
settings = Settings()