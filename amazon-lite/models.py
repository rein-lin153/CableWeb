import enum
from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship, backref
from database import Base
from datetime import datetime
from sqlalchemy import JSON # 🟢 引入 JSON 类型

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

class InquiryStatus(str, enum.Enum):
    PENDING = "pending"      # 待报价
    QUOTED = "quoted"        # 已报价
    ACCEPTED = "accepted"    # 客户已接受(转订单)
    REJECTED = "rejected"    # 客户已拒绝
    CLOSED = "closed"        # 关闭

# ============================
# 2. 用户与权限
# ============================
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

    # 关系
    cart_items = relationship("CartItem", back_populates="user")
    orders = relationship("Order", foreign_keys="[Order.user_id]", back_populates="user")
    assigned_orders = relationship("Order", foreign_keys="[Order.driver_id]", back_populates="driver")
    # [新增] 询价单关系
    inquiries = relationship("Inquiry", back_populates="user")

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
    name = Column(String, index=True)
    # 🟢 [新增] 父级ID (自关联)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # 关系
    products = relationship("Product", back_populates="category")
    # 🟢 [新增] 子分类关系
    children = relationship("Category", backref=backref("parent", remote_side=[id]))
# 2. 升级产品表 (关联成本)
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    # ... (保留 name, description 等原有字段) ...
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    is_active = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))

    # 🟢 [新增] 关联成本ID (用于追踪该商品来自哪个成本核算)
    cost_id = Column(Integer, ForeignKey("product_costs.id"), nullable=True)

    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product")
    # 🟢 [新增] 关系
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

# ============================
# 5. [新增] 询价系统 (Inquiry)
# ============================
class Inquiry(Base):
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    status = Column(Enum(InquiryStatus), default=InquiryStatus.PENDING)
    
    # 销售报价总金额 (初始为 None)
    quoted_total_price = Column(Float, nullable=True)
    
    # 客户留言 / 销售备注
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
    
    # 预留快照字段，防止变体被删
    product_name = Column(String)
    product_spec = Column(String)
    product_color = Column(String)
    
    quantity = Column(Integer)
    
    # 销售给出的单价 (初始为 None)
    quoted_unit_price = Column(Float, nullable=True)

    inquiry = relationship("Inquiry", back_populates="items")
    variant = relationship("ProductVariant")

# ============================
# 6. 其他 (资讯/铜价/规格书)
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
    reference_price = Column(Float, default=0.0) # 参考售价 (成本+15%)
    
    spec_name = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=True)
    remark = Column(String, nullable=True)

    # 🟢 [核心升级] 
    # 材质: "Cu" (铜), "Al" (铝)
    material = Column(String, default="Cu", nullable=False)
    
    # 核心结构 (JSON list)
    # 存储格式示例: 
    # [
    #   {"cores": 3, "gauge": 1.35, "strands": 7},  // 3*10 部分
    #   {"cores": 1, "gauge": 1.04, "strands": 7}   // 1*6 部分
    # ]
    core_structure = Column(JSON, nullable=False) 

    total_weight = Column(Float, nullable=False)  # 整卷总重 (kg)
    length = Column(Float, default=100.0)         # 长度 (m)
    
    # 🟢 [价格参数]
    # 绝缘类型 (用于备注，如 PVC, XLPE)
    insulation_type = Column(String, default="PVC") 
    
    copper_price = Column(Float, nullable=False)  # 导体单价 (铜/铝)
    pvc_price = Column(Float, nullable=False)     # 非导体材料均价 (绝缘+填充+护套)
    labor_cost = Column(Float, default=0.0)       # 人工

    # [计算结果]
    copper_weight = Column(Float) # 导体总重
    copper_amount = Column(Float) # 导体总金额
    pvc_weight = Column(Float)    # 塑料总重
    pvc_amount = Column(Float)    # 塑料总金额
    total_cost = Column(Float)    # 总成本

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)