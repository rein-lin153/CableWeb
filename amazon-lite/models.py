# models.py (最终合并版)
import enum
from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship, backref
from database import Base
from datetime import datetime

# ============================
# 1. 枚举定义
# ============================

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

# ============================
# 2. 用户与权限
# ============================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, index=True, nullable=True) # 员工/用户昵称
    hashed_password = Column(String)
    
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False) # 兼容旧代码
    role = Column(String, default=UserRole.USER) # 新的角色字段
    
    company_name = Column(String, nullable=True)
    discount_rate = Column(Float, default=0.0)

    # 关系
    cart_items = relationship("CartItem", back_populates="user")
    
    # 作为买家的订单
    orders = relationship("Order", foreign_keys="[Order.user_id]", back_populates="user")
    
    # 作为司机的运单
    assigned_orders = relationship("Order", foreign_keys="[Order.driver_id]", back_populates="driver")

class TokenBlocklist(Base):
    __tablename__ = "token_blocklist"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================
# 3. 产品与分类
# ============================

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    
    # 无限层级支持
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    children = relationship(
        "Category",
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete"
    )
    
    products = relationship("Product", back_populates="category_rel")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    image_url = Column(String)
    unit = Column(String, default="卷") # 默认单位
    
    has_variants = Column(Boolean, default=True) # 是否启用多规格
    
    category_id = Column(Integer, ForeignKey("categories.id"))
    category_rel = relationship("Category", back_populates="products")
    
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    
    spec = Column(String)  # 规格
    color = Column(String) # 颜色
    price = Column(Float)  # 单价
    stock = Column(Integer, default=0)
    unit = Column(String, default="米")
    sku_code = Column(String, nullable=True)

    product = relationship("Product", back_populates="variants")
    cart_items = relationship("CartItem", back_populates="variant")

# ============================
# 4. 交易与订单
# ============================

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
    
    # 买卖双方
    user_id = Column(Integer, ForeignKey("users.id"))
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 物流位置
    driver_lat = Column(Float, nullable=True)
    driver_lng = Column(Float, nullable=True)
    # [新增] 送达拍照图片路径
    delivery_photo_url = Column(String, nullable=True)

    # 状态与金额
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING_CONFIRMATION)
    original_total_price = Column(Float, default=0.0)
    final_total_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系绑定
    user = relationship("User", foreign_keys=[user_id], back_populates="orders")
    driver = relationship("User", foreign_keys=[driver_id], back_populates="assigned_orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    @property
    def user_email(self):
        return self.user.email if self.user else "Unknown"

    @property
    def driver_email(self):
        return self.driver.email if self.driver else None

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    
    # 快照数据
    product_id = Column(Integer, nullable=True) # 记录ID用于回溯
    product_name = Column(String)
    product_spec = Column(String)
    product_color = Column(String)
    product_image = Column(String, nullable=True)
    product_unit = Column(String)
    
    unit_price = Column(Float)
    quantity = Column(Integer)
    subtotal = Column(Float)

    order = relationship("Order", back_populates="items")

# ============================
# 5. 其他 (资讯/铜价)
# ============================

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

    # ============================
# 6. 技术参数 (新增)
# ============================
class TechnicalSpec(Base):
    __tablename__ = "technical_specs"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, index=True)      # 规格型号 (如 BV 2.5)
    category = Column(String, index=True)   # 分类 (如 家装电线)
    
    standard_param = Column(String)         # 国标要求
    actual_param = Column(String)           # 实测数据
    feature = Column(String)                # 产品特性描述
    
    created_at = Column(DateTime, default=datetime.utcnow)