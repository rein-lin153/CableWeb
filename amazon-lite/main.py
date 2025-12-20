import shutil
import os
from typing import List, Optional
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import magic  # [Step C.3] 引入 Magic 库用于文件头校验
from apscheduler.schedulers.asyncio import AsyncIOScheduler # 异步调度器
import random # 记得导入这个


from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# sqlalchemy async imports
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
# Note: "Session" import removed/replaced with AsyncSession in type hints

from jose import JWTError, jwt
from apscheduler.schedulers.background import BackgroundScheduler

# Local imports
import models, schemas, crud
from database import AsyncSessionLocal, engine, get_db
from config import settings
from tasks import update_copper_price_task

# 1. 安全修复：图片深度校验
async def validate_image_security(file: UploadFile):
    header = await file.read(2048)
    await file.seek(0)
    mime = magic.from_buffer(header, mime=True)
    if not mime.startswith('image/'):
        raise HTTPException(status_code=400, detail=f"非法文件类型: {mime}")
# =========================================================
# 1. Setup & Config
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads") # 定义上传目录

scheduler = BackgroundScheduler()


# 异步生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 创建表结构
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    
    # 2. 初始化超级管理员
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(models.User).filter(models.User.email == settings.FIRST_SUPERUSER)
        )
        user = result.scalars().first()
        if not user:
            print(f"⚡ 未找到管理员，正在创建...")
            admin_user = models.User(
                email=settings.FIRST_SUPERUSER,
                username="Admin",
                hashed_password=crud.get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                role="admin",
                is_admin=True,
                is_active=True,
                company_name="Amazon Cable HQ"
            )
            db.add(admin_user)
            await db.commit()
            print(f"✅ 管理员创建成功: {settings.FIRST_SUPERUSER}")

    # 3. 【关键修复】立即执行一次铜价获取，防止数据库为空
    try:
        await update_copper_price_task()
    except Exception as e:
        print(f"⚠️ 初始铜价获取失败: {e}")

    # 4. 启动调度器 (后续每小时执行一次)
    try:
        # 注意：如果之前添加过任务，这里add_job可能会重复，但在 lifespan 里通常没事
        if not scheduler.get_jobs():
            scheduler.add_job(update_copper_price_task, 'interval', hours=1)
            scheduler.start()
            print("⏰ 定时任务调度器已启动")
    except Exception as e:
        print(f"⚠️ 调度器启动异常: {e}")

    yield
    
    if scheduler.running:
        scheduler.shutdown()

app = FastAPI(title="Amazon Cable API", version="1.0.0", lifespan=lifespan)

# Mount Static Files
os.makedirs(UPLOAD_DIR, exist_ok=True) # 确保上传目录存在
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# =========================================================
# 2. Dependencies & Helpers
# =========================================================

# --- 修改 get_db 依赖 ---
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if await crud.is_token_revoked(db, token):
        raise HTTPException(status_code=401, detail="Token has been revoked", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise credentials_exception
    except JWTError: raise credentials_exception
    
    user = await crud.get_user_by_email(db, email=email)
    if user is None: raise credentials_exception
    if not user.is_active: raise HTTPException(status_code=400, detail="Inactive user")
    return user

async def get_current_active_superuser(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

# --- [Step C.3] 文件安全校验函数 ---

async def validate_image(file: UploadFile):
    """
    深度校验上传文件：
    1. 检查文件头 (Magic Number) 确认真实的 MIME 类型。
    2. 检查文件大小 (不信任 Content-Length 头)。
    """
    # 限制配置
    MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB
    ALLOWED_MIMES = ["image/jpeg", "image/png", "image/webp"]

    # 1. 检查文件头 (前2KB足够判断大多数图片)
    header = await file.read(2048)
    # 务必重置指针，否则后续保存时文件会残缺
    await file.seek(0) 

    if not header:
        raise HTTPException(status_code=400, detail="Empty file")

    # 使用 python-magic 获取真实 MIME
    try:
        mime_type = magic.from_buffer(header, mime=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File analysis failed: {str(e)}")

    if mime_type not in ALLOWED_MIMES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type: {mime_type}. Only JPEG, PNG, WEBP allowed."
        )

    # 2. 检查文件实际大小
    # 方法A: 移动指针到末尾获取大小 (适用于 SpooledTemporaryFile)
    await file.seek(0, 2) # Seek to end
    file_size = file.file.tell()
    await file.seek(0) # Reset to start

    if file_size > MAX_FILE_SIZE:
         raise HTTPException(status_code=400, detail=f"File too large. Limit is {MAX_FILE_SIZE/1024/1024}MB")

# =========================================================
# 3. API Routes
# =========================================================

# --- Auth ---

@app.post("/api/v1/auth/login", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_email(db, form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.post("/api/v1/auth/logout", status_code=200)
async def logout(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    await crud.revoke_token(db, token)
    return {"message": "Successfully logged out"}

@app.post("/api/v1/auth/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user=user)

# --- Users ---

@app.get("/api/v1/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
    

@app.get("/api/v1/users/", response_model=List[schemas.UserResponse])
async def read_users(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    return await crud.get_users(db, skip=skip, limit=limit)

@app.post("/api/v1/users/", response_model=schemas.UserResponse, status_code=201)
async def create_user_by_admin(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    user = await crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    return await crud.create_user(db, user_in)

@app.put("/api/v1/users/{user_id}", response_model=schemas.UserResponse)
async def update_user_detail(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_active_superuser)
):
    if user_id == current_admin.id and user_in.role and user_in.role != "admin":
        raise HTTPException(status_code=400, detail="Cannot change your own role to non-admin")
        
    user = await crud.update_user(db, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/api/v1/users/{user_id}/role", response_model=schemas.UserResponse)
async def update_user_role(
    user_id: int,
    role_update: schemas.UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_active_superuser)
):
    # Async Fetch
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user_to_edit = result.scalars().first()
    
    if not user_to_edit:
        raise HTTPException(status_code=404, detail="User not found")

    if user_id == current_admin.id and role_update.is_superuser is False:
        raise HTTPException(status_code=400, detail="Operation not allowed: You cannot remove your own admin privileges.")

    user_to_edit.is_admin = role_update.is_superuser
    await db.commit()
    await db.refresh(user_to_edit)
    return user_to_edit

@app.patch("/api/v1/users/{user_id}/status", response_model=schemas.UserResponse)
async def update_user_status(
    user_id: int,
    status_data: schemas.UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_active_superuser)
):
    # crud.update_user logic handles this via generic update, or specific logic
    # Implementing specific logic here as crud.py might not have update_user_status specifically 
    # (assuming crud.update_user is generic enough or add logic here)
    if user_id == current_admin.id and status_data.is_active is False:
        raise HTTPException(status_code=400, detail="Cannot ban yourself")
    
    # Using generic update
    update_schema = schemas.UserUpdate(is_active=status_data.is_active)
    user = await crud.update_user(db, user_id, update_schema)
    
    if not user: 
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/api/v1/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_active_superuser)
):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    # crud.delete_user needs to be implemented or we do it here
    # Assuming crud.py has delete logic or we use execute(delete)
    # Let's assume we implement a simple delete logic here for safety if missing in CRUD
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()

@app.patch("/api/v1/users/{user_id}/discount", response_model=schemas.UserResponse)
async def update_user_discount(
    user_id: int,
    discount_data: schemas.UserDiscountUpdate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    user = await crud.update_user_discount(db, user_id, discount_data.discount_rate)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/v1/users/drivers", response_model=List[schemas.UserResponse])
async def get_drivers(
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    return await crud.get_drivers(db)

# --- Categories ---

@app.get("/api/v1/categories/", response_model=List[schemas.CategoryResponse])
async def read_categories(
    skip: int = 0,
    limit: int = 100,
    flat: bool = True,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_categories(db, skip=skip, limit=limit, flat=flat)

@app.post("/api/v1/categories/", response_model=schemas.CategoryResponse)
async def create_category(
    cat: schemas.CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    # 1. 检查父分类是否存在
    if cat.parent_id:
        res = await db.execute(select(models.Category).filter(models.Category.id == cat.parent_id))
        if not res.scalars().first():
            raise HTTPException(status_code=400, detail="Parent category not found")
    
    # 2. 创建分类 (捕获重复名称)
    new_cat = await crud.create_category(db, cat)
    if not new_cat:
        # 如果 crud 返回 None，说明名称重复
        raise HTTPException(status_code=400, detail="分类名称已存在，请勿重复创建")
    
    # 3. 重新加载并预加载 children 关系 (防止 MissingGreenlet)
    query = select(models.Category)\
        .options(selectinload(models.Category.children))\
        .filter(models.Category.id == new_cat.id)
        
    result = await db.execute(query)
    return result.scalars().first()


@app.put("/api/v1/categories/{cat_id}", response_model=schemas.CategoryResponse)
async def update_category(
    cat_id: int,
    cat_update: schemas.CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    # 1. 检查父分类
    if cat_update.parent_id:
        res = await db.execute(select(models.Category).filter(models.Category.id == cat_update.parent_id))
        if not res.scalars().first():
            raise HTTPException(status_code=400, detail="Parent category not found")
            
    # 2. 更新分类
    db_cat = await crud.update_category(db, cat_id, cat_update)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")

    # 3. 【关键修复】重新加载并预加载 children 关系
    query = select(models.Category)\
        .options(selectinload(models.Category.children))\
        .filter(models.Category.id == db_cat.id)
    
    result = await db.execute(query)
    return result.scalars().first()

@app.delete("/api/v1/categories/{cat_id}", status_code=204)
async def delete_category(
    cat_id: int,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    if not await crud.delete_category(db, cat_id):
        raise HTTPException(status_code=404, detail="Category not found")

# --- Products ---

@app.get("/api/v1/products/")
async def read_products(db: AsyncSession = Depends(get_db)): # 类型改为 AsyncSession
    return await crud.get_products(db) # 加上 await

@app.get("/api/v1/products/{product_id}", response_model=schemas.ProductResponse)
async def read_product_detail(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/api/v1/products/", response_model=schemas.ProductResponse, status_code=201)
async def create_product(
    product: schemas.ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    return await crud.create_product(db=db, product=product)

@app.put("/api/v1/products/{product_id}", response_model=schemas.ProductResponse)
async def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    db_prod = await crud.update_product(db, product_id, product_update)
    if not db_prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_prod

@app.delete("/api/v1/products/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    if not await crud.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")

# --- Cart ---

@app.get("/api/v1/cart/", response_model=List[schemas.CartItemResponse])
async def read_cart(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    items = await crud.get_cart_items(db, current_user.id)
    res = []
    for item in items:
        if not item.variant or not item.variant.product:
            continue
        res.append({
            "id": item.id,
            "variant_id": item.variant_id,
            "quantity": item.quantity,
            "product_name": item.variant.product.name,
            "spec": item.variant.spec,
            "color": item.variant.color,
            "price": item.variant.price,
            "unit": item.variant.unit,
            "image_url": item.variant.product.image_url,
            "subtotal": item.variant.price * item.quantity
        })
    return res

@app.post("/api/v1/cart/", response_model=schemas.CartItemResponse)
async def add_to_cart(
    cart_data: schemas.CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    item = await crud.add_to_cart(db, current_user.id, cart_data.variant_id, cart_data.quantity)
    if not item:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    # Re-fetch or structure the response manually because 'item' might not have loaded relationships immediately after add
    # Ideally crud.add_to_cart should refresh with relationships or we construct response
    # For async safety, let's construct manually or ensure joinedload in CRUD return
    
    # Simple fix: return structured dict if lazy load is issue, but we used selectinload/refresh in CRUD?
    # Actually CRUD refresh might not load relationships.
    # It is safer to re-fetch the item with eager loads to return full schema
    
    # Re-fetch for response
    query = select(models.CartItem)\
        .options(selectinload(models.CartItem.variant).selectinload(models.ProductVariant.product))\
        .filter(models.CartItem.id == item.id)
    res = await db.execute(query)
    full_item = res.scalars().first()
    
    return {
        "id": full_item.id,
        "variant_id": full_item.variant_id,
        "quantity": full_item.quantity,
        "product_name": full_item.variant.product.name,
        "spec": full_item.variant.spec,
        "color": full_item.variant.color,
        "price": full_item.variant.price,
        "unit": full_item.variant.unit,
        "image_url": full_item.variant.product.image_url,
        "subtotal": full_item.variant.price * full_item.quantity
    }

@app.delete("/api/v1/cart/{item_id}")
async def remove_cart_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    success = await crud.remove_from_cart(db, current_user.id, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Deleted"}

# --- Orders ---

@app.post("/api/v1/orders/", response_model=schemas.OrderResponse, status_code=201)
async def create_order(db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    order = await crud.create_order_from_cart(db, current_user.id, current_user.discount_rate)
    if not order: raise HTTPException(status_code=400, detail="Cart is empty")
    return order

@app.get("/api/v1/orders/my", response_model=List[schemas.OrderResponse])
async def read_my_orders(db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return await crud.get_orders(db, user_id=current_user.id)

@app.get("/api/v1/orders/", response_model=List[schemas.OrderResponse])
async def read_orders(
    skip: int = 0, limit: int = 100, q: Optional[str] = None,
    db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    user_id, driver_id = None, None
    if current_user.role == "driver": driver_id = current_user.id
    elif not (current_user.is_admin or current_user.role == "admin"): user_id = current_user.id
    return await crud.get_orders(db, skip=skip, limit=limit, user_id=user_id, driver_id=driver_id, search=q)

@app.get("/api/v1/orders/{order_id}", response_model=schemas.OrderResponse)
async def read_order_detail(order_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    order = await crud.get_order_by_id(db, order_id)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    
    is_admin = current_user.is_admin or current_user.role == "admin"
    is_owner = order.user_id == current_user.id
    is_assigned_driver = order.driver_id == current_user.id
    
    if not (is_admin or is_owner or is_assigned_driver):
        raise HTTPException(status_code=403, detail="Permission denied")
    return order

@app.patch("/api/v1/orders/{order_id}/confirm", response_model=schemas.OrderResponse)
async def confirm_order(order_id: int, db: AsyncSession = Depends(get_db), _: models.User = Depends(get_current_active_superuser)):
    order, error = await crud.confirm_order(db, order_id)
    if error: raise HTTPException(status_code=400, detail=error)
    return order

@app.patch("/api/v1/orders/{order_id}/ship", response_model=schemas.OrderResponse)
async def ship_order(order_id: int, db: AsyncSession = Depends(get_db), _: models.User = Depends(get_current_active_superuser)):
    order, error = await crud.ship_order(db, order_id)
    if error: raise HTTPException(status_code=400, detail=error)
    return order

# 安全校验函数
async def validate_image_security(file: UploadFile):
    # 读取前 2KB 检查文件特征码
    header = await file.read(2048)
    await file.seek(0)
    mime = magic.from_buffer(header, mime=True)
    if not mime.startswith('image/'):
        raise HTTPException(status_code=400, detail=f"非法文件类型: {mime}")

# [Step C.3] 增强版 Complete Order
@app.post("/api/v1/orders/{order_id}/complete", response_model=schemas.OrderResponse)
async def complete_order(
    order_id: int,
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """完成订单并进行安全图片检查"""
    # 1. 先查订单
    order = await crud.get_order_by_id(db, order_id)
    if not order: 
        raise HTTPException(status_code=404, detail="订单未找到")

    # 2. 权限校验 (管理员 或 被指派的司机)
    if current_user.role != "admin" and order.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此订单")

    # 3. 处理文件上传
    if file:
        await validate_image_security(file) # 安全校验
        file_ext = file.filename.split(".")[-1]
        # 文件名加上时间戳防止缓存
        timestamp = int(datetime.now().timestamp())
        file_name = f"order_{order_id}_sign_{timestamp}.{file_ext}"
        file_path = os.path.join(STATIC_DIR, "uploads", file_name)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 保存到数据库的路径
        order.delivery_photo_url = f"/static/uploads/{file_name}"

    # 4. 更新状态
    order.status = models.OrderStatus.COMPLETED
    await db.commit()
    
    # 【关键修复】必须调用 crud.get_order_by_id 重新加载完整数据！
    # 否则 user_email 和 items 字段会报错 MissingGreenlet
    return await crud.get_order_by_id(db, order_id)

@app.patch("/api/v1/orders/{order_id}/cancel", response_model=schemas.OrderResponse)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    order, error = await crud.cancel_order(db, order_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return order

@app.patch("/api/v1/orders/{order_id}/price", response_model=schemas.OrderResponse)
async def update_order_price(
    order_id: int,
    price_data: schemas.OrderPriceUpdate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    order = await crud.update_order_price(db, order_id, price_data.new_price)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.patch("/api/v1/orders/{order_id}/items/{item_id}", response_model=schemas.OrderResponse)
async def update_order_item_price(
    order_id: int,
    item_id: int,
    price_data: schemas.OrderItemPriceUpdate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    updated_order = await crud.update_order_item_price(
        db, order_id=order_id, item_id=item_id, new_unit_price=price_data.new_unit_price
    )
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order Item not found")
    return updated_order

@app.patch("/api/v1/orders/{order_id}/assign", response_model=schemas.OrderResponse)
async def assign_order_driver(
    order_id: int,
    assign_req: schemas.AssignDriverRequest,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    order, error = await crud.assign_driver(db, order_id, assign_req.driver_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return order

@app.post("/api/v1/orders/{order_id}/location", response_model=schemas.OrderResponse)
async def update_order_location(
    order_id: int,
    loc: schemas.DriverLocationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "driver":
        raise HTTPException(status_code=403, detail="Not a driver")
        
    order = await crud.update_driver_location(db, order_id, loc.lat, loc.lng)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/v1/orders/driver/tasks", response_model=List[schemas.OrderResponse])
async def get_my_driver_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "driver":
        raise HTTPException(status_code=403, detail="Not a driver")
    return await crud.get_driver_tasks(db, current_user.id)

# --- News ---

@app.get("/api/v1/news/", response_model=List[schemas.NewsResponse])
async def read_news_list(
    skip: int = 0, limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_news_list(db, skip=skip, limit=limit)

@app.get("/api/v1/news/{news_id}", response_model=schemas.NewsResponse)
async def read_news_detail(news_id: int, db: AsyncSession = Depends(get_db)):
    news = await crud.get_news_by_id(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news

@app.post("/api/v1/news/", response_model=schemas.NewsResponse, status_code=201)
async def create_news(
    news: schemas.NewsCreate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    return await crud.create_news(db, news)

@app.put("/api/v1/news/{news_id}", response_model=schemas.NewsResponse)
async def update_news(
    news_id: int,
    news_update: schemas.NewsUpdate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    news = await crud.update_news(db, news_id, news_update)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news

@app.delete("/api/v1/news/{news_id}", status_code=204)
async def delete_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    success = await crud.delete_news(db, news_id)
    if not success:
        raise HTTPException(status_code=404, detail="News not found")

# --- Specs ---

@app.get("/api/v1/specs/", response_model=List[schemas.TechnicalSpecResponse], tags=["Specs"])
async def read_specs(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_technical_specs(db, skip=skip, limit=limit, category=category, search=search)

@app.post("/api/v1/specs/", response_model=schemas.TechnicalSpecResponse, status_code=201, tags=["Specs"])
async def create_spec(
    spec: schemas.TechnicalSpecCreate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    return await crud.create_technical_spec(db, spec)

@app.put("/api/v1/specs/{spec_id}", response_model=schemas.TechnicalSpecResponse, tags=["Specs"])
async def update_spec(
    spec_id: int,
    spec_update: schemas.TechnicalSpecUpdate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    spec = await crud.update_technical_spec(db, spec_id, spec_update)
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")
    return spec

@app.delete("/api/v1/specs/{spec_id}", status_code=204, tags=["Specs"])
async def delete_spec(
    spec_id: int,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    if not await crud.delete_technical_spec(db, spec_id):
        raise HTTPException(status_code=404, detail="Spec not found")

# --- Misc ---

@app.get("/api/v1/meta/prices", response_model=schemas.CopperDisplayResponse)
async def get_metal_prices(db: AsyncSession = Depends(get_db)):
    # 1. 获取最新的一条记录 (当前价格)
    res = await db.execute(
        select(models.CopperPrice).order_by(models.CopperPrice.updated_at.desc()).limit(1)
    )
    latest = res.scalars().first()
    
    # 如果没有数据，返回默认空值
    if not latest:
        return {
            "CNY": {"source": "无数据", "symbol": "¥", "price": 0.0, "change": 0.0},
            "USD": {"source": "无数据", "symbol": "$", "price": 0.0, "change": 0.0},
            "exchange_rate": 0.0,
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    # 2. 获取“昨天收盘价” (即今天 00:00 之前的最后一条记录)
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    res_prev = await db.execute(
        select(models.CopperPrice)
        .filter(models.CopperPrice.updated_at < today_start) # 关键：找今天之前的数据
        .order_by(models.CopperPrice.updated_at.desc())
        .limit(1)
    )
    prev = res_prev.scalars().first()

    # 3. 计算涨跌额
    cny_change = 0.0
    usd_change = 0.0
    
    if prev:
        cny_change = latest.cny_price - prev.cny_price
        usd_change = latest.usd_price - prev.usd_price

    # 4. 组装返回结果
    return {
        "CNY": {
            "source": "沪铜主连",
            "symbol": "¥",
            "price": latest.cny_price,
            "change": round(cny_change, 2) # 保留两位小数
        },
        "USD": {
            "source": "LME折算",
            "symbol": "$",
            "price": latest.usd_price,
            "change": round(usd_change, 2)
        },
        "exchange_rate": latest.exchange_rate,
        "updated": latest.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.post("/api/v1/inquiries/", response_model=schemas.InquiryResponse)
async def create_inquiry(
    inquiry_in: schemas.InquiryCreate,  # <---【关键点】这里必须是 Schema 对象，不能是 List
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """用户提交询价单 (将购物车内容转为询价单)"""
    # 调用 crud 时传入备注
    inquiry = await crud.create_inquiry_from_cart(
        db, 
        user_id=current_user.id, 
        user_remark=inquiry_in.user_remark
    )
    
    if not inquiry:
        raise HTTPException(status_code=400, detail="购物车为空或创建失败")
        
    return inquiry

@app.patch("/api/v1/admin/inquiries/{inquiry_id}/quote")
async def quote_inquiry(
    inquiry_id: int,
    quote_data: schemas.OrderPriceUpdate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    res = await db.execute(select(models.Inquiry).filter(models.Inquiry.id == inquiry_id))
    inquiry = res.scalars().first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
        
    inquiry.total_quoted_price = quote_data.new_price
    inquiry.status = models.InquiryStatus.QUOTED
    await db.commit()
    return inquiry

# ============================
# 询价系统 API (Inquiries)
# ============================

@app.post("/api/v1/inquiries/", response_model=schemas.InquiryResponse)
async def create_inquiry(
    inquiry_in: schemas.InquiryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """用户提交询价单 (将购物车内容转为询价单)"""
    inquiry = await crud.create_inquiry_from_cart(db, current_user.id, inquiry_in.user_remark)
    if not inquiry:
        raise HTTPException(status_code=400, detail="购物车为空，无法提交询价")
    return inquiry

@app.get("/api/v1/inquiries/", response_model=List[schemas.InquiryResponse])
async def read_inquiries(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """获取询价单列表 (管理员看所有，用户看自己)"""
    user_id = current_user.id if current_user.role != "admin" else None
    return await crud.get_inquiries(db, skip, limit, user_id=user_id, status=status)

@app.get("/api/v1/inquiries/{inquiry_id}", response_model=schemas.InquiryResponse)
async def read_inquiry(
    inquiry_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    inquiry = await crud.get_inquiry_by_id(db, inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail="询价单不存在")
    # 权限检查
    if current_user.role != "admin" and inquiry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看")
    return inquiry

@app.patch("/api/v1/inquiries/{inquiry_id}/quote", response_model=schemas.InquiryResponse)
async def quote_inquiry(
    inquiry_id: int,
    quote_data: schemas.InquiryQuoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_superuser)
):
    """管理员进行报价"""
    inquiry = await crud.quote_inquiry(db, inquiry_id, quote_data)
    if not inquiry:
        raise HTTPException(status_code=404, detail="询价单不存在")
    return inquiry

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
