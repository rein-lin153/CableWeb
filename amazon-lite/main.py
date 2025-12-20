import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select

import models, crud
from database import AsyncSessionLocal, engine
from config import settings
from tasks import update_copper_price_task

# 🟢 确保这里导入了 specs
from routers import auth, users, products, orders, news, inquiries, specs, admin_costs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 初始化表
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    
    # 2. 初始化超级管理员
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(models.User).filter(models.User.email == settings.FIRST_SUPERUSER))
        if not result.scalars().first():
            admin = models.User(
                email=settings.FIRST_SUPERUSER,
                username="Admin",
                hashed_password=crud.get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                role="admin", is_admin=True, is_active=True, company_name="HQ"
            )
            db.add(admin)
            await db.commit()

    # 3. 立即执行一次并启动调度器
    try:
        await update_copper_price_task()
        if not scheduler.get_jobs():
            scheduler.add_job(update_copper_price_task, 'interval', hours=1)
            scheduler.start()
    except Exception as e:
        print(f"Task Error: {e}")
        
    yield
    if scheduler.running: scheduler.shutdown()

app = FastAPI(title="Amazon Cable API", version="1.1.0", lifespan=lifespan)

# Middlewares & Static
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
os.makedirs(os.path.join(STATIC_DIR, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 🟢 注册路由 (Fix: 给 products 加上明确的 prefix)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])

# 🔥 重点修改这一行：
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])

app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(news.router, prefix="/api/v1/news", tags=["News"])
app.include_router(inquiries.router, prefix="/api/v1/inquiries", tags=["Inquiries"])
app.include_router(specs.router, prefix="/api/v1/specs", tags=["Specs"])
app.include_router(admin_costs.router) # admin_costs 内部自带了完整 prefix，保持现状即可


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
