# schemas.py (调整顺序版)

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ============================
# 1. 枚举 & 基础类 (Enums)
# ============================
class OrderStatusEnum(str, Enum):
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# ============================
# 2. Category (必须放在 Product 之前！)
# ============================
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    # [新增] 允许指定父级
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

# [新增] 更新分类使用的 Schema (所有字段都是可选的)
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None

# [修改] 返回分类时，包含子分类列表
class CategoryResponse(CategoryBase):
    id: int
    children: List['CategoryResponse'] = []
    class Config:
        from_attributes = True

# ============================
# 3. Product & Variants (放在 Category 之后)
# ============================


# [新增] 变体创建/更新的基础字段
class ProductVariantBase(BaseModel):
    spec: str        # 规格
    color: str       # 颜色
    price: float     # 价格
    stock: int       # 库存
    unit: str = "米"
    sku_code: Optional[str] = None # ERP编码
    
    
# --- 3.1 变体 ---
class ProductVariantBase(BaseModel):
    spec: str
    color: str
    price: float
    stock: int
    unit: str = "米"
    sku_code: Optional[str] = None

class ProductVariantCreate(ProductVariantBase):
    pass

class ProductVariantResponse(ProductVariantBase):
    id: int
    class Config:
        from_attributes = True

# --- 3.2 产品 ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    has_variants: bool = True
    unit: str = "卷"

# [修改] 创建产品时，接收变体列表
class ProductCreate(ProductBase):
    variants: List[ProductVariantCreate] = [] # 必填，但可以是空列表

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    has_variants: Optional[bool] = None
    variants: Optional[List[ProductVariantCreate]] = None   # 可选更新变体列表
    # [新增] 允许修改单位
    unit: Optional[str] = None

# [修改] 返回产品时，包含变体列表
class ProductResponse(ProductBase):
    id: int
    category_detail: Optional['CategoryResponse'] = None
    
    # 返回完整的变体数据，前端可据此计算 价格区间 和 总库存
    variants: List[ProductVariantResponse] = []

    class Config:
        from_attributes = True

# ============================
# 4. User & Token
# ============================
class UserBase(BaseModel):
    email: str
    company_name: Optional[str] = None
    # [新增] 基础字段包含 username
    username: Optional[str] = None

class UserCreate(UserBase):
    password: str
    username: str # 创建时必填
    role: str = "user" # 默认为普通用户，管理员可选 driver/admin
    
# [新增] 更新用户 Schema (管理员用)
class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None # 允许改密码
    company_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None # 允许改角色
    discount_rate: Optional[float] = None

class UserRoleUpdate(BaseModel):
    is_superuser: bool

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserDiscountUpdate(BaseModel):
    discount_rate: float

# [修改] 返回用户 Schema
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    discount_rate: float
    role: str
    # username 继承自 UserBase
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None

# ============================
# 5. Cart
# ============================
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

# ============================
# 6. Order
# ============================
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
    # [新增] 司机及位置信息
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
        
# 3. [新增] 派送员位置更新 Schema
class DriverLocationUpdate(BaseModel):
    lat: float
    lng: float

# 4. [新增] 指派司机 Schema
class AssignDriverRequest(BaseModel):
    driver_id: int

class OrderPriceUpdate(BaseModel):
    new_price: float

class OrderItemPriceUpdate(BaseModel):
    new_unit_price: float

# ============================
# 7. News & Copper (其他)
# ============================
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
        
# [新增] 角色枚举
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    DRIVER = "driver"

# ============================
# Technical Spec Schemas (新增)
# ============================

class TechnicalSpecBase(BaseModel):
    model: str
    category: str
    standard_param: Optional[str] = None
    actual_param: Optional[str] = None
    feature: Optional[str] = None

# 创建时使用
class TechnicalSpecCreate(TechnicalSpecBase):
    pass

# 更新时使用 (所有字段可选)
class TechnicalSpecUpdate(BaseModel):
    model: Optional[str] = None
    category: Optional[str] = None
    standard_param: Optional[str] = None
    actual_param: Optional[str] = None
    feature: Optional[str] = None

# 返回给前端使用
class TechnicalSpecResponse(TechnicalSpecBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        
        
CategoryResponse.model_rebuild()