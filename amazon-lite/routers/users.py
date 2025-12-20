from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dependencies import get_db, get_current_user, get_current_active_superuser
import crud, schemas, models

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=List[schemas.UserResponse])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    return await crud.get_users(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.UserResponse, status_code=201)
async def create_user_by_admin(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    user = await crud.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    return await crud.create_user(db, user_in)

@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user_detail(user_id: int, user_in: schemas.UserUpdate, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_active_superuser)):
    if user_id == current_admin.id and user_in.role and user_in.role != "admin":
        raise HTTPException(status_code=400, detail="Cannot change your own role to non-admin")
    user = await crud.update_user(db, user_id, user_in)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}/role", response_model=schemas.UserResponse)
async def update_user_role(user_id: int, role_update: schemas.UserRoleUpdate, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_active_superuser)):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user_to_edit = result.scalars().first()
    if not user_to_edit: raise HTTPException(status_code=404, detail="User not found")
    if user_id == current_admin.id and role_update.is_superuser is False:
        raise HTTPException(status_code=400, detail="Operation not allowed")
    user_to_edit.is_admin = role_update.is_superuser
    await db.commit()
    await db.refresh(user_to_edit)
    return user_to_edit

@router.patch("/{user_id}/status", response_model=schemas.UserResponse)
async def update_user_status(user_id: int, status_data: schemas.UserStatusUpdate, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_active_superuser)):
    if user_id == current_admin.id and status_data.is_active is False:
        raise HTTPException(status_code=400, detail="Cannot ban yourself")
    user = await crud.update_user(db, user_id, schemas.UserUpdate(is_active=status_data.is_active))
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), current_admin=Depends(get_current_active_superuser)):
    if user_id == current_admin.id: raise HTTPException(status_code=400, detail="Cannot delete yourself")
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()

@router.patch("/{user_id}/discount", response_model=schemas.UserResponse)
async def update_user_discount(user_id: int, discount_data: schemas.UserDiscountUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    user = await crud.update_user_discount(db, user_id, discount_data.discount_rate)
    if not user: raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/drivers", response_model=List[schemas.UserResponse])
async def get_drivers(db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    return await crud.get_drivers(db)
