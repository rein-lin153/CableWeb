# amazon-lite/crud.py
import bcrypt
import models, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, cast, String
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError

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
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user(db: AsyncSession, user: schemas.UserCreate, is_admin: bool = False):
    hashed_password = get_password_hash(user.password)
    if user.role == "admin":
        is_admin = True
        
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        company_name=user.company_name,
        role=user.role,
        is_admin=is_admin,
        is_active=True
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, user_id: int, user_update: schemas.UserUpdate):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    db_user = result.scalars().first()
    if not db_user: return None
    
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    if "role" in update_data:
        if update_data["role"] == "admin":
            update_data["is_admin"] = True
        elif update_data["role"] in ["user", "driver"]:
            update_data["is_admin"] = False

    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user_role(db: AsyncSession, user_id: int, is_superuser: bool):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()
    if user:
        user.is_admin = is_superuser
        await db.commit()
        await db.refresh(user)
    return user

# ============================
# 3. Token 黑名单
# ============================
async def revoke_token(db: AsyncSession, token: str):
    db_token = models.TokenBlocklist(token=token)
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    return db_token

async def is_token_revoked(db: AsyncSession, token: str) -> bool:
    result = await db.execute(select(models.TokenBlocklist).filter(models.TokenBlocklist.token == token))
    return result.scalars().first() is not None

# ============================
# 4. 分类管理
# ============================
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100, flat: bool = True):
    if flat:
        # [修复点] 增加 options(selectinload(...))
        # 即使是平铺模式，前端可能仍需要 children 字段（哪怕是空的），必须预加载防止报错
        query = select(models.Category).options(selectinload(models.Category.children)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    else:
        # 树形模式：只查顶级分类，并预加载子分类
        query = select(models.Category)\
            .filter(models.Category.parent_id == None)\
            .options(selectinload(models.Category.children))\
            .offset(skip).limit(limit)
        
        result = await db.execute(query)
        # unique() 是为了防止 joinedload/selectinload 产生重复行（虽然 selectinload 通常不需要，但加上更保险）
        return result.unique().scalars().all()

async def create_category(db: AsyncSession, category: schemas.CategoryCreate):
    # Pydantic v2 使用 model_dump(), v1 使用 dict()
    # 你的环境大概率是 v2，建议用 model_dump()，如果报错则改回 dict()
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    try:
        await db.commit()
        await db.refresh(db_category)
        return db_category
    except IntegrityError:
        # 捕获“唯一性约束”失败的错误
        await db.rollback()
        return None

async def delete_category(db: AsyncSession, category_id: int):
    result = await db.execute(select(models.Category).filter(models.Category.id == category_id))
    cat = result.scalars().first()
    if not cat: return False
    
    # 处理子分类：将子分类 parent_id 设为 None
    child_res = await db.execute(select(models.Category).filter(models.Category.parent_id == category_id))
    children = child_res.scalars().all()
    for child in children:
        child.parent_id = None
    
    await db.delete(cat)
    await db.commit()
    return True

async def update_category(db: AsyncSession, category_id: int, category_update: schemas.CategoryUpdate):
    result = await db.execute(select(models.Category).filter(models.Category.id == category_id))
    db_cat = result.scalars().first()
    if not db_cat: return None
    
    update_data = category_update.dict(exclude_unset=True)
    if "parent_id" in update_data and update_data["parent_id"] == category_id:
        del update_data["parent_id"]

    for key, value in update_data.items():
        setattr(db_cat, key, value)
    
    await db.commit()
    await db.refresh(db_cat)
    return db_cat

# ============================
# 5. 产品管理
# ============================
async def get_products(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    category_id: int = None,
    search: str = None
):
    query = select(models.Product).options(joinedload(models.Product.variants))
    
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                models.Product.name.ilike(search_fmt),
                models.Product.description.ilike(search_fmt)
            )
        )
        
    result = await db.execute(query.offset(skip).limit(limit))
    return result.unique().scalars().all()

async def get_product(db: AsyncSession, product_id: int):
    query = select(models.Product)\
        .options(joinedload(models.Product.variants))\
        .filter(models.Product.id == product_id)
    result = await db.execute(query)
    return result.unique().scalars().first()

async def create_product(db: AsyncSession, product: schemas.ProductCreate):
    db_product = models.Product(
        name=product.name,
        description=product.description,
        image_url=product.image_url,
        category_id=product.category_id,
        has_variants=True,
        unit=product.unit
    )
    for v_data in product.variants:
        variant = models.ProductVariant(**v_data.dict())
        db_product.variants.append(variant)

    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    query = select(models.Product)\
        .options(selectinload(models.Product.variants))\
        .filter(models.Product.id == db_product.id)
    result = await db.execute(query)
    return result.scalars().first()

async def update_product(db: AsyncSession, product_id: int, product_update: schemas.ProductUpdate):
    db_product = await get_product(db, product_id)
    if not db_product: return None
    
    update_data = product_update.dict(exclude_unset=True)
    variants_data = update_data.pop('variants', None) 

    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    if variants_data is not None:
        # 在 async 模式下，全量替换最好是清空旧的再加新的
        # 但直接操作 .variants 集合通常可行，注意 lazy load 问题
        # 简单起见，我们假设前端传来全量数据
        db_product.variants = [models.ProductVariant(**v) for v in variants_data]

    await db.commit()
    await db.refresh(db_product)
    return db_product

async def delete_product(db: AsyncSession, product_id: int):
    # 使用 get_product 确保变体加载
    db_product = await get_product(db, product_id)
    if db_product:
        await db.delete(db_product)
        await db.commit()
        return True
    return False

# 新闻管理
async def get_news_list(db: AsyncSession, skip: int = 0, limit: int = 10):
    query = select(models.News)\
        .filter(models.News.is_published == True)\
        .order_by(models.News.created_at.desc())\
        .offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_news_by_id(db: AsyncSession, news_id: int):
    result = await db.execute(select(models.News).filter(models.News.id == news_id))
    return result.scalars().first()

async def create_news(db: AsyncSession, news: schemas.NewsCreate):
    db_news = models.News(**news.dict())
    db.add(db_news)
    await db.commit()
    await db.refresh(db_news)
    return db_news

async def update_news(db: AsyncSession, news_id: int, news_update: schemas.NewsUpdate):
    result = await db.execute(select(models.News).filter(models.News.id == news_id))
    db_news = result.scalars().first()
    if not db_news: return None
    
    update_data = news_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_news, key, value)
    
    await db.commit()
    await db.refresh(db_news)
    return db_news

async def delete_news(db: AsyncSession, news_id: int):
    result = await db.execute(select(models.News).filter(models.News.id == news_id))
    db_news = result.scalars().first()
    if db_news:
        await db.delete(db_news)
        await db.commit()
        return True
    return False

# ============================
# 7. 购物车 (Cart)
# ============================
async def get_cart_items(db: AsyncSession, user_id: int):
    query = select(models.CartItem)\
             .options(joinedload(models.CartItem.variant).joinedload(models.ProductVariant.product))\
             .filter(models.CartItem.user_id == user_id)
    result = await db.execute(query)
    return result.scalars().all()
             
async def add_to_cart(db: AsyncSession, user_id: int, variant_id: int, quantity: int):
    # 1. 检查变体是否存在
    v_res = await db.execute(select(models.ProductVariant).filter(models.ProductVariant.id == variant_id))
    variant = v_res.scalars().first()
    if not variant: return None

    # 2. 查找购物车是否已有该商品
    c_res = await db.execute(select(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.variant_id == variant_id
    ))
    cart_item = c_res.scalars().first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = models.CartItem(user_id=user_id, variant_id=variant_id, quantity=quantity)
        db.add(cart_item)
    
    await db.commit()
    
    # 3. [关键优化] 重新查询并预加载关联数据 (解决 MissingGreenlet)
    # 不仅仅是 refresh，而是重新 select 包含 relationship 的数据
    query = select(models.CartItem)\
        .options(
            selectinload(models.CartItem.variant).selectinload(models.ProductVariant.product)
        )\
        .filter(models.CartItem.id == cart_item.id)
        
    result = await db.execute(query)
    return result.scalars().first()

async def remove_from_cart(db: AsyncSession, user_id: int, item_id: int):
    res = await db.execute(select(models.CartItem).filter(
        models.CartItem.id == item_id, 
        models.CartItem.user_id == user_id
    ))
    item = res.scalars().first()
    if item:
        await db.delete(item)
        await db.commit()
        return True
    return False

async def clear_cart(db: AsyncSession, user_id: int):
    # delete() 语句在 async 下需要 execution
    from sqlalchemy import delete
    await db.execute(delete(models.CartItem).where(models.CartItem.user_id == user_id))
    await db.commit()

# ============================
# 8. 订单 (Order)
# ============================
async def create_order_from_cart(db: AsyncSession, user_id: int, discount_rate: float):
    # 注意：get_cart_items 是 async
    cart_items = await get_cart_items(db, user_id)
    if not cart_items: return None
    
    original_total = 0.0
    order_items_data = []

    for item in cart_items:
        variant = item.variant
        product = variant.product
        
        unit_price = variant.price
        subtotal = unit_price * item.quantity
        original_total += subtotal
        
        order_items_data.append({
            "product_id": product.id,
            "product_name": product.name,
            "product_image": product.image_url,
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
    await db.flush() # 拿 ID

    for item_data in order_items_data:
        db_item = models.OrderItem(order_id=db_order.id, **item_data)
        db.add(db_item)
    
    # 清空购物车
    from sqlalchemy import delete
    await db.execute(delete(models.CartItem).where(models.CartItem.user_id == user_id))
    
    await db.commit()
    
    await db.refresh(db_order)
    return await get_order_by_id(db, db_order.id)

async def get_orders(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    user_id: int = None, 
    driver_id: int = None,
    search: str = None
):
    query = select(models.Order).options(
        joinedload(models.Order.items),
        joinedload(models.Order.user),
        joinedload(models.Order.driver)
    )

    if user_id:
        query = query.filter(models.Order.user_id == user_id)
    if driver_id:
        query = query.filter(models.Order.driver_id == driver_id)

    if search:
        search_fmt = f"%{search}%"
        query = query.join(models.User).filter(
            or_(
                models.User.email.ilike(search_fmt),
                cast(models.Order.id, String).ilike(search_fmt)
            )
        )

    result = await db.execute(query.order_by(models.Order.created_at.desc()).offset(skip).limit(limit))
    return result.unique().scalars().all()

async def get_order_by_id(db: AsyncSession, order_id: int):
    query = select(models.Order)\
        .options(
            joinedload(models.Order.items),   # 加载商品
            joinedload(models.Order.user),    # 加载买家
            joinedload(models.Order.driver)   # 【关键】加载司机 (为了 driver_email)
        )\
        .filter(models.Order.id == order_id)
    result = await db.execute(query)
    return result.unique().scalars().first()

async def update_order_status(db: AsyncSession, order_id: int, status: models.OrderStatus):
    order = await get_order_by_id(db, order_id)
    if order:
        order.status = status
        await db.commit()
        # 重新获取最新状态（包含关联数据）
        return await get_order_by_id(db, order_id) 
    return await get_order_by_id(db, order_id)


async def update_order_price(db: AsyncSession, order_id: int, new_price: float):
    order = await get_order_by_id(db, order_id)
    if order:
        order.final_total_price = new_price
        await db.commit()
        return await get_order_by_id(db, order_id)
    return order

async def update_user_discount(db: AsyncSession, user_id: int, discount_rate: float):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()
    if user:
        user.discount_rate = discount_rate
        await db.commit()
        await db.refresh(user)
    return await get_order_by_id(db, order_id)

async def update_order_item_price(db: AsyncSession, order_id: int, item_id: int, new_unit_price: float):
    # 查找 item 并预加载 order
    res = await db.execute(
        select(models.OrderItem)
        .options(joinedload(models.OrderItem.order).joinedload(models.Order.items))
        .filter(models.OrderItem.id == item_id, models.OrderItem.order_id == order_id)
    )
    item = res.scalars().first()
    if not item: return None

    item.unit_price = new_unit_price
    item.subtotal = round(new_unit_price * item.quantity, 2)
    
    # 重新计算总价
    current_order = item.order
    # 注意：在内存中，current_order.items 里的 item 对象已经是最新的了
    new_final_total = sum([i.subtotal for i in current_order.items])
    current_order.final_total_price = round(new_final_total, 2)

    await db.commit()
    await db.refresh(current_order)
    return current_order

# ============================
# 订单流程 (Confirm / Ship / Complete / Cancel)
# ============================
async def confirm_order(db: AsyncSession, order_id: int):
    order = await get_order_by_id(db, order_id)
    if not order or order.status != models.OrderStatus.PENDING_CONFIRMATION:
        return None, "Invalid order"

    for item in order.items:
        # 查找变体扣库存
        v_res = await db.execute(select(models.ProductVariant).filter(
            models.ProductVariant.product_id == item.product_id,
            models.ProductVariant.spec == item.product_spec,
            models.ProductVariant.color == item.product_color
        ))
        variant = v_res.scalars().first()
        
        if not variant: continue
        if variant.stock < item.quantity:
            return None, f"库存不足: {item.product_name} {item.product_spec}"
        
        variant.stock -= item.quantity
    
    order.status = models.OrderStatus.CONFIRMED
    await db.commit()
    await db.refresh(order)
    return order, None

async def ship_order(db: AsyncSession, order_id: int):
    order = await get_order_by_id(db, order_id)
    if not order: return None, "Not found"
    if order.status != models.OrderStatus.CONFIRMED:
        return None, "Must confirm first"
    
    order.status = models.OrderStatus.DELIVERING
    await db.commit()
    await db.refresh(order)
    return order, None

async def complete_order(db: AsyncSession, order_id: int):
    order = await get_order_by_id(db, order_id)
    if not order: return None, "Not found"
    
    order.status = models.OrderStatus.COMPLETED
    await db.commit()
    await db.refresh(order)
    return order, None

async def cancel_order(db: AsyncSession, order_id: int):
    order = await get_order_by_id(db, order_id)
    if not order: return None, "Not found"
    
    if order.status == models.OrderStatus.COMPLETED:
        return None, "Cannot cancel completed order"
    
    should_rollback_stock = order.status in [models.OrderStatus.CONFIRMED, models.OrderStatus.DELIVERING]

    if should_rollback_stock:
        for item in order.items:
            # 简化回滚：通过名字和规格尝试找回
            # 严格来说应该存 variant_id，这里作为权宜之计
            # ...逻辑略...
            pass
    
    order.status = models.OrderStatus.CANCELLED
    await db.commit()
    await db.refresh(order)
    return order, None

# ============================
# 司机逻辑
# ============================
async def get_drivers(db: AsyncSession):
    res = await db.execute(select(models.User).filter(models.User.role == "driver"))
    return res.scalars().all()

async def assign_driver(db: AsyncSession, order_id: int, driver_id: int):
    # 1. 检查司机
    d_res = await db.execute(select(models.User).filter(models.User.id == driver_id, models.User.role == "driver"))
    driver = d_res.scalars().first()
    if not driver: return None, "Driver not found or invalid role"
    
    # 2. 检查订单
    res = await db.execute(select(models.Order).filter(models.Order.id == order_id))
    order = res.scalars().first()
    if not order: return None, "Order not found"
    
    # 3. 更新状态
    order.driver_id = driver_id
    order.status = models.OrderStatus.DELIVERING
    await db.commit()
    
    # 【核心修复】必须重新查询完整数据再返回！
    # 之前报错是因为这里只写了 db.refresh(order) 或直接 return order
    refreshed_order = await get_order_by_id(db, order_id)
    return refreshed_order, None

async def update_driver_location(db: AsyncSession, order_id: int, lat: float, lng: float):
    # 1. 简单查询订单
    res = await db.execute(select(models.Order).filter(models.Order.id == order_id))
    order = res.scalars().first()
    if not order: return None
    
    # 2. 更新经纬度
    order.driver_lat = lat
    order.driver_lng = lng
    await db.commit()
    
    # 【关键修复】必须调用 get_order_by_id 重新查一遍完整数据！
    # 否则 user_email (依赖 user) 和 items 都会导致 MissingGreenlet 报错
    return await get_order_by_id(db, order_id)

async def get_driver_tasks(db: AsyncSession, driver_id: int):
    query = select(models.Order)\
        .options(joinedload(models.Order.items), joinedload(models.Order.user))\
        .filter(
            models.Order.driver_id == driver_id,
            models.Order.status == models.OrderStatus.DELIVERING
        )
    result = await db.execute(query)
    return result.unique().scalars().all()

# ============================
# 技术参数 (Specs)
# ============================
async def get_technical_specs(db: AsyncSession, skip: int = 0, limit: int = 100, category: str = None, search: str = None):
    query = select(models.TechnicalSpec)
    if category:
        query = query.filter(models.TechnicalSpec.category == category)
    if search:
        query = query.filter(
            or_(models.TechnicalSpec.model.contains(search), models.TechnicalSpec.feature.contains(search))
        )
    result = await db.execute(query.order_by(models.TechnicalSpec.model.asc()).offset(skip).limit(limit))
    return result.scalars().all()

async def create_technical_spec(db: AsyncSession, spec: schemas.TechnicalSpecCreate):
    db_spec = models.TechnicalSpec(**spec.dict())
    db.add(db_spec)
    await db.commit()
    await db.refresh(db_spec)
    return db_spec

async def update_technical_spec(db: AsyncSession, spec_id: int, spec_update: schemas.TechnicalSpecUpdate):
    res = await db.execute(select(models.TechnicalSpec).filter(models.TechnicalSpec.id == spec_id))
    db_spec = res.scalars().first()
    if not db_spec: return None
    
    update_data = spec_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_spec, key, value)
        
    await db.commit()
    await db.refresh(db_spec)
    return db_spec

async def delete_technical_spec(db: AsyncSession, spec_id: int):
    res = await db.execute(select(models.TechnicalSpec).filter(models.TechnicalSpec.id == spec_id))
    db_spec = res.scalars().first()
    if db_spec:
        await db.delete(db_spec)
        await db.commit()
        return True
    return False


# ============================
# 11. 询价系统 (Inquiry Logic)
# ============================

# 获取单条询价单 (包含关联数据)
async def get_inquiry_by_id(db: AsyncSession, inquiry_id: int):
    query = select(models.Inquiry)\
        .options(
            joinedload(models.Inquiry.items),
            joinedload(models.Inquiry.user)
        )\
        .filter(models.Inquiry.id == inquiry_id)
    result = await db.execute(query)
    return result.unique().scalars().first()

# 创建询价单 (从购物车导入，类似 create_order_from_cart)
async def create_inquiry_from_cart(db: AsyncSession, user_id: int, user_remark: str = None):
    # 1. 获取购物车
    cart_items = await get_cart_items(db, user_id)
    if not cart_items: return None

    # 2. 创建询价单主表
    db_inquiry = models.Inquiry(
        user_id=user_id,
        status=models.InquiryStatus.PENDING,
        user_remark=user_remark
    )
    db.add(db_inquiry)
    await db.flush() # 获取 ID

    # 3. 创建明细表
    for item in cart_items:
        variant = item.variant
        product = variant.product
        
        db_item = models.InquiryItem(
            inquiry_id=db_inquiry.id,
            variant_id=variant.id,
            product_name=product.name,
            product_spec=variant.spec,
            product_color=variant.color,
            quantity=item.quantity
        )
        db.add(db_item)
    
    # 4. 清空购物车
    from sqlalchemy import delete
    await db.execute(delete(models.CartItem).where(models.CartItem.user_id == user_id))
    
    await db.commit()
    # 5. 重新加载并返回
    return await get_inquiry_by_id(db, db_inquiry.id)

# 获取询价列表
async def get_inquiries(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100, 
    user_id: int = None,
    status: models.InquiryStatus = None
):
    query = select(models.Inquiry)\
        .options(
            # 【关键修复】必须显式加载 items 关系，否则报错 MissingGreenlet
            selectinload(models.Inquiry.items),
            # user 关系通常是单对单，用 joinedload 或 selectinload 都可以
            selectinload(models.Inquiry.user)
        )\
        .order_by(models.Inquiry.created_at.desc())

    if user_id:
        query = query.filter(models.Inquiry.user_id == user_id)
    if status:
        query = query.filter(models.Inquiry.status == status)

    result = await db.execute(query.offset(skip).limit(limit))
    return result.unique().scalars().all()

# 管理员报价
async def quote_inquiry(db: AsyncSession, inquiry_id: int, quote_data: schemas.InquiryQuoteUpdate):
    inquiry = await get_inquiry_by_id(db, inquiry_id)
    if not inquiry: return None
    
    inquiry.quoted_total_price = quote_data.quoted_total_price
    inquiry.admin_reply = quote_data.admin_reply
    inquiry.status = models.InquiryStatus.QUOTED
    
    await db.commit()
    return await get_inquiry_by_id(db, inquiry_id)