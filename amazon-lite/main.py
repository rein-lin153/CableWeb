from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from tasks import update_copper_price_task # 导入刚才写的任务
import models, schemas, crud
from database import SessionLocal, engine
from config import settings # <--- 导入配置
import shutil # [新增] 用于保存文件
import os     # [新增] 用于路径操作
from fastapi import File, UploadFile # [新增]
from fastapi.staticfiles import StaticFiles # [新增]
from typing import List, Optional # 确保导入 Optional


# 修改 startup_event / lifespan 里的产品初始化逻辑
@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    scheduler.add_job(update_copper_price_task, 'interval', hours=1)
    scheduler.start()
    
    db = SessionLocal()
    try:
        # 1. Admin
        if not crud.get_user_by_email(db, settings.FIRST_SUPERUSER):
            print(f"Creating Admin: {settings.FIRST_SUPERUSER}")
            # 注意：这里我们手动创建一个 Admin，role="admin"
            user = models.User(
                email=settings.FIRST_SUPERUSER,
                hashed_password=crud.get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                company_name="HQ",
                is_admin=True,
                role="admin" # 设置角色
            )
            db.add(user)
            db.commit()

        # 2. Driver (测试用)
        driver_email = "driver@amazoncable.com"
        if not crud.get_user_by_email(db, driver_email):
            print(f"Creating Driver: {driver_email}")
            user = models.User(
                email=driver_email,
                hashed_password=crud.get_password_hash("driver123"),
                company_name="Logistics Team",
                is_admin=False,
                role="driver" # 设置角色
            )
            db.add(user)
            db.commit()

        # ... (Category 和 Product 初始化保持不变) ...
    finally:
        db.close()
    yield
    scheduler.shutdown()
    print("Scheduler shut down.")

# --- 初始化 App ---
app = FastAPI(
    title="Amazon Cable API", 
    version="1.0.0", 
    lifespan=lifespan # 注入 lifespan
)


# --- 配置 ---
SECRET_KEY = "YOUR_SUPER_SECRET_KEY_HERE" # 生产环境请使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

scheduler = BackgroundScheduler()

# =========================================================
# 1. 核心修复：定义绝对路径变量
# =========================================================

# 3. 设置路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")






# --- CORS 配置 ---
origins = [
    "http://localhost:5173", # Vite 默认端口
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    # 允许的来源列表。
    # 生产环境应该填具体的 ["http://localhost:5173", "http://192.168.1.76:5173"]
    # 开发环境为了方便手机调试，直接用 ["*"] 允许所有 IP
    allow_origins=["*"], 
    
    allow_credentials=True,
    allow_methods=["*"], # 允许所有方法 (GET, POST, PUT, DELETE...)
    allow_headers=["*"], # 允许所有 Header
)

# --- 依赖项 (Dependencies) ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# 修改 create_access_token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # 使用 settings
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # 使用 settings
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. 检查黑名单 (Logout check)
    if crud.is_token_revoked(db, token):
        raise HTTPException(
            status_code=401, 
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 验证 Token 签名
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 3. 查找用户
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception

    # ★★★ [关键修复] 检查用户是否被封禁 ★★★
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user
# ★★★ [新增] 超级管理员权限验证 ★★★
async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    RBAC 核心逻辑：
    1. 必须先通过 get_current_user 拿到有效用户。
    2. 检查 is_admin 是否为 True。
    3. 如果不是，直接拦截并返回 403。
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, 
            detail="The user doesn't have enough privileges (Admin required)"
        )
    return current_user

# 核心：管理员权限依赖
async def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限 (Admin privileges required)"
        )
    return current_user

# --- API 路由 (Routes) ---


# 1. Auth Login
@app.post("/api/v1/auth/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. 验证账号密码
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ★★★ [关键修复] 禁止封禁用户获取 Token ★★★
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # 2. 生成 Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # 3. 返回结果
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "user": user 
    }

# [新增] 登出接口
@app.post("/api/v1/auth/logout", status_code=200)
def logout(
    token: str = Depends(oauth2_scheme), # 获取原始 Token 字符串
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # 确保用户当前是登录状态
):
    """
    用户登出：
    将当前的 Access Token 加入黑名单，使其立即失效。
    """
    crud.revoke_token(db, token)
    return {"message": "Successfully logged out"}

# --- Category Routes (新增) ---
@app.get("/api/v1/categories/", response_model=List[schemas.CategoryResponse])
def read_categories(
    skip: int = 0, 
    limit: int = 100, 
    flat: bool = True, # [新增] 参数控制返回结构
    db: Session = Depends(get_db)
):
    """
    获取分类列表。
    - flat=true (默认): 返回平铺列表。
    - flat=false: 返回树形嵌套结构 (children)。
    """
    return crud.get_categories(db, skip=skip, limit=limit, flat=flat)

@app.post("/api/v1/categories/", response_model=schemas.CategoryResponse)
def create_category(
    cat: schemas.CategoryCreate, 
    db: Session = Depends(get_db), 
    _: models.User = Depends(get_current_active_superuser)
):
    # 如果指定了 parent_id，最好检查一下 parent 是否存在
    if cat.parent_id:
        parent = db.query(models.Category).filter(models.Category.id == cat.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")
            
    return crud.create_category(db, cat)

@app.delete("/api/v1/categories/{cat_id}", status_code=204)
def delete_category(
    cat_id: int, 
    db: Session = Depends(get_db), 
    _: models.User = Depends(get_current_active_superuser)
):
    if not crud.delete_category(db, cat_id):
        raise HTTPException(status_code=404, detail="Category not found")
    

# [新增] 更新分类接口
@app.put("/api/v1/categories/{cat_id}", response_model=schemas.CategoryResponse)
def update_category(
    cat_id: int,
    cat_update: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser) # 仅限管理员
):
    """
    修改分类信息 (名称、描述、父级)。
    修改名称不会影响该分类下的商品 (因为商品关联的是ID)。
    """
    # 1. 如果修改了 parent_id，检查新父亲是否存在
    if cat_update.parent_id:
        parent = db.query(models.Category).filter(models.Category.id == cat_update.parent_id).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")
            
    # 2. 执行更新
    db_cat = crud.update_category(db, cat_id, cat_update)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
        
    return db_cat

# 2. Auth Register
@app.post("/api/v1/auth/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# 3. Users Me
# 获取当前用户信息 (供前端校验 Session)
@app.get("/api/v1/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# 4. Users List (Admin Only)
# [升级] 获取用户列表 -> 必须是管理员
@app.get("/api/v1/users/", response_model=List[schemas.UserResponse])
def read_users(
    skip: int = 0, limit: int = 100, 
    db: Session = Depends(get_db), 
    _: models.User = Depends(get_current_active_superuser) # ★ 权限锁
):
    return crud.get_users(db, skip=skip, limit=limit)

# [Admin Only] 修改用户权限 (关键新增功能)
# [修复] 修改用户权限接口
@app.patch("/api/v1/users/{user_id}/role", response_model=schemas.UserResponse)
def update_user_role(
    user_id: int, 
    role_update: schemas.UserRoleUpdate,  # 使用刚才定义的 Schema
    db: Session = Depends(get_db), 
    current_admin: models.User = Depends(get_current_active_superuser) # 只有现有管理员可操作
):
    """
    修改用户权限 (Admin Only)
    前端发送: { "is_superuser": true/false }
    """
    
    # 1. 查找目标用户
    user_to_edit = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_edit:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. [安全保护] 防止管理员取消自己的权限
    # 如果目标是自己，且试图将 is_superuser 设为 False，则报错
    if user_id == current_admin.id and role_update.is_superuser is False:
        raise HTTPException(
            status_code=400, 
            detail="Operation not allowed: You cannot remove your own admin privileges."
        )
    
    # 3. 执行更新 (映射字段: is_superuser -> is_admin)
    user_to_edit.is_admin = role_update.is_superuser
    db.commit()
    db.refresh(user_to_edit)
    
    return user_to_edit

# [新增] 封禁用户 -> 必须是管理员
@app.patch("/api/v1/users/{user_id}/status", response_model=schemas.UserResponse)
def update_user_status(
    user_id: int,
    status_data: schemas.UserStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_active_superuser) # ★ 权限锁
):
    # 自我保护：防止管理员封禁自己
    if user_id == current_admin.id and status_data.is_active is False:
        raise HTTPException(status_code=400, detail="Cannot ban yourself")

    user = crud.update_user_status(db, user_id, status_data.is_active)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user

# [新增] 删除用户 -> 必须是管理员
@app.delete("/api/v1/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_active_superuser) # ★ 权限锁
):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    if not crud.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")

# ============================
# 产品管理接口 (Product Management)
# ============================

# 1. 获取列表 (公开)
@app.get("/api/v1/products/", response_model=List[schemas.ProductResponse])
def read_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    q: Optional[str] = None, # [新增] 接收前端传来的 ?q=xxx
    db: Session = Depends(get_db)
):
    # 将 q 传给 crud 的 search 参数
    products = crud.get_products(
        db, 
        skip=skip, 
        limit=limit, 
        category_id=category_id, 
        search=q 
    )
    return products

# 2. 获取详情 (公开)
@app.get("/api/v1/products/{product_id}", response_model=schemas.ProductResponse)
def read_product_detail(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# 3. 创建产品 (Admin)
@app.post("/api/v1/products/", response_model=schemas.ProductResponse, status_code=201)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db), 
    _: models.User = Depends(get_current_active_superuser)
):
    # 这里的 product 参数已经包含了 variants 列表
    return crud.create_product(db=db, product=product)

# 4. 更新产品 (Admin)
@app.put("/api/v1/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int, 
    product_update: schemas.ProductUpdate, 
    db: Session = Depends(get_db), 
    _: models.User = Depends(get_current_active_superuser)
):
    """
    更新产品信息。
    如果 body 中包含 variants 数组，将执行全量替换（删除旧规格，写入新规格）。
    """
    db_prod = crud.update_product(db, product_id, product_update)
    if not db_prod: 
        raise HTTPException(status_code=404, detail="Product not found")
    return db_prod

# 5. 删除产品 (Admin)
@app.delete("/api/v1/products/{product_id}", status_code=204)
def delete_product(
    product_id: int, 
    db: Session = Depends(get_db), 
    _: models.User = Depends(get_current_active_superuser)
):
    if not crud.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")


# 修改接口定义
@app.get("/api/v1/meta/prices", response_model=schemas.CopperDisplayResponse)
def get_metal_prices(db: Session = Depends(get_db)):
    # 1. 取最新的一条记录
    latest = db.query(models.CopperPrice).order_by(models.CopperPrice.updated_at.desc()).first()
    
    # 2. 如果没数据，返回默认空结构
    if not latest:
        return {
            "CNY": {"source": "无数据", "symbol": "¥", "price": 0.0, "change": 0.0},
            "USD": {"source": "无数据", "symbol": "$", "price": 0.0, "change": 0.0},
            "exchange_rate": 0.0,
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    # 3. 组装成你要求的 JSON 格式
    return {
        "CNY": {
            "source": "沪铜主连",
            "symbol": "¥",
            "price": latest.cny_price,
            "change": 0.0 # 数据库目前没存涨跌幅，暂时给0，或者你也在model里加一列
        },
        "USD": {
            "source": "沪铜主连(折算)",
            "symbol": "$",
            "price": latest.usd_price,
            "change": 0.0
        },
        "exchange_rate": latest.exchange_rate,
        # 格式化时间字符串
        "updated": latest.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    }


# [Public] 获取新闻列表
@app.get("/api/v1/news/", response_model=List[schemas.NewsResponse])
def read_news_list(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """
    获取新闻列表 (默认按时间倒序)
    - Public 接口，无需登录
    """
    return crud.get_news_list(db, skip=skip, limit=limit)

# [Public] 获取新闻详情
@app.get("/api/v1/news/{news_id}", response_model=schemas.NewsResponse)
def read_news_detail(
    news_id: int, 
    db: Session = Depends(get_db)
):
    """
    获取单条新闻详情
    """
    news = crud.get_news_by_id(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news

# [Admin Only] 发布新闻
@app.post("/api/v1/news/", response_model=schemas.NewsResponse, status_code=201)
def create_news(
    news: schemas.NewsCreate, 
    db: Session = Depends(get_db), 
    _: models.User = Depends(get_current_active_superuser) # ★ 只有超级管理员可发布
):
    return crud.create_news(db, news)

# [Admin Only] 删除新闻
@app.delete("/api/v1/news/{news_id}", status_code=204)
def delete_news(
    news_id: int, 
    db: Session = Depends(get_db), 
    _: models.User = Depends(get_current_active_superuser) # ★ 只有超级管理员可删除
):
    success = crud.delete_news(db, news_id)
    if not success:
        raise HTTPException(status_code=404, detail="News not found")

# ==========================================
# 购物车接口 (修复 SKU 逻辑)
# ==========================================

@app.get("/api/v1/cart/", response_model=List[schemas.CartItemResponse])
def read_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # crud.get_cart_items 已经预加载了 variant 和 variant.product
    items = crud.get_cart_items(db, current_user.id)
    
    res = []
    for item in items:
        # [修复] 逻辑变更：
        # 1. 不再读取 item.product_id (字段已删除)
        # 2. 改为读取 item.variant_id
        # 3. 产品信息需要通过 item.variant.product 来获取
        
        # 安全检查：防止脏数据（比如变体被删了但购物车没清）
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
            
            # ★★★ [新增] 从变体获取单位 ★★★
            "unit": item.variant.unit, 
            
            "image_url": item.variant.product.image_url,
            "subtotal": item.variant.price * item.quantity
        })
    return res

@app.post("/api/v1/cart/", response_model=schemas.CartItemResponse)
def add_to_cart(
    cart_data: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    item = crud.add_to_cart(db, current_user.id, cart_data.variant_id, cart_data.quantity)
    if not item:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    return {
        "id": item.id,
        "variant_id": item.variant_id,
        "quantity": item.quantity,
        "product_name": item.variant.product.name,
        "spec": item.variant.spec,
        "color": item.variant.color,
        "price": item.variant.price,
        
        # ★★★ [新增] 从变体获取单位 ★★★
        "unit": item.variant.unit,
        
        "image_url": item.variant.product.image_url,
        "subtotal": item.variant.price * item.quantity
    }

@app.delete("/api/v1/cart/{item_id}")
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    success = crud.remove_from_cart(db, current_user.id, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Deleted"}

# ==========================================
# 7. 订单接口 (Order Routes)
# ==========================================

# 用户下单
@app.post("/api/v1/orders/", response_model=schemas.OrderResponse, status_code=201)
def create_order(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 传入用户当前的 discount_rate
    order = crud.create_order_from_cart(db, current_user.id, current_user.discount_rate)
    if not order:
        raise HTTPException(status_code=400, detail="Cart is empty")
    return order

# 用户查看自己的订单
@app.get("/api/v1/orders/my", response_model=List[schemas.OrderResponse])
def read_my_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_orders(db, user_id=current_user.id)

# [Admin] 查看所有订单
@app.get("/api/v1/orders/", response_model=List[schemas.OrderResponse])
def read_all_orders(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    return crud.get_orders(db)

# 1. 确认订单 (Confirm)
@app.patch("/api/v1/orders/{order_id}/confirm", response_model=schemas.OrderResponse)
def confirm_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    order, error = crud.confirm_order(db, order_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return order

@app.get("/api/v1/orders/", response_model=List[schemas.OrderResponse])
def read_orders(
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = None, # [新增] 接收搜索词
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 权限判断逻辑 (保持不变)
    user_id = None
    driver_id = None
    
    if current_user.role == "admin" or current_user.is_admin:
        # 管理员看所有 (user_id=None)，但如果有搜索词，会在所有订单里搜
        pass 
    elif current_user.role == "driver":
        driver_id = current_user.id
    else:
        # 普通用户只能搜自己的
        user_id = current_user.id

    orders = crud.get_orders(
        db, 
        skip=skip, 
        limit=limit, 
        user_id=user_id, 
        driver_id=driver_id,
        search=q # [新增] 传入搜索词
    )
    return orders


# 2. 发货 (Ship)
@app.patch("/api/v1/orders/{order_id}/ship", response_model=schemas.OrderResponse)
def ship_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    order, error = crud.ship_order(db, order_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return order

# 3. 完成 (Complete)
@app.post("/api/v1/orders/{order_id}/complete", response_model=schemas.OrderResponse)
def complete_order(
    order_id: int,
    file: UploadFile = File(None), # [关键] 接收可选的文件
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    完成订单 (拍照签收)。
    - 仅限 Driver 或 Admin 操作。
    - 必须是 delivering 状态。
    - 支持上传一张图片。
    """
    
    # 1. 获取订单
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 2. 权限校验
    if current_user.role == "driver":
        # 如果是司机，必须是该订单的指派司机
        if order.driver_id != current_user.id:
             raise HTTPException(status_code=403, detail="Not assigned to this order")
    elif current_user.role == "admin" or current_user.is_admin:
        pass # 管理员通行
    else:
        raise HTTPException(status_code=403, detail="Permission denied")

    # 3. 状态校验
    if order.status != models.OrderStatus.DELIVERING:
        raise HTTPException(status_code=400, detail="Order must be in delivering status")

    # 4. [新增] 处理图片上传
    if file:
        try:
            # 这里的 upload_dir 也要改成绝对路径，或者和上面保持一致
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            upload_dir = os.path.join(BASE_DIR, "static/uploads")
            
            # 确保目录存在
            os.makedirs(upload_dir, exist_ok=True)
            
            file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
            file_name = f"order_{order_id}_sign.{file_ext}"
            file_path = os.path.join(upload_dir, file_name)
            
            print(f"正在保存图片到: {file_path}") # <--- 加个打印
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            order.delivery_photo_url = f"/static/uploads/{file_name}"
            print("✅ 图片保存成功")
            
        except Exception as e:
            # ★★★ 把 pass 改成打印错误，甚至抛出异常 ★★★
            print(f"❌ 图片上传失败: {e}")
            raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    # 5. 更新状态
    order.status = models.OrderStatus.COMPLETED
    db.commit()
    db.refresh(order)
    
    return order
# 4. 作废 (Cancel)
@app.patch("/api/v1/orders/{order_id}/cancel", response_model=schemas.OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    order, error = crud.cancel_order(db, order_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return order

# [Admin] 订单改价
@app.patch("/api/v1/orders/{order_id}/price", response_model=schemas.OrderResponse)
def update_order_price(
    order_id: int,
    price_data: schemas.OrderPriceUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    order = crud.update_order_price(db, order_id, price_data.new_price)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    return order

# ==========================================
# 8. 用户折扣接口 (Admin User)
# ==========================================
@app.patch("/api/v1/users/{user_id}/discount", response_model=schemas.UserResponse)
def update_user_discount(
    user_id: int,
    discount_data: schemas.UserDiscountUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    """
    设置用户折扣率，例如 0.05 代表 95折
    """
    user = crud.update_user_discount(db, user_id, discount_data.discount_rate)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user

# [新增/修改] 修改订单中某商品的单价 (Admin Only)
# 原来的修改总价接口建议废弃或删除
@app.patch("/api/v1/orders/{order_id}/items/{item_id}", response_model=schemas.OrderResponse)
def update_order_item_price(
    order_id: int,
    item_id: int,
    price_data: schemas.OrderItemPriceUpdate, # 使用新定义的 Schema
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser) # 必须是管理员
):
    """
    管理员修改订单明细单价。
    后端会自动重算该 Item 的小计，并重算整个 Order 的最终总价。
    """
    updated_order = crud.update_order_item_price(
        db, 
        order_id=order_id, 
        item_id=item_id, 
        new_unit_price=price_data.new_unit_price
    )
    
    if not updated_order:
        raise HTTPException(
            status_code=404, 
            detail="Order Item not found or does not belong to this order"
        )
        
    return updated_order

# [新增] 修改新闻 (Admin Only)
@app.put("/api/v1/news/{news_id}", response_model=schemas.NewsResponse)
def update_news(
    news_id: int,
    news_update: schemas.NewsUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser) # ★ 权限控制
):
    news = crud.update_news(db, news_id, news_update)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news

# 1. 获取司机列表 (Admin Only)
@app.get("/api/v1/users/drivers", response_model=List[schemas.UserResponse])
def get_drivers(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    return crud.get_drivers(db)

# 2. 订单指派司机 (Admin Only)
@app.patch("/api/v1/orders/{order_id}/assign", response_model=schemas.OrderResponse)
def assign_order_driver(
    order_id: int,
    assign_req: schemas.AssignDriverRequest,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    order, error = crud.assign_driver(db, order_id, assign_req.driver_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return order

# 3. 更新实时位置 (Driver Only)
@app.post("/api/v1/orders/{order_id}/location", response_model=schemas.OrderResponse)
def update_order_location(
    order_id: int,
    loc: schemas.DriverLocationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 权限检查：必须是司机，且必须是该订单的负责人
    if current_user.role != "driver":
        raise HTTPException(status_code=403, detail="Not a driver")
    
    # 也可以加一步检查: order.driver_id == current_user.id
    
    order = crud.update_driver_location(db, order_id, loc.lat, loc.lng)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# 4. 司机获取任务列表 (Driver Only)
@app.get("/api/v1/orders/driver/tasks", response_model=List[schemas.OrderResponse])
def get_my_driver_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "driver":
        raise HTTPException(status_code=403, detail="Not a driver")
    return crud.get_driver_tasks(db, current_user.id)


@app.get("/api/v1/orders/{order_id}", response_model=schemas.OrderResponse)
def read_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # ★ 允许所有登录用户进入，内部再判断权限
):
    """
    获取订单详情。
    权限规则：
    1. 管理员: 可查看所有订单。
    2. 买家: 只能查看自己的订单。
    3. 司机: 只能查看指派给自己的订单。
    """
    # 1. 查询订单
    order = crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # 2. ★★★ 核心权限校验逻辑 ★★★
    
    # A. 检查是否为管理员
    is_admin = current_user.is_admin or current_user.role == "admin"
    
    # B. 检查是否为该订单的买家
    is_owner = order.user_id == current_user.id
    
    # C. 检查是否为该订单的司机
    is_assigned_driver = order.driver_id == current_user.id

    # 如果以上三个身份都不符合，拒绝访问
    if not (is_admin or is_owner or is_assigned_driver):
        raise HTTPException(
            status_code=403, 
            detail="You do not have permission to view this order."
        )

    # 3. 返回数据 (Schema 会自动提取 driver_lat, driver_lng, status)
    return order


# ============================
# 用户管理接口 (User Management)
# ============================

# [新增] 管理员创建用户 (POST /api/v1/users/)
@app.post("/api/v1/users/", response_model=schemas.UserResponse, status_code=201)
def create_user_by_admin(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser) # ★ 仅限管理员
):
    # 1. 检查邮箱是否已存在
    user = crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # 2. 创建用户 (密码会在 crud 里被加密)
    user = crud.create_user(db, user_in)
    return user

# [新增] 管理员修改用户信息 (PUT /api/v1/users/{id})
@app.put("/api/v1/users/{user_id}", response_model=schemas.UserResponse)
def update_user_detail(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_active_superuser) # ★ 仅限管理员
):
    # 自我保护：防止管理员把自己降级成普通用户而失去管理权
    if user_id == current_admin.id and user_in.role and user_in.role != "admin":
         raise HTTPException(status_code=400, detail="Cannot change your own role to non-admin")

    user = crud.update_user(db, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ==========================================
# 新增：技术参数接口 (Technical Specs)
# ==========================================

# 1. 获取列表 (公开)
@app.get("/api/v1/specs/", response_model=List[schemas.TechnicalSpecResponse], tags=["Specs"])
def read_specs(
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_technical_specs(db, skip=skip, limit=limit, category=category, search=search)

# 2. 创建 (管理员)
@app.post("/api/v1/specs/", response_model=schemas.TechnicalSpecResponse, status_code=201, tags=["Specs"])
def create_spec(
    spec: schemas.TechnicalSpecCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    return crud.create_technical_spec(db, spec)

# 3. 更新 (管理员)
@app.put("/api/v1/specs/{spec_id}", response_model=schemas.TechnicalSpecResponse, tags=["Specs"])
def update_spec(
    spec_id: int,
    spec_update: schemas.TechnicalSpecUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    spec = crud.update_technical_spec(db, spec_id, spec_update)
    if not spec:
        raise HTTPException(status_code=404, detail="Spec not found")
    return spec

# 4. 删除 (管理员)
@app.delete("/api/v1/specs/{spec_id}", status_code=204, tags=["Specs"])
def delete_spec(
    spec_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    if not crud.delete_technical_spec(db, spec_id):
        raise HTTPException(status_code=404, detail="Spec not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
    