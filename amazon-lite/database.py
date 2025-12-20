from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# 1. 创建异步引擎
# check_same_thread=False 是 SQLite 异步模式必须的参数
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False, # 如果需要查看 SQL 日志，改为 True
    connect_args=connect_args,
)

# 2. 创建 Session 工厂
# main.py 引用的是 AsyncSessionLocal，这里必须匹配
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 增加一个别名 SessionLocal，防止有些文件（如 lifespan）还在用旧名字
SessionLocal = AsyncSessionLocal

# 3. 创建模型基类
Base = declarative_base()

# 4. 定义数据库依赖函数 get_db
# FastAPI 的路由依赖会用到这个
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()