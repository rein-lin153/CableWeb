from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models, schemas
from dependencies import get_db, get_current_active_superuser

router = APIRouter()

# 1. 获取列表 (公开)
@router.get("/", response_model=List[schemas.TechnicalSpecResponse])
async def read_specs(
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None, 
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(models.TechnicalSpec)
    
    if category:
        query = query.filter(models.TechnicalSpec.category == category)
    if search:
        # 假设搜索的是 spec 的 name 字段
        query = query.filter(models.TechnicalSpec.name.contains(search))
        
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

# 2. 创建 (管理员)
@router.post("/", response_model=schemas.TechnicalSpecResponse, status_code=201)
async def create_spec(
    spec: schemas.TechnicalSpecCreate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    db_spec = models.TechnicalSpec(**spec.dict())
    db.add(db_spec)
    await db.commit()
    await db.refresh(db_spec)
    return db_spec

# 3. 更新 (管理员)
@router.put("/{spec_id}", response_model=schemas.TechnicalSpecResponse)
async def update_spec(
    spec_id: int,
    spec_update: schemas.TechnicalSpecUpdate,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    # 先查询是否存在
    result = await db.execute(select(models.TechnicalSpec).filter(models.TechnicalSpec.id == spec_id))
    db_spec = result.scalars().first()
    
    if not db_spec:
        raise HTTPException(status_code=404, detail="Spec not found")
    
    # 更新字段
    update_data = spec_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_spec, key, value)
        
    await db.commit()
    await db.refresh(db_spec)
    return db_spec

# 4. 删除 (管理员)
@router.delete("/{spec_id}", status_code=204)
async def delete_spec(
    spec_id: int,
    db: AsyncSession = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    result = await db.execute(select(models.TechnicalSpec).filter(models.TechnicalSpec.id == spec_id))
    db_spec = result.scalars().first()
    
    if not db_spec:
        raise HTTPException(status_code=404, detail="Spec not found")
        
    await db.delete(db_spec)
    await db.commit()