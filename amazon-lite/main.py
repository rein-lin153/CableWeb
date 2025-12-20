import os
import shutil
import enum
import time
import requests
import magic  # pip install python-magic (Windows需安装 python-magic-bin)
import uvicorn
import bcrypt
from datetime import datetime, timedelta
from typing import List, Optional, Any
from contextlib import asynccontextmanager

# FastAPI & Pydantic
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# SQLAlchemy & AsyncIO
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, backref, selectinload, joinedload
from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, JSON, select, or_, cast, desc, delete
from sqlalchemy.exc import IntegrityError

# JWT
from jose import JWTError, jwt

# Scheduler
from apscheduler.schedulers.background import BackgroundScheduler

# ==========================================
# 1. 配置 (Config)
# ==========================================
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

    # API 配置
    SINA_API_URL: str = "http://hq.sinajs.cn/list=nf_CU0"
    EXCHANGE_RATE_API: str = "https://api.exchangerate-api.com/v4/latest/USD"

    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

# 全局路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# ==========================================
# 2. 数据库 (Database)
# ==========================================
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

# ==========================================
# 3. 模型定义 (Models)
# ==========================================

# 枚举
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    DRIVER = "driver"

class OrderStatus(str, enum.Enum):
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class InquiryStatus(str, enum.Enum):
    PENDING = "pending"
    QUOTED = "quoted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CLOSED = "closed"

# 表结构
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, index=True, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String, default=UserRole.USER)
    company_name = Column(String, nullable=True)
    discount_rate = Column(Float, default=0.0)

    cart_items = relationship("CartItem", back_populates="user")
    orders = relationship("Order", foreign_keys="[Order.user_id]", back_populates="user")
    assigned_orders = relationship("Order", foreign_keys="[Order.driver_id]", back_populates="driver")
    inquiries = relationship("Inquiry", back_populates="user")

class TokenBlocklist(Base):
    __tablename__ = "token_blocklist"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    products = relationship("Product", back_populates="category")
    children = relationship("Category", backref=backref("parent", remote_side=[id]))

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    is_active = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    cost_id = Column(Integer, ForeignKey("product_costs.id"), nullable=True) # 关联成本

    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    cost_source = relationship("ProductCost")

class ProductVariant(Base):
    __tablename__ = "product_variants"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    spec = Column(String)
    color = Column(String)
    price = Column(Float)
    stock = Column(Integer, default=0)
    unit = Column(String, default="米")
    sku_code = Column(String, nullable=True)
    copper_weight = Column(Float, default=0.0)
    process_cost = Column(Float, default=0.0)

    product = relationship("Product", back_populates="variants")
    cart_items = relationship("CartItem", back_populates="variant")

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    variant_id = Column(Integer, ForeignKey("product_variants.id"))
    quantity = Column(Integer, default=1)
    user = relationship("User", back_populates="cart_items")
    variant = relationship("ProductVariant", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    driver_lat = Column(Float, nullable=True)
    driver_lng = Column(Float, nullable=True)
    delivery_photo_url = Column(String, nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING_CONFIRMATION)
    original_total_price = Column(Float, default=0.0)
    final_total_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], back_populates="orders")
    driver = relationship("User", foreign_keys=[driver_id], back_populates="assigned_orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, nullable=True)
    product_name = Column(String)
    product_spec = Column(String)
    product_color = Column(String)
    product_image = Column(String, nullable=True)
    product_unit = Column(String)
    unit_price = Column(Float)
    quantity = Column(Integer)
    subtotal = Column(Float)
    order = relationship("Order", back_populates="items")

class Inquiry(Base):
    __tablename__ = "inquiries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(InquiryStatus), default=InquiryStatus.PENDING)
    quoted_total_price = Column(Float, nullable=True)
    user_remark = Column(String, nullable=True)
    admin_reply = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="inquiries")
    items = relationship("InquiryItem", back_populates="inquiry", cascade="all, delete-orphan")

class InquiryItem(Base):
    __tablename__ = "inquiry_items"
    id = Column(Integer, primary_key=True, index=True)
    inquiry_id = Column(Integer, ForeignKey("inquiries.id"))
    variant_id = Column(Integer, ForeignKey("product_variants.id"))
    product_name = Column(String)
    product_spec = Column(String)
    product_color = Column(String)
    quantity = Column(Integer)
    quoted_unit_price = Column(Float, nullable=True)
    inquiry = relationship("Inquiry", back_populates="items")
    variant = relationship("ProductVariant")

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    summary = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_published = Column(Boolean, default=True)

class CopperPrice(Base):
    __tablename__ = "copper_prices"
    id = Column(Integer, primary_key=True, index=True)
    cny_price = Column(Float, nullable=False)
    usd_price = Column(Float, nullable=False)
    exchange_rate = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

class TechnicalSpec(Base):
    __tablename__ = "technical_specs"
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, index=True)
    category = Column(String, index=True)
    standard_param = Column(String)
    actual_param = Column(String)
    feature = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProductCost(Base):
    __tablename__ = "product_costs"
    id = Column(Integer, primary_key=True, index=True)
    reference_price = Column(Float, default=0.0)
    spec_name = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=True)
    remark = Column(String, nullable=True)
    material = Column(String, default="Cu", nullable=False)
    core_structure = Column(JSON, nullable=False)
    total_weight = Column(Float, nullable=False)
    length = Column(Float, default=100.0)
    insulation_type = Column(String, default="PVC")
    copper_price = Column(Float, nullable=False)
    pvc_price = Column(Float, nullable=False)
    labor_cost = Column(Float, default=0.0)
    copper_weight = Column(Float)
    copper_amount = Column(Float)
    pvc_weight = Column(Float)
    pvc_amount = Column(Float)
    total_cost = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ==========================================
# 4. Schemas (Pydantic)
# ==========================================

# Enums (re-use)
OrderStatusEnum = OrderStatus
InquiryStatusEnum = InquiryStatus

# Category
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    children: List['CategoryResponse'] = []
    class Config:
        from_attributes = True

# Product
class ProductVariantBase(BaseModel):
    spec: str
    color: str
    price: float
    stock: int
    unit: str = "米"
    sku_code: Optional[str] = None
    copper_weight: Optional[float] = 0.0
    process_cost: Optional[float] = 0.0

class ProductVariantCreate(ProductVariantBase):
    pass

class ProductVariantResponse(ProductVariantBase):
    id: int
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    has_variants: bool = True
    unit: str = "卷"

class ProductCreate(ProductBase):
    variants: List[ProductVariantCreate] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    has_variants: Optional[bool] = None
    variants: Optional[List[ProductVariantCreate]] = None
    unit: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    category_detail: Optional['CategoryResponse'] = None
    variants: List[ProductVariantResponse] = []
    class Config:
        from_attributes = True

# User
class UserBase(BaseModel):
    email: str
    company_name: Optional[str] = None
    username: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "user"

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    company_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    discount_rate: Optional[float] = None

class UserRoleUpdate(BaseModel):
    is_superuser: bool

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserDiscountUpdate(BaseModel):
    discount_rate: float

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    discount_rate: float
    role: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

# Cart
class CartItemCreate(BaseModel):
    variant_id: int
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    variant_id: int
    quantity: int
    product_name: str
    spec: str
    color: str
    price: float
    unit: str
    image_url: Optional[str] = None
    subtotal: float
    class Config:
        from_attributes = True

# Order
class OrderItemResponse(BaseModel):
    id: int
    product_name: str
    product_spec: Optional[str] = None
    product_color: Optional[str] = None
    product_image: Optional[str] = None
    unit_price: float
    quantity: int
    subtotal: float
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    user_email: Optional[str] = None
    driver_id: Optional[int] = None
    driver_email: Optional[str] = None
    driver_lat: Optional[float] = None
    driver_lng: Optional[float] = None
    delivery_photo_url: Optional[str] = None
    status: OrderStatusEnum
    original_total_price: float
    final_total_price: float
    created_at: datetime
    items: List[OrderItemResponse] = []
    class Config:
        from_attributes = True

class DriverLocationUpdate(BaseModel):
    lat: float
    lng: float

class AssignDriverRequest(BaseModel):
    driver_id: int

class OrderPriceUpdate(BaseModel):
    new_price: float

class OrderItemPriceUpdate(BaseModel):
    new_unit_price: float

# Inquiry
class InquiryItemCreate(BaseModel):
    variant_id: int
    quantity: int

class InquiryCreate(BaseModel):
    user_remark: Optional[str] = None
    items: Optional[List[InquiryItemCreate]] = None

class InquiryQuoteUpdate(BaseModel):
    quoted_total_price: float
    admin_reply: Optional[str] = None

class InquiryItemResponse(BaseModel):
    id: int
    product_name: str
    product_spec: str
    product_color: str
    quantity: int
    quoted_unit_price: Optional[float] = None
    class Config:
        from_attributes = True

class InquiryResponse(BaseModel):
    id: int
    user_id: int
    user_email: Optional[str] = None
    status: InquiryStatusEnum
    quoted_total_price: Optional[float] = None
    user_remark: Optional[str] = None
    admin_reply: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[InquiryItemResponse] = []
    class Config:
        from_attributes = True

# News & Specs
class NewsBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: str
    image_url: Optional[str] = None
    is_published: bool = True

class NewsCreate(NewsBase):
    pass

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    is_published: Optional[bool] = None

class NewsResponse(NewsBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class TechnicalSpecBase(BaseModel):
    model: str
    category: str
    standard_param: Optional[str] = None
    actual_param: Optional[str] = None
    feature: Optional[str] = None

class TechnicalSpecCreate(TechnicalSpecBase):
    pass

class TechnicalSpecUpdate(BaseModel):
    model: Optional[str] = None
    category: Optional[str] = None
    standard_param: Optional[str] = None
    actual_param: Optional[str] = None
    feature: Optional[str] = None

class TechnicalSpecResponse(TechnicalSpecBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Costs & Pricing
class CoreGroup(BaseModel):
    cores: int
    strands: int
    gauge: float

class CostBase(BaseModel):
    spec_name: str
    category: Optional[str] = None
    remark: Optional[str] = None
    material: str = "Cu"
    insulation_type: str = "PVC"
    core_structure: List[CoreGroup]
    total_weight: float
    length: float = 100.0
    copper_price: float
    pvc_price: float
    labor_cost: float

class CostCreate(CostBase):
    pass

class CostUpdate(CostBase):
    pass

class CostResponse(CostBase):
    id: int
    copper_weight: float
    copper_amount: float
    pvc_weight: float
    pvc_amount: float
    total_cost: float
    updated_at: datetime
    reference_price: float
    class Config:
        from_attributes = True

class CategoryTree(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    children: List['CategoryTree'] = []
    class Config:
        from_attributes = True

class ConvertCostToProduct(BaseModel):
    cost_id: int
    target_category_id: int
    name: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None

# Meta & Copper Display (🟢 新增补充)
class PriceDetail(BaseModel):
    source: str
    symbol: str
    price: float
    change: float

class CopperDisplayResponse(BaseModel):
    CNY: PriceDetail
    USD: PriceDetail
    exchange_rate: float
    updated: str
    class Config:
        from_attributes = True

# 解决递归引用
CategoryResponse.model_rebuild()

# ==========================================
# 5. 安全与依赖 (Security & Dependencies)
# ==========================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def is_token_revoked(db: AsyncSession, token: str) -> bool:
    result = await db.execute(select(TokenBlocklist).filter(TokenBlocklist.token == token))
    return result.scalars().first() is not None

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if await is_token_revoked(db, token):
        raise HTTPException(status_code=401, detail="Token has been revoked", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise credentials_exception
    except JWTError: raise credentials_exception
    
    user = await get_user_by_email(db, email=email)
    if user is None: raise credentials_exception
    if not user.is_active: raise HTTPException(status_code=400, detail="Inactive user")
    return user

async def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

async def validate_image_security(file: UploadFile):
    MAX_FILE_SIZE = 5 * 1024 * 1024
    ALLOWED_MIMES = ["image/jpeg", "image/png", "image/webp"]
    header = await file.read(2048)
    await file.seek(0)
    if not header: raise HTTPException(status_code=400, detail="Empty file")
    try:
        mime_type = magic.from_buffer(header, mime=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File analysis failed: {str(e)}")
    if mime_type not in ALLOWED_MIMES:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {mime_type}")
    await file.seek(0, 2)
    file_size = file.file.tell()
    await file.seek(0)
    if file_size > MAX_FILE_SIZE: raise HTTPException(status_code=400, detail="File too large")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# ==========================================
# 6. CRUD 逻辑集合
# ==========================================
async def get_cart_items(db: AsyncSession, user_id: int):
    query = select(CartItem).options(joinedload(CartItem.variant).joinedload(ProductVariant.product)).filter(CartItem.user_id == user_id)
    return (await db.execute(query)).scalars().all()

async def create_order_from_cart(db: AsyncSession, user_id: int, discount_rate: float):
    cart_items = await get_cart_items(db, user_id)
    if not cart_items: return None
    original_total = 0.0
    order_items_data = []
    for item in cart_items:
        variant = item.variant
        product = variant.product
        subtotal = variant.price * item.quantity
        original_total += subtotal
        order_items_data.append({
            "product_id": product.id, "product_name": product.name, "product_image": product.image_url,
            "product_spec": variant.spec, "product_color": variant.color, "product_unit": variant.unit,
            "unit_price": variant.price, "quantity": item.quantity, "subtotal": subtotal
        })
    final_total = round(original_total * (1 - discount_rate), 2)
    db_order = Order(user_id=user_id, status=OrderStatus.PENDING_CONFIRMATION, original_total_price=original_total, final_total_price=final_total)
    db.add(db_order)
    await db.flush()
    for item_data in order_items_data:
        db.add(OrderItem(order_id=db_order.id, **item_data))
    await db.execute(delete(CartItem).where(CartItem.user_id == user_id))
    await db.commit()
    await db.refresh(db_order)
    return await get_order_by_id(db, db_order.id)

async def get_order_by_id(db: AsyncSession, order_id: int):
    query = select(Order).options(joinedload(Order.items), joinedload(Order.user), joinedload(Order.driver)).filter(Order.id == order_id)
    return (await db.execute(query)).unique().scalars().first()

async def create_inquiry_from_cart(db: AsyncSession, user_id: int, user_remark: str = None):
    cart_items = await get_cart_items(db, user_id)
    if not cart_items: return None
    db_inquiry = Inquiry(user_id=user_id, status=InquiryStatus.PENDING, user_remark=user_remark)
    db.add(db_inquiry)
    await db.flush()
    for item in cart_items:
        db.add(InquiryItem(inquiry_id=db_inquiry.id, variant_id=item.variant.id, product_name=item.variant.product.name,
                           product_spec=item.variant.spec, product_color=item.variant.color, quantity=item.quantity))
    await db.execute(delete(CartItem).where(CartItem.user_id == user_id))
    await db.commit()
    return await get_inquiry_by_id(db, db_inquiry.id)

async def get_inquiry_by_id(db: AsyncSession, inquiry_id: int):
    query = select(Inquiry).options(joinedload(Inquiry.items), joinedload(Inquiry.user)).filter(Inquiry.id == inquiry_id)
    return (await db.execute(query)).unique().scalars().first()

# ==========================================
# 7. 定时任务 & 爬虫 (Tasks)
# ==========================================
def get_realtime_copper_prices():
    print("🕷️ 正在从新浪财经获取数据...", end=" ")
    sina_url = settings.SINA_API_URL
    headers = {"Referer": "https://finance.sina.com.cn/"}
    cny_price = 0.0
    try:
        resp = requests.get(sina_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data_str = resp.text.split('"')[1]
            data_list = data_str.split(',')
            if len(data_list) > 8: cny_price = float(data_list[8])
    except Exception as e:
        print(f"\n❌ 新浪接口报错: {e}")
        return None
    
    usd_to_cny_rate = 7.07
    try:
        rate_resp = requests.get(settings.EXCHANGE_RATE_API, timeout=5)
        if rate_resp.status_code == 200:
            usd_to_cny_rate = rate_resp.json().get("rates", {}).get("CNY", 7.07)
    except: pass
    
    usd_price = cny_price / usd_to_cny_rate if cny_price > 0 else 0.0
    print(f"✅ 获取成功: ¥{cny_price}")
    return {
        "CNY": {"source": "沪铜连续", "symbol": "¥", "price": round(cny_price, 2), "change": 0.0},
        "USD": {"source": f"折算 (1:{usd_to_cny_rate:.2f})", "symbol": "$", "price": round(usd_price, 2), "change": 0.0},
        "exchange_rate": round(usd_to_cny_rate, 4),
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

async def update_copper_price_task():
    print(f"[{datetime.now()}] ⏰ 定时任务启动...")
    data = get_realtime_copper_prices()
    if not data or data['CNY']['price'] <= 0: return
    async with AsyncSessionLocal() as db:
        try:
            record = CopperPrice(cny_price=data['CNY']['price'], usd_price=data['USD']['price'], exchange_rate=data['exchange_rate'], updated_at=datetime.now())
            db.add(record)
            await db.commit()
            print(f"💾 数据库已更新: ¥{record.cny_price}")
        except Exception as e:
            print(f"❌ 数据库写入失败: {e}")
            await db.rollback()

# ==========================================
# 8. FastAPI Application
# ==========================================
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Init DB Tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Init Admin
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).filter(User.email == settings.FIRST_SUPERUSER))
        if not res.scalars().first():
            admin = User(email=settings.FIRST_SUPERUSER, username="Admin", hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD), role="admin", is_admin=True, is_active=True, company_name="HQ")
            db.add(admin)
            await db.commit()
    # Start Scheduler
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
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
os.makedirs(os.path.join(STATIC_DIR, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ==========================================
# 9. Routers Implementation
# ==========================================

# --- Meta Router (🟢 新增补充: 解决 404 /api/v1/meta/prices) ---
meta_router = APIRouter(prefix="/api/v1/meta", tags=["Meta"])
@meta_router.get("/prices", response_model=CopperDisplayResponse)
async def get_meta_prices(db: AsyncSession = Depends(get_db)):
    """获取最新铜价 (前端 Header/Footer 显示用)"""
    res = await db.execute(select(CopperPrice).order_by(desc(CopperPrice.updated_at)).limit(1))
    latest = res.scalars().first()
    if not latest:
        # Fallback if db is empty
        return {
            "CNY": {"source": "System", "symbol": "¥", "price": 0.0, "change": 0.0},
            "USD": {"source": "System", "symbol": "$", "price": 0.0, "change": 0.0},
            "exchange_rate": 7.0,
            "updated": "No Data"
        }
    return {
        "CNY": {"source": "沪铜连续", "symbol": "¥", "price": latest.cny_price, "change": 0.0},
        "USD": {"source": "国际折算", "symbol": "$", "price": latest.usd_price, "change": 0.0},
        "exchange_rate": latest.exchange_rate,
        "updated": latest.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    }

# --- Auth Router ---
auth_router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active: raise HTTPException(status_code=400, detail="Inactive user")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@auth_router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db, user.email): raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(email=user.email, username=user.username, hashed_password=get_password_hash(user.password), company_name=user.company_name, role=user.role, is_admin=user.role=="admin")
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@auth_router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    db.add(TokenBlocklist(token=token))
    await db.commit()
    return {"message": "Successfully logged out"}

# --- Users Router ---
users_router = APIRouter(prefix="/api/v1/users", tags=["Users"])
@users_router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@users_router.get("/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    res = await db.execute(select(User).offset(skip).limit(limit))
    return res.scalars().all()

@users_router.get("/drivers", response_model=List[UserResponse])
async def get_drivers(db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    res = await db.execute(select(User).filter(User.role == "driver"))
    return res.scalars().all()

# --- Categories Router (🟢 新增补充: 解决 404 /api/v1/categories/) ---
categories_router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

@categories_router.get("/", response_model=List[CategoryResponse])
async def read_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """获取分类列表 (平铺结构)"""
    res = await db.execute(select(Category).options(selectinload(Category.children)).offset(skip).limit(limit))
    return res.scalars().all()

@categories_router.delete("/{id}")
async def delete_category(id: int, db: AsyncSession = Depends(get_db), _ = Depends(get_current_active_superuser)):
    """删除分类"""
    res = await db.execute(select(Category).filter(Category.id == id))
    cat = res.scalars().first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(cat)
    await db.commit()
    return {"ok": True}

# --- Products Router ---
products_router = APIRouter(prefix="/api/v1/products", tags=["Products"])
@products_router.get("/categories/tree", response_model=List[CategoryTree])
async def get_category_tree(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Category))
    all_cats = res.scalars().all()
    cat_map = {c.id: CategoryTree(id=c.id, name=c.name, parent_id=c.parent_id, children=[]) for c in all_cats}
    roots = []
    for cat in all_cats:
        node = cat_map[cat.id]
        if cat.parent_id is None: roots.append(node)
        else:
            if parent := cat_map.get(cat.parent_id): parent.children.append(node)
    return roots

@products_router.post("/categories/", response_model=CategoryResponse)
async def create_category(cat: CategoryCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    db_cat = Category(name=cat.name, parent_id=cat.parent_id)
    db.add(db_cat)
    await db.commit()
    return (await db.execute(select(Category).options(selectinload(Category.children)).filter(Category.id==db_cat.id))).scalars().first()

@products_router.post("/convert-from-cost", response_model=ProductResponse)
async def convert_cost_to_product(payload: ConvertCostToProduct, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    cost_res = await db.execute(select(ProductCost).filter(ProductCost.id == payload.cost_id))
    cost_item = cost_res.scalars().first()
    if not cost_item: raise HTTPException(status_code=404, detail="Cost record not found")
    new_product = Product(name=payload.name, description=payload.description, price=payload.price, category_id=payload.target_category_id, image_url=payload.image_url, cost_id=cost_item.id)
    db.add(new_product)
    await db.flush()
    new_variant = ProductVariant(product_id=new_product.id, spec=cost_item.spec_name, color="默认", price=payload.price, stock=9999, sku_code=f"AUTO-{cost_item.id}", copper_weight=cost_item.copper_weight, process_cost=(cost_item.labor_cost + cost_item.pvc_amount))
    db.add(new_variant)
    await db.commit()
    return (await db.execute(select(Product).options(selectinload(Product.variants)).filter(Product.id == new_product.id))).scalars().first()

@products_router.get("/", response_model=List[ProductResponse])
async def read_products(skip: int = 0, limit: int = 100, category_id: Optional[int] = None, search: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Product).options(selectinload(Product.variants))
    if category_id: query = query.filter(Product.category_id == category_id)
    if search: query = query.filter(Product.name.contains(search))
    return (await db.execute(query.offset(skip).limit(limit))).scalars().all()

@products_router.get("/{id}", response_model=ProductResponse)
async def read_product(id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Product).options(selectinload(Product.variants)).filter(Product.id == id))
    product = res.scalars().first()
    if not product: raise HTTPException(status_code=404, detail="Product not found")
    return product

@products_router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    db_product = Product(name=product.name, description=product.description, image_url=product.image_url, category_id=product.category_id, unit=product.unit)
    for v in product.variants: db_product.variants.append(ProductVariant(**v.dict()))
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

# --- Orders Router ---
orders_router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])
@orders_router.get("/cart/", response_model=List[CartItemResponse])
async def read_cart(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    items = await get_cart_items(db, current_user.id)
    return [{"id": i.id, "variant_id": i.variant_id, "quantity": i.quantity, "product_name": i.variant.product.name, "spec": i.variant.spec, "price": i.variant.price, "subtotal": i.variant.price * i.quantity, "image_url": i.variant.product.image_url} for i in items if i.variant and i.variant.product]

@orders_router.post("/cart/", response_model=CartItemResponse)
async def add_to_cart(cart_data: CartItemCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    res = await db.execute(select(ProductVariant).filter(ProductVariant.id == cart_data.variant_id))
    if not res.scalars().first(): raise HTTPException(status_code=404, detail="Variant not found")
    c_res = await db.execute(select(CartItem).filter(CartItem.user_id==current_user.id, CartItem.variant_id==cart_data.variant_id))
    if item := c_res.scalars().first(): item.quantity += cart_data.quantity
    else: 
        item = CartItem(user_id=current_user.id, variant_id=cart_data.variant_id, quantity=cart_data.quantity)
        db.add(item)
    await db.commit()
    query = select(CartItem).options(selectinload(CartItem.variant).selectinload(ProductVariant.product)).filter(CartItem.id == item.id)
    full_item = (await db.execute(query)).scalars().first()
    return {"id": full_item.id, "variant_id": full_item.variant_id, "quantity": full_item.quantity, "product_name": full_item.variant.product.name, "price": full_item.variant.price, "subtotal": full_item.variant.price * full_item.quantity}

@orders_router.post("/", response_model=OrderResponse)
async def create_order(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    order = await create_order_from_cart(db, current_user.id, current_user.discount_rate)
    if not order: raise HTTPException(status_code=400, detail="Cart is empty")
    return order

# 🟢 关键修复: 添加 /my 接口 (必须在 /{order_id} 之前)
@orders_router.get("/my", response_model=List[OrderResponse])
async def read_my_orders(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """快捷入口：查看我自己的订单"""
    # 复用 get_orders 逻辑 (内联写法)
    query = select(Order).options(joinedload(Order.items), joinedload(Order.user), joinedload(Order.driver)).order_by(desc(Order.created_at))
    query = query.filter(Order.user_id == current_user.id)
    return (await db.execute(query)).unique().scalars().all()

@orders_router.get("/", response_model=List[OrderResponse])
async def read_orders(skip: int = 0, limit: int = 100, q: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    query = select(Order).options(joinedload(Order.items), joinedload(Order.user), joinedload(Order.driver)).order_by(desc(Order.created_at))
    if current_user.role == "driver": query = query.filter(Order.driver_id == current_user.id)
    elif not (current_user.is_admin or current_user.role == "admin"): query = query.filter(Order.user_id == current_user.id)
    if q: query = query.join(User).filter(or_(User.email.ilike(f"%{q}%"), cast(Order.id, String).ilike(f"%{q}%")))
    return (await db.execute(query.offset(skip).limit(limit))).unique().scalars().all()

@orders_router.get("/{order_id}", response_model=OrderResponse)
async def read_order_detail(order_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    order = await get_order_by_id(db, order_id)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    if not (current_user.is_admin or order.user_id == current_user.id or order.driver_id == current_user.id):
        raise HTTPException(status_code=403, detail="Permission denied")
    return order

@orders_router.patch("/{order_id}/assign", response_model=OrderResponse)
async def assign_driver(order_id: int, req: AssignDriverRequest, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    order = await get_order_by_id(db, order_id)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    order.driver_id = req.driver_id
    order.status = OrderStatus.DELIVERING
    await db.commit()
    return await get_order_by_id(db, order_id)

@orders_router.post("/{order_id}/complete", response_model=OrderResponse)
async def complete_order(order_id: int, file: UploadFile = File(None), db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    order = await get_order_by_id(db, order_id)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != "admin" and order.driver_id != current_user.id: raise HTTPException(status_code=403)
    if file:
        await validate_image_security(file)
        fname = f"order_{order_id}_sign_{int(datetime.now().timestamp())}.{file.filename.split('.')[-1]}"
        fpath = os.path.join(STATIC_DIR, "uploads", fname)
        with open(fpath, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
        order.delivery_photo_url = f"/static/uploads/{fname}"
    order.status = OrderStatus.COMPLETED
    await db.commit()
    return await get_order_by_id(db, order_id)

# --- News Router ---
news_router = APIRouter(prefix="/api/v1/news", tags=["News"])
@news_router.get("/", response_model=List[NewsResponse])
async def read_news(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(News).filter(News.is_published==True).order_by(desc(News.created_at)).offset(skip).limit(limit))
    return res.scalars().all()

@news_router.post("/", response_model=NewsResponse)
async def create_news(news: NewsCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    db_news = News(**news.dict())
    db.add(db_news)
    await db.commit()
    await db.refresh(db_news)
    return db_news

# --- Inquiries Router ---
inquiries_router = APIRouter(prefix="/api/v1/inquiries", tags=["Inquiries"])
@inquiries_router.post("/", response_model=InquiryResponse)
async def create_inquiry(inq: InquiryCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    inquiry = await create_inquiry_from_cart(db, current_user.id, inq.user_remark)
    if not inquiry: raise HTTPException(status_code=400, detail="Cart is empty")
    return inquiry

@inquiries_router.get("/", response_model=List[InquiryResponse])
async def read_inquiries(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    query = select(Inquiry).options(selectinload(Inquiry.items), selectinload(Inquiry.user)).order_by(desc(Inquiry.created_at))
    if current_user.role != "admin": query = query.filter(Inquiry.user_id == current_user.id)
    if status: query = query.filter(Inquiry.status == status)
    return (await db.execute(query.offset(skip).limit(limit))).unique().scalars().all()

@inquiries_router.patch("/{inquiry_id}/quote", response_model=InquiryResponse)
async def quote_inquiry(inquiry_id: int, q: InquiryQuoteUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    inq = await get_inquiry_by_id(db, inquiry_id)
    if not inq: raise HTTPException(status_code=404)
    inq.quoted_total_price = q.quoted_total_price
    inq.admin_reply = q.admin_reply
    inq.status = InquiryStatus.QUOTED
    await db.commit()
    return await get_inquiry_by_id(db, inquiry_id)

# --- Specs Router ---
specs_router = APIRouter(prefix="/api/v1/specs", tags=["Specs"])
@specs_router.get("/", response_model=List[TechnicalSpecResponse])
async def read_specs(skip: int=0, limit: int=100, category: str=None, db: AsyncSession = Depends(get_db)):
    query = select(TechnicalSpec)
    if category: query = query.filter(TechnicalSpec.category == category)
    return (await db.execute(query.offset(skip).limit(limit))).scalars().all()

@specs_router.post("/", response_model=TechnicalSpecResponse)
async def create_spec(spec: TechnicalSpecCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    db_spec = TechnicalSpec(**spec.dict())
    db.add(db_spec)
    await db.commit()
    await db.refresh(db_spec)
    return db_spec

# --- Admin Costs Router ---
admin_costs_router = APIRouter(prefix="/api/v1/admin/costs", tags=["Admin Cost"], dependencies=[Depends(get_current_active_superuser)])

PROCESS_FEES = {"BVR": 1000, "BV": 200, "RVV": 700}

def calculate_copper_usd_price(market_cny: float, exchange_rate: float, category: str) -> float:
    base_cny = (market_cny * 0.935) + 1500.0
    surcharge = 0
    cat_upper = category.upper() if category else ""
    if "BVR" in cat_upper: surcharge = PROCESS_FEES["BVR"]
    elif "RVV" in cat_upper: surcharge = PROCESS_FEES["RVV"]
    elif "BV" in cat_upper: surcharge = PROCESS_FEES["BV"]
    return ((base_cny + surcharge) / exchange_rate) / 1000.0

# 🟢 关键修复: 添加 /categories 接口 (解决 404 /api/v1/admin/costs/categories)
@admin_costs_router.get("/categories", response_model=List[str])
async def get_cost_categories(db: AsyncSession = Depends(get_db)):
    query = select(ProductCost.category).where(ProductCost.category != None).distinct()
    result = await db.execute(query)
    categories = result.scalars().all()
    return sorted([c for c in categories if c])

@admin_costs_router.get("/calculate-unit-price")
async def get_calculated_unit_price(category: str = "", db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CopperPrice).order_by(desc(CopperPrice.updated_at)).limit(1))
    latest = res.scalars().first()
    if not latest: raise HTTPException(status_code=400, detail="No market price found")
    unit_price = calculate_copper_usd_price(latest.cny_price, latest.exchange_rate, category)
    return {"price": round(unit_price, 4), "market_cny": latest.cny_price, "rate": latest.exchange_rate}

@admin_costs_router.post("/sync-market-prices")
async def sync_costs_with_market(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(CopperPrice).order_by(desc(CopperPrice.updated_at)).limit(1))
    latest = res.scalars().first()
    if not latest: raise HTTPException(status_code=400, detail="No market price")
    res_costs = await db.execute(select(ProductCost))
    updated_count = 0
    for cost in res_costs.scalars().all():
        cost.copper_price = round(calculate_copper_usd_price(latest.cny_price, latest.exchange_rate, cost.category), 4)
        # Recalculate
        density = 0.214 if cost.material == "Al" else 0.7
        total_cw = sum([(g['gauge']**2 * g['strands'] * g['cores'] * density * cost.length)/100.0 for g in cost.core_structure])
        cost.copper_weight = round(total_cw, 4)
        cost.copper_amount = round(total_cw * cost.copper_price, 2)
        cost.pvc_weight = max(0.0, round(cost.total_weight - total_cw, 4))
        cost.pvc_amount = round(cost.pvc_weight * cost.pvc_price, 2)
        cost.total_cost = round(cost.copper_amount + cost.pvc_amount + cost.labor_cost, 2)
        cost.reference_price = round(cost.total_cost * 1.15, 2)
        updated_count += 1
    await db.commit()
    return {"message": f"Synced {updated_count} records"}

@admin_costs_router.post("/", response_model=CostResponse)
async def create_cost_record(cost: CostCreate, db: AsyncSession = Depends(get_db)):
    density = 0.214 if cost.material == "Al" else 0.7
    total_cw = sum([(g.gauge**2 * g.strands * g.cores * density * cost.length)/100.0 for g in cost.core_structure])
    cw = round(total_cw, 4)
    ca = round(total_cw * cost.copper_price, 2)
    pw = max(0.0, round(cost.total_weight - total_cw, 4))
    pa = round(pw * cost.pvc_price, 2)
    tc = round(ca + pa + cost.labor_cost, 2)
    new_cost = ProductCost(**cost.dict(), copper_weight=cw, copper_amount=ca, pvc_weight=pw, pvc_amount=pa, total_cost=tc, reference_price=round(tc*1.15, 2))
    db.add(new_cost)
    await db.commit()
    await db.refresh(new_cost)
    return new_cost

@admin_costs_router.get("/", response_model=List[CostResponse])
async def read_costs(skip: int = 0, limit: int = 100, category: str = None, search: str = None, db: AsyncSession = Depends(get_db)):
    query = select(ProductCost).order_by(desc(ProductCost.updated_at))
    if category: query = query.filter(ProductCost.category == category)
    if search: query = query.filter(or_(ProductCost.spec_name.contains(search), ProductCost.remark.contains(search)))
    return (await db.execute(query.offset(skip).limit(limit))).scalars().all()

# Register Routers
app.include_router(meta_router) # 🟢 注册新 meta 路由
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(news_router)
app.include_router(inquiries_router)
app.include_router(specs_router)
app.include_router(admin_costs_router)
app.include_router(categories_router)

# ==========================================
# 10. Start
# ==========================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)