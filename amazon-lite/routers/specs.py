# backend/routers/specs.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import crud, models, schemas
from database import get_db
from deps import get_current_active_superuser # 假设你有这个依赖文件，如果没有，直接从main.py引入类似的逻辑

router = APIRouter(
    prefix="/specs",
    tags=["technical-specs"]
)

# 1. 获取列表 (公开)
@router.get("/", response_model=List[schemas.TechnicalSpecResponse])
def read_specs(
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_technical_specs(db, skip=skip, limit=limit, category=category, search=search)

# 2. 创建 (管理员)
@router.post("/", response_model=schemas.TechnicalSpecResponse, status_code=201)
def create_spec(
    spec: schemas.TechnicalSpecCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    return crud.create_technical_spec(db, spec)

# 3. 更新 (管理员)
@router.put("/{spec_id}", response_model=schemas.TechnicalSpecResponse)
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
@router.delete("/{spec_id}", status_code=204)
def delete_spec(
    spec_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_active_superuser)
):
    if not crud.delete_technical_spec(db, spec_id):
        raise HTTPException(status_code=404, detail="Spec not found")