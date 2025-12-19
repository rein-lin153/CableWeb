# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import settings # <--- 导入配置

# 使用配置中的 URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# SQLite 特有的参数 check_same_thread，Postgres 不需要
connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()