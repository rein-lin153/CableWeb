# amazon-lite/schemas.py (修复完整版)

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

class InquiryStatusEnum(str, Enum):
    PENDING = "pending"
    QUOTED = "quoted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CLOSED = "closed"

# ============================
# 2. Category
# ============================
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

# ============================
# 3. Product & Variants
# ============================
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

# ============================
# 4. User & Token
# ============================
class UserBase(BaseModel):
    email: str
    company_name: Optional[str] = None
    username: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "user"

# [修复] 补全后台管理需要的 Update 类
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

# ============================
# 7. Inquiry (询价系统)
# ============================
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

# ============================
# 8. Others (News, Specs, Copper)
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

# 解决 Pydantic 递归模型引用
CategoryResponse.model_rebuild()

# 🟢 [新增] 单组核心的结构定义
class CoreGroup(BaseModel):
    cores: int        # 芯数 (如 3)
    strands: int      # 每芯根数 (如 7)
    gauge: float      # 单丝直径 (mm)

# 基础输入字段
class CostBase(BaseModel):
    spec_name: str
    category: Optional[str] = None
    remark: Optional[str] = None
    
    material: str = "Cu"       # Cu / Al
    insulation_type: str = "PVC"
    
    # 🟢 [升级] 支持多组核心
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

# 返回给管理员的完整数据
class CostResponse(CostBase):
    id: int
    copper_weight: float
    copper_amount: float
    pvc_weight: float
    pvc_amount: float
    total_cost: float
    updated_at: datetime
    reference_price: float # [新增]
    class Config:
        from_attributes = True

    # 🟢 分类树结构
class CategoryTree(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    children: List['CategoryTree'] = [] # 递归结构
    
    class Config:
        from_attributes = True

# 🟢 转换请求体
class ConvertCostToProduct(BaseModel):
    cost_id: int
    target_category_id: int # 必须指定一个公共分类
    name: str # 允许修改名称
    price: float # 允许修改建议售价
    description: Optional[str] = None
    image_url: Optional[str] = None