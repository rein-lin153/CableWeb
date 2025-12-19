import bcrypt
import models, schemas
from sqlalchemy.orm import Session, joinedload # <--- [关键] 务必导入 joinedload
from sqlalchemy import or_, cast, String # <--- 新增导入

# ============================
# 1. 工具函数 (密码哈希)
# ============================
def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

# ============================
# 2. 用户管理 (User CRUD)
# ============================
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# [修改] 创建用户 (支持 username 和 role)
def create_user(db: Session, user: schemas.UserCreate, is_admin: bool = False):
    hashed_password = get_password_hash(user.password)
    
    # 如果 role 是 admin，自动设置 is_admin=True (保持兼容性)
    if user.role == "admin":
        is_admin = True
        
    db_user = models.User(
        email=user.email,
        username=user.username, # [新增]
        hashed_password=hashed_password,
        company_name=user.company_name,
        role=user.role,         # [新增]
        is_admin=is_admin,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# [新增] 更新用户 (通用更新)
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    
    # 特殊处理密码加密
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # 特殊处理角色同步 (如果改为 admin 角色，is_admin 也要变)
    if "role" in update_data:
        if update_data["role"] == "admin":
            update_data["is_admin"] = True
        elif update_data["role"] == "user" or update_data["role"] == "driver":
            update_data["is_admin"] = False

    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_role(db: Session, user_id: int, is_superuser: bool):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_admin = is_superuser
        db.commit()
        db.refresh(user)
    return user

# ============================
# 3. Token 黑名单 (Logout) [你缺失的部分!]
# ============================
def revoke_token(db: Session, token: str):
    """将 Token 加入黑名单"""
    db_token = models.TokenBlocklist(token=token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def is_token_revoked(db: Session, token: str) -> bool:
    """检查 Token 是否已失效"""
    result = db.query(models.TokenBlocklist).filter(models.TokenBlocklist.token == token).first()
    return result is not None

# ============================
# 4. 分类管理 (Category CRUD)
# ============================
def get_categories(db: Session, skip: int = 0, limit: int = 100, flat: bool = True):
    if flat:
        # [平铺模式] 返回所有数据，简单直接
        return db.query(models.Category).offset(skip).limit(limit).all()
    else:
        # [树形模式] 只返回 parent_id 为空的（顶级根节点）
        # SQLAlchemy 的 relationship 会自动懒加载 children
        # 加上 joinedload 可以一次性查出来 (对于超深层级建议 lazy loading，这里用 joinedload 优化性能)
        return db.query(models.Category)\
            .filter(models.Category.parent_id == None)\
            .offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_obj = models.Category(
        name=category.name, 
        description=category.description,
        parent_id=category.parent_id # [新增]
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_category(db: Session, category_id: int):
    # 1. 查找要删除的分类
    cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not cat:
        return False
    
    # 2. [保护逻辑] 处理子分类
    # 需求：将子分类的 parent_id 设为 NULL (变成顶级分类)，而不是级联删除
    children = db.query(models.Category).filter(models.Category.parent_id == category_id).all()
    for child in children:
        child.parent_id = None
    
    # 3. 删除自身
    db.delete(cat)
    db.commit()
    return True

# [新增] 更新分类
def update_category(db: Session, category_id: int, category_update: schemas.CategoryUpdate):
    # 1. 查找分类
    db_cat = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not db_cat:
        return None
    
    # 2. 提取要修改的数据
    update_data = category_update.dict(exclude_unset=True)
    
    # 3. 如果要修改 parent_id，防止把自己设为自己的父亲（死循环）
    if "parent_id" in update_data and update_data["parent_id"] == category_id:
        # 简单处理：忽略这个修改，或者抛错。这里选择忽略
        del update_data["parent_id"]

    # 4. 执行更新
    for key, value in update_data.items():
        setattr(db_cat, key, value)
    
    db.commit()
    db.refresh(db_cat)
    return db_cat

# ============================
# 5. 产品管理 (Product CRUD)
# ============================
# 1. 获取产品列表 (预加载变体)
def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    category_id: int = None,
    search: str = None # [新增] 搜索关键词
):
    query = db.query(models.Product)
    
    # 现有分类过滤
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    
    # [新增] 搜索逻辑: 名称 OR 描述 (不区分大小写)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                models.Product.name.ilike(search_fmt),
                models.Product.description.ilike(search_fmt)
            )
        )
        
    return query.offset(skip).limit(limit).all()

# 2. 获取单条详情 (预加载变体)
def get_product(db: Session, product_id: int):
    return db.query(models.Product)\
        .options(joinedload(models.Product.variants))\
        .filter(models.Product.id == product_id).first()

# 3. 创建产品 (事务：同时创建父子表)
def create_product(db: Session, product: schemas.ProductCreate):
    # A. 创建父对象
    db_product = models.Product(
        name=product.name,
        description=product.description,
        image_url=product.image_url,
        category_id=product.category_id,
        has_variants=True,
        unit=product.unit
    )
    # B. 转换变体数据为 Model 对象列表
    # SQLAlchemy 会在 commit 时自动处理外键关联
    for v_data in product.variants:
        variant = models.ProductVariant(**v_data.dict())
        db_product.variants.append(variant)

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# 4. 更新产品 (支持全量替换变体)
def update_product(db: Session, product_id: int, product_update: schemas.ProductUpdate):
    # 必须先把原对象查出来
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    # A. 更新基础字段
    update_data = product_update.dict(exclude_unset=True)
    
    # 这里的 variants 单独处理，从 update_data 中剔除
    variants_data = update_data.pop('variants', None) 

    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    # B. 更新变体 (全量替换逻辑)
    if variants_data is not None:
        # 1. SQLAlchemy 的 delete-orphan 机制：
        # 当我们把 db_product.variants 赋值为一个新列表时，
        # 旧的且不在新列表中的对象会被自动从数据库删除。
        
        new_variants = []
        for v in variants_data:
            # 注意：这里是创建新的 Variant 对象
            new_variants.append(models.ProductVariant(**v))
        
        # 直接赋值，SQLAlchemy 自动处理：删除旧的，插入新的
        db_product.variants = new_variants

    db.commit()
    db.refresh(db_product)
    return db_product

# 5. 删除产品 (级联删除)
def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if db_product:
        # 由于配置了 cascade="all, delete-orphan"，删除父对象会自动删除所有变体
        db.delete(db_product)
        db.commit()
        return True
    return False

# 获取新闻列表 (分页 + 按时间倒序)
def get_news_list(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.News)\
        .filter(models.News.is_published == True)\
        .order_by(models.News.created_at.desc())\
        .offset(skip).limit(limit).all()

# 获取单条新闻详情
def get_news_by_id(db: Session, news_id: int):
    return db.query(models.News).filter(models.News.id == news_id).first()

# 创建新闻
def create_news(db: Session, news: schemas.NewsCreate):
    db_news = models.News(**news.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

# 删除新闻
def delete_news(db: Session, news_id: int):
    db_news = db.query(models.News).filter(models.News.id == news_id).first()
    if db_news:
        db.delete(db_news)
        db.commit()
        return True
    return False


# ============================
# 7. 购物车 (Cart)
# ============================
def get_cart_items(db: Session, user_id: int):
    # 预加载 variant 和 variant.product (用于拿商品名和图片)
    return db.query(models.CartItem)\
             .options(joinedload(models.CartItem.variant).joinedload(models.ProductVariant.product))\
             .filter(models.CartItem.user_id == user_id).all()
             
def add_to_cart(db: Session, user_id: int, variant_id: int, quantity: int):
    # 检查变体是否存在
    variant = db.query(models.ProductVariant).filter(models.ProductVariant.id == variant_id).first()
    if not variant:
        return None

    cart_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.variant_id == variant_id
    ).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = models.CartItem(user_id=user_id, variant_id=variant_id, quantity=quantity)
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart_item)
    return cart_item


def remove_from_cart(db: Session, user_id: int, item_id: int):
    item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id, 
        models.CartItem.user_id == user_id
    ).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False

def clear_cart(db: Session, user_id: int):
    db.query(models.CartItem).filter(models.CartItem.user_id == user_id).delete()
    db.commit()

# ============================
# 8. 订单 (Order) - 核心交易逻辑
# ============================
def create_order_from_cart(db: Session, user_id: int, discount_rate: float):
    cart_items = get_cart_items(db, user_id)
    if not cart_items: return None
    
    original_total = 0.0
    order_items_data = []

    for item in cart_items:
        variant = item.variant
        product = variant.product # 父商品
        
        unit_price = variant.price
        subtotal = unit_price * item.quantity
        original_total += subtotal
        
        # 准备快照数据
        order_items_data.append({
            "product_id": product.id,
            "product_name": product.name,
            "product_image": product.image_url,
            # [关键] 记录规格和颜色
            "product_spec": variant.spec,
            "product_color": variant.color,
            "product_unit": variant.unit,
            "unit_price": unit_price,
            "quantity": item.quantity,
            "subtotal": subtotal
        })
    
    final_total = round(original_total * (1 - discount_rate), 2)

    db_order = models.Order(
        user_id=user_id,
        status=models.OrderStatus.PENDING_CONFIRMATION,
        original_total_price=original_total,
        final_total_price=final_total
    )
    db.add(db_order)
    db.flush()

    for item_data in order_items_data:
        db_item = models.OrderItem(order_id=db_order.id, **item_data)
        db.add(db_item)
    
    # 清空购物车
    db.query(models.CartItem).filter(models.CartItem.user_id == user_id).delete()
    db.commit()
    db.refresh(db_order)
    return db_order

# 获取订单列表 (可选按用户筛选) - 优化预加载
def get_orders(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    user_id: int = None, # 如果传入则只看该用户的，否则看所有(Admin)
    driver_id: int = None,
    search: str = None   # [新增] 搜索关键词
):
    # 预加载 User 信息，因为我们可能需要搜索 User.email
    query = db.query(models.Order).join(models.User).options(
        joinedload(models.Order.items),
        joinedload(models.Order.user),
        joinedload(models.Order.driver)
    )

    # 权限过滤 (保持原有逻辑)
    if user_id:
        query = query.filter(models.Order.user_id == user_id)
    if driver_id:
        query = query.filter(models.Order.driver_id == driver_id)

    # [新增] 搜索逻辑: 订单ID(转字符串) OR 用户邮箱
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                # 模糊匹配买家邮箱
                models.User.email.ilike(search_fmt),
                # 将整数类型的 ID 转为字符串再匹配 (例如输入 "10" 能搜到 ID 102)
                cast(models.Order.id, String).ilike(search_fmt)
            )
        )

    return query.order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

# [修改] 获取单条订单详情 (包含所有关联数据)
def get_order_by_id(db: Session, order_id: int):
    return db.query(models.Order)\
        .options(
            joinedload(models.Order.items),   # 加载商品
            joinedload(models.Order.user),    # 加载买家信息
            joinedload(models.Order.driver)   # [新增] 加载司机信息(为了拿到坐标/名字)
        )\
        .filter(models.Order.id == order_id).first()

def update_order_status(db: Session, order_id: int, status: models.OrderStatus):
    order = get_order_by_id(db, order_id)
    if order:
        order.status = status
        db.commit()
        db.refresh(order)
    return order

def update_order_price(db: Session, order_id: int, new_price: float):
    order = get_order_by_id(db, order_id)
    if order:
        order.final_total_price = new_price
        db.commit()
        db.refresh(order)
    return order

# ============================
# 9. 用户折扣管理
# ============================
def update_user_discount(db: Session, user_id: int, discount_rate: float):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.discount_rate = discount_rate
        db.commit()
        db.refresh(user)
    return user


# [新增] 修改订单明细单价并重算总价
def update_order_item_price(db: Session, order_id: int, item_id: int, new_unit_price: float):
    # 1. 查询该订单明细
    # 同时关联出 order 对象，方便后续操作
    item = db.query(models.OrderItem).filter(
        models.OrderItem.id == item_id,
        models.OrderItem.order_id == order_id # 安全检查：确保item属于该order
    ).first()

    if not item:
        return None

    # 2. 更新该明细的单价和小计
    item.unit_price = new_unit_price
    # 计算小计 (保留2位小数)
    item.subtotal = round(new_unit_price * item.quantity, 2)
    
    # 3. 核心逻辑：重新计算订单总价
    # 获取该订单下的所有 items
    # 注意：此时 session 中的 item 已经是更新过的值了，但还没 commit，
    # 直接使用 order.items 遍历通常能获取到 session 中的脏数据(Dirty state)，
    # 但为了绝对稳健，我们显式重新计算。
    
    current_order = item.order
    new_final_total = 0.0
    
    for order_item in current_order.items:
        # 这里的 order_item.subtotal 已经是上面更新过的值了
        new_final_total += order_item.subtotal
    
    # 4. 更新订单主表
    current_order.final_total_price = round(new_final_total, 2)

    # 5. 提交事务
    db.commit()
    
    # 6. 刷新并返回最新的 Order 对象
    db.refresh(current_order)
    return current_order


# [新增] 更新新闻
def update_news(db: Session, news_id: int, news_update: schemas.NewsUpdate):
    # 1. 查找新闻
    db_news = db.query(models.News).filter(models.News.id == news_id).first()
    if not db_news:
        return None
    
    # 2. 动态更新字段 (exclude_unset=True 确保只更新前端传来的字段)
    update_data = news_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_news, key, value)
    
    
# ============================
# 订单状态管理 (核心业务逻辑)
# ============================

# 1. 确认订单 (Confirm) -> 扣减库存
def confirm_order(db: Session, order_id: int):
    order = db.query(models.Order).options(joinedload(models.Order.items)).filter(models.Order.id == order_id).first()
    if not order or order.status != models.OrderStatus.PENDING_CONFIRMATION:
        return None, "Invalid order"

    for item in order.items:
        # 这里需要稍微复杂的逻辑去回溯 Variant ID。
        # 由于 OrderItem 没存 variant_id (为了防止 variant 被删)，我们通过 product_id + spec + color 去找。
        # 或者更简单的：你在 OrderItem 里也存一个 variant_id (nullable)，如果 variant 还在就用 id 找，不在就报错。
        
        # 这里演示通过匹配规格查找：
        variant = db.query(models.ProductVariant).filter(
            models.ProductVariant.product_id == item.product_id,
            models.ProductVariant.spec == item.product_spec,
            models.ProductVariant.color == item.product_color
        ).first()
        
        if not variant:
            continue # 变体可能被删了，无法扣库存
            
        if variant.stock < item.quantity:
            return None, f"库存不足: {item.product_name} {item.product_spec}"
        
        variant.stock -= item.quantity
    
    order.status = models.OrderStatus.CONFIRMED
    db.commit()
    db.refresh(order)
    return order, None

# 2. 发货 (Ship)
def ship_order(db: Session, order_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order: return None, "Not found"
    if order.status != models.OrderStatus.CONFIRMED:
        return None, "Order must be confirmed before shipping"
    
    order.status = models.OrderStatus.DELIVERING
    db.commit()
    db.refresh(order)
    return order, None

# 3. 完成 (Complete)
def complete_order(db: Session, order_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order: return None, "Not found"
    if order.status != models.OrderStatus.DELIVERING:
        return None, "Order must be delivering before complete"
    
    order.status = models.OrderStatus.COMPLETED
    db.commit()
    db.refresh(order)
    return order, None

# 4. 取消订单 (Cancel) -> 回滚库存
def cancel_order(db: Session, order_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order: return None, "Not found"
    
    if order.status == models.OrderStatus.COMPLETED:
        return None, "Cannot cancel completed order"
    
    if order.status == models.OrderStatus.CANCELLED:
        return None, "Order already cancelled"

    # 只有在该订单曾经扣过库存的情况下（已确认或派送中），才需要把库存加回去
    should_rollback_stock = order.status in [models.OrderStatus.CONFIRMED, models.OrderStatus.DELIVERING]

    if should_rollback_stock:
        for item in order.items:
            # 同样尝试找回产品
            product = db.query(models.Product).filter(models.Product.name == item.product_name).first()
            if product:
                product.stock += item.quantity
    
    order.status = models.OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    return order, None    

# ============================
# 司机与物流管理
# ============================

# 1. 获取所有司机
def get_drivers(db: Session):
    return db.query(models.User).filter(models.User.role == "driver").all()

# 2. 指派司机
def assign_driver(db: Session, order_id: int, driver_id: int):
    # 检查司机是否存在且角色正确
    driver = db.query(models.User).filter(models.User.id == driver_id, models.User.role == "driver").first()
    if not driver:
        return None, "Driver not found or invalid role"
    
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return None, "Order not found"
    
    # 更新订单
    order.driver_id = driver_id
    order.status = models.OrderStatus.DELIVERING # 指派即开始派送
    db.commit()
    db.refresh(order)
    return order, None

# 3. 更新位置 (司机端)
def update_driver_location(db: Session, order_id: int, lat: float, lng: float):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return None
    
    order.driver_lat = lat
    order.driver_lng = lng
    db.commit()
    db.refresh(order)
    return order

# 4. 获取司机的任务列表
def get_driver_tasks(db: Session, driver_id: int):
    return db.query(models.Order)\
        .options(joinedload(models.Order.items), joinedload(models.Order.user))\
        .filter(
            models.Order.driver_id == driver_id,
            models.Order.status == models.OrderStatus.DELIVERING
        ).all()

    # 3. 提交并返回
    db.commit()
    db.refresh(db_news)
    return db_news

# ============================
# 技术参数 CRUD (新增)
# ============================

# 1. 获取列表 (支持 搜索 和 分类过滤)
def get_technical_specs(db: Session, skip: int = 0, limit: int = 100, category: str = None, search: str = None):
    query = db.query(models.TechnicalSpec)
    
    if category:
        query = query.filter(models.TechnicalSpec.category == category)
    
    if search:
        # 模糊搜索型号或特性
        query = query.filter(
            (models.TechnicalSpec.model.contains(search)) | 
            (models.TechnicalSpec.feature.contains(search))
        )
        
    return query.order_by(models.TechnicalSpec.model.asc()).offset(skip).limit(limit).all()

# 2. 创建参数
def create_technical_spec(db: Session, spec: schemas.TechnicalSpecCreate):
    db_spec = models.TechnicalSpec(**spec.dict())
    db.add(db_spec)
    db.commit()
    db.refresh(db_spec)
    return db_spec

# 3. 更新参数
def update_technical_spec(db: Session, spec_id: int, spec_update: schemas.TechnicalSpecUpdate):
    db_spec = db.query(models.TechnicalSpec).filter(models.TechnicalSpec.id == spec_id).first()
    if not db_spec:
        return None
    
    update_data = spec_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_spec, key, value)
        
    db.commit()
    db.refresh(db_spec)
    return db_spec

# 4. 删除参数
def delete_technical_spec(db: Session, spec_id: int):
    db_spec = db.query(models.TechnicalSpec).filter(models.TechnicalSpec.id == spec_id).first()
    if db_spec:
        db.delete(db_spec)
        db.commit()
        return True
    return False