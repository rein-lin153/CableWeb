import os, shutil
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from dependencies import get_db, get_current_user, get_current_active_superuser, validate_image_security
import crud, schemas, models

router = APIRouter(prefix="/api/v1", tags=["Orders"])
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

# --- Cart ---
@router.get("/cart/", response_model=List[schemas.CartItemResponse], tags=["Cart"])
async def read_cart(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    items = await crud.get_cart_items(db, current_user.id)
    res = []
    for item in items:
        if not item.variant or not item.variant.product: continue
        res.append({
            "id": item.id, "variant_id": item.variant_id, "quantity": item.quantity,
            "product_name": item.variant.product.name, "spec": item.variant.spec,
            "price": item.variant.price, "subtotal": item.variant.price * item.quantity,
            "image_url": item.variant.product.image_url
        })
    return res

@router.post("/cart/", response_model=schemas.CartItemResponse, tags=["Cart"])
async def add_to_cart(cart_data: schemas.CartItemCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    item = await crud.add_to_cart(db, current_user.id, cart_data.variant_id, cart_data.quantity)
    if not item: raise HTTPException(status_code=404, detail="Variant not found")
    query = select(models.CartItem).options(selectinload(models.CartItem.variant).selectinload(models.ProductVariant.product)).filter(models.CartItem.id == item.id)
    full_item = (await db.execute(query)).scalars().first()
    return {"id": full_item.id, "variant_id": full_item.variant_id, "quantity": full_item.quantity, "product_name": full_item.variant.product.name, "price": full_item.variant.price, "subtotal": full_item.variant.price * full_item.quantity}

# --- Orders ---
@router.post("/orders/", response_model=schemas.OrderResponse)
async def create_order(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    order = await crud.create_order_from_cart(db, current_user.id, current_user.discount_rate)
    if not order: raise HTTPException(status_code=400, detail="Cart is empty")
    return order

@router.get("/orders/", response_model=List[schemas.OrderResponse])
async def read_orders(
    skip: int = 0, 
    limit: int = 100, 
    q: Optional[str] = None,
    db: AsyncSession = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """管理员查看所有订单，司机查看分配的任务，用户查看自己的订单"""
    user_id, driver_id = None, None
    
    # 权限逻辑
    if current_user.role == "driver": 
        driver_id = current_user.id
    elif not (current_user.is_admin or current_user.role == "admin"): 
        user_id = current_user.id
        
    return await crud.get_orders(db, skip=skip, limit=limit, user_id=user_id, driver_id=driver_id, search=q)

@router.get("/orders/my", response_model=List[schemas.OrderResponse])
async def read_my_orders(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """快捷入口：查看我自己的订单"""
    return await crud.get_orders(db, user_id=current_user.id)

@router.get("/orders/{order_id}", response_model=schemas.OrderResponse)
async def read_order_detail(order_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    """查看订单详情（含权限检查）"""
    order = await crud.get_order_by_id(db, order_id)
    if not order: 
        raise HTTPException(status_code=404, detail="Order not found")
    
    is_admin = current_user.is_admin or current_user.role == "admin"
    is_owner = order.user_id == current_user.id
    is_assigned_driver = order.driver_id == current_user.id
    
    if not (is_admin or is_owner or is_assigned_driver):
        raise HTTPException(status_code=403, detail="Permission denied")
    return order

@router.post("/orders/{order_id}/complete", response_model=schemas.OrderResponse)
async def complete_order(order_id: int, file: UploadFile = File(None), db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    order = await crud.get_order_by_id(db, order_id)
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != "admin" and order.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    if file:
        await validate_image_security(file)
        file_name = f"order_{order_id}_sign_{int(datetime.now().timestamp())}.{file.filename.split('.')[-1]}"
        file_path = os.path.join(STATIC_DIR, "uploads", file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
        order.delivery_photo_url = f"/static/uploads/{file_name}"
    
    order.status = models.OrderStatus.COMPLETED
    await db.commit()
    return await crud.get_order_by_id(db, order_id)

@router.patch("/orders/{order_id}/assign", response_model=schemas.OrderResponse)
async def assign_order_driver(order_id: int, assign_req: schemas.AssignDriverRequest, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    order, error = await crud.assign_driver(db, order_id, assign_req.driver_id)
    if error: raise HTTPException(status_code=400, detail=error)
    return order
