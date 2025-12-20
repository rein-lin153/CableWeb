from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
import schemas, models
from database import get_db
from dependencies import get_current_active_superuser

# 🟢 修正：去掉内部的 prefix="/api/v1"，保持纯净
router = APIRouter()

# ==========================================
# 🟢 必须放在最前面：静态路径路由
# ==========================================

@router.get("/categories/tree", response_model=List[schemas.CategoryTree])
async def get_category_tree(db: AsyncSession = Depends(get_db)):
    """获取无限级分类树"""
    # 1. 查出所有分类
    res = await db.execute(select(models.Category))
    all_cats = res.scalars().all()
    
    # 2. 内存组装树
    cat_map = {c.id: schemas.CategoryTree.from_orm(c) for c in all_cats}
    roots = []
    
    for cat in all_cats:
        node = cat_map[cat.id]
        if cat.parent_id is None:
            roots.append(node)
        else:
            parent = cat_map.get(cat.parent_id)
            if parent:
                parent.children.append(node)
                
    return roots

@router.post("/categories/", response_model=schemas.CategoryResponse)
async def create_category(
    cat: schemas.CategoryCreate, 
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_active_superuser) # 需要管理员权限
):
    db_cat = models.Category(name=cat.name, parent_id=cat.parent_id)
    db.add(db_cat)
    await db.commit()
    await db.refresh(db_cat)
    return db_cat

@router.delete("/categories/{id}")
async def delete_category(
    id: int, 
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_active_superuser)
):
    result = await db.execute(select(models.Category).filter(models.Category.id == id))
    cat = result.scalars().first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(cat)
    await db.commit()
    return {"ok": True}

@router.post("/convert-from-cost", response_model=schemas.ProductResponse)
async def convert_cost_to_product(
    payload: schemas.ConvertCostToProduct, 
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_active_superuser)
):
    # 1. 获取源成本数据
    cost_res = await db.execute(select(models.ProductCost).filter(models.ProductCost.id == payload.cost_id))
    cost_item = cost_res.scalars().first()
    if not cost_item:
        raise HTTPException(status_code=404, detail="成本记录不存在")

    # 2. 创建主产品
    new_product = models.Product(
        name=payload.name,
        description=payload.description or f"Based on {cost_item.spec_name}",
        price=payload.price,
        category_id=payload.target_category_id,
        image_url=payload.image_url,
        cost_id=cost_item.id,
        is_active=True
    )
    db.add(new_product)
    await db.flush()

    # 3. 创建默认变体 (关键：带入铜重)
    new_variant = models.ProductVariant(
        product_id=new_product.id,
        spec=cost_item.spec_name,
        color="默认",
        price=payload.price,
        stock=9999,
        sku_code=f"AUTO-{cost_item.id}",
        copper_weight=cost_item.copper_weight,
        process_cost=(cost_item.labor_cost + cost_item.pvc_amount)
    )
    db.add(new_variant)
    
    await db.commit()
    await db.refresh(new_product)
    return new_product

# ==========================================
# 🟢 通用产品路由 (放在特定路由之后)
# ==========================================

@router.get("/", response_model=List[schemas.ProductResponse])
async def read_products(
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(models.Product).options(selectinload(models.Product.variants))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if search:
        query = query.filter(models.Product.name.contains(search))
        
    res = await db.execute(query.offset(skip).limit(limit))
    return res.scalars().all()

@router.get("/{id}", response_model=schemas.ProductResponse)
async def read_product(id: int, db: AsyncSession = Depends(get_db)):
    query = select(models.Product).options(selectinload(models.Product.variants)).filter(models.Product.id == id)
    res = await db.execute(query)
    product = res.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=schemas.ProductResponse)
async def create_product(
    product: schemas.ProductCreate, 
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_active_superuser)
):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

@router.put("/{id}", response_model=schemas.ProductResponse)
async def update_product(
    id: int, 
    product_update: schemas.ProductUpdate, 
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_active_superuser)
):
    res = await db.execute(select(models.Product).filter(models.Product.id == id))
    db_prod = res.scalars().first()
    if not db_prod:
        raise HTTPException(status_code=404, detail="Product not found")
        
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_prod, key, value)
        
    await db.commit()
    await db.refresh(db_prod)
    return db_prod

@router.delete("/{id}")
async def delete_product(
    id: int, 
    db: AsyncSession = Depends(get_db),
    _ = Depends(get_current_active_superuser)
):
    res = await db.execute(select(models.Product).filter(models.Product.id == id))
    db_prod = res.scalars().first()
    if not db_prod:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(db_prod)
    await db.commit()
    return {"ok": True}